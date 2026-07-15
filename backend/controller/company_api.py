from flask_restful import Resource
from flask import request,jsonify,make_response,current_app,send_from_directory
from flask_security import auth_token_required,roles_required ,current_user
from controller.models import Company,db,Placement_Drive,Application,Program,Eligibility,Interview,Offer
from werkzeug.utils import secure_filename

from datetime import datetime,date
import os

from celery_app import export_company_history

class ExportCompany(Resource):

    @auth_token_required
    @roles_required("company")
    def post(self):

        company = current_user.company

        task = export_company_history.delay(
            company.id)

        return make_response(
            jsonify({
                "message": "Export started successfully.",
                "task_id": task.id
            }),
            202
        )

class CompanyDashboard(Resource):

    @auth_token_required
    @roles_required('company')
    def get(self):

        company = current_user.company

        if not company:
            return make_response(
                jsonify({"message": "Company not found"}),
                404
            )

        drives = company.placement_drives

        total_drives = len(drives)

        approved_drives = sum(
            1 for d in drives
            if d.status == "Approved"
        )

        pending_drives = sum(
            1 for d in drives
            if d.status == "Pending"
        )

        closed_drives = sum(
            1 for d in drives
            if d.status == "Closed"
        )

        applications = []

        for drive in drives:
            applications.extend(drive.applications)

        total_applications = len(applications)

        shortlisted = sum(
            1 for a in applications
            if a.status == "Shortlisted"
        )

        selected = sum(
            1 for a in applications
            if a.status == "Selected"
        )

        recent_drives = sorted(
            drives,
            key=lambda d: d.application_deadline,
            reverse=True
        )[:5]

        recent = []

        for drive in recent_drives:

            recent.append({
                "id": drive.id,
                "job_title": drive.job_title,
                "deadline": drive.application_deadline.strftime("%Y-%m-%d"),
                "status": drive.status,
                "applications": len(drive.applications)
            })

        result = {
            "company": {
                "id": company.id,
                "name": company.name
            },

            "statistics": {
                "total_drives": total_drives,
                "approved_drives": approved_drives,
                "pending_drives": pending_drives,
                "closed_drives": closed_drives,
                "total_applications": total_applications,
                "shortlisted": shortlisted,
                "selected": selected
            },

            "recent_drives": recent
        }

        return make_response(jsonify(result), 200)
    
class CompanyDrives(Resource):

    @auth_token_required
    @roles_required("company")
    def get(self):

        company = current_user.company

        if not company:
            return make_response(
                jsonify({"message": "Company not found"}),
                404
            )

        query = Placement_Drive.query.filter_by(
            company_id=company.id
        )

        job_title = request.args.get("job_title")
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if job_title:
            query = query.filter(
                Placement_Drive.job_title.ilike(f"%{job_title}%")
            )

        if status:
            query = query.filter(
                Placement_Drive.status == status
            )

        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(
                    Placement_Drive.application_deadline >= start
                )
            except ValueError:
                return make_response(
                    jsonify({"message": "Invalid start date"}),
                    400
                )

        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                query = query.filter(
                    Placement_Drive.application_deadline <= end
                )
            except ValueError:
                return make_response(
                    jsonify({"message": "Invalid end date"}),
                    400
                )

        drives = query.order_by(
            Placement_Drive.application_deadline.desc()
        ).all()

        result = []

        for drive in drives:

            result.append({

                "id": drive.id,

                "job_title": drive.job_title,

                "deadline": drive.application_deadline.strftime(
                    "%Y-%m-%d"
                ),

                "status": drive.status,

                "applications": len(drive.applications)

            })

        return make_response(
            jsonify(result),
            200
        )
    
    @auth_token_required
    @roles_required("company")
    def post(self):

        data = request.get_json()

        if not data:
            return make_response(
                jsonify({
                    "message": "Request body is required."
                }),
                400
            )

        job_title = data.get("job_title")
        job_description = data.get("job_description")
        application_deadline = data.get("application_deadline")
        eligibility = data.get("eligibility")

        if not all([
            job_title,
            job_description,
            application_deadline,
            eligibility
        ]):
            return make_response(
                jsonify({
                    "message": "All fields are required."
                }),
                400
            )

        if len(job_title) > 100:
            return make_response(
                jsonify({
                    "message": "Job title cannot exceed 100 characters."
                }),
                400
            )

        if len(job_description.strip()) < 20:
            return make_response(
                jsonify({
                    "message": "Job description is too short."
                }),
                400
            )

        try:

            deadline = datetime.fromisoformat(
                application_deadline
            )

        except ValueError:

            return make_response(
                jsonify({
                    "message": "Invalid application deadline."
                }),
                400
            )

        if deadline <= datetime.now():

            return make_response(
                jsonify({
                    "message": "Deadline must be in the future."
                }),
                400
            )

        company = current_user.company

        drive = Placement_Drive(

            company_id=company.id,

            job_title=job_title.strip(),

            job_description=job_description.strip(),

            application_deadline=deadline

        )

        db.session.add(drive)

        db.session.flush()

        for item in eligibility:

            program_code = item.get("program_code")
            min_cgpa = item.get("min_cgpa")
            eligible_year = item.get("eligible_year")

            if not all([
                program_code,
                min_cgpa is not None,
                eligible_year
            ]):

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        "Incomplete eligibility criteria."
                    }),
                    400
                )

            program = Program.query.filter_by(
                code=program_code
            ).first()

            if not program:

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        f"Program '{program_code}' does not exist."
                    }),
                    400
                )

            try:

                min_cgpa = float(min_cgpa)

            except ValueError:

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        "Minimum CGPA must be numeric."
                    }),
                    400
                )

            if not (0 <= min_cgpa <= 10):

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        "Minimum CGPA must be between 0 and 10."
                    }),
                    400
                )

            try:

                eligible_year = int(eligible_year)

            except ValueError:

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        "Eligible year must be an integer."
                    }),
                    400
                )

            if eligible_year <= 0:

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        "Eligible year must be greater than zero."
                    }),
                    400
                )

            if eligible_year > program.duration:

                db.session.rollback()

                return make_response(
                    jsonify({
                        "message":
                        f"{program.code} is only {program.duration} years long."
                    }),
                    400
                )

            db.session.add(

                Eligibility(

                    drive_id=drive.id,

                    program_code=program_code,

                    min_cgpa=min_cgpa,

                    eligibile_year=eligible_year

                )

            )

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            return make_response(

                jsonify({

                    "message":
                    "Unable to create placement drive.",

                    "error":
                    str(e)

                }),

                500

            )

        return make_response(

            jsonify({

                "message":
                "Placement drive created successfully."

            }),

            201

        )

class CloseDrive(Resource):

    @auth_token_required
    @roles_required("company")
    def put(self, id):

        company = current_user.company

        drive = Placement_Drive.query.filter_by(
            id=id,
            company_id=company.id
        ).first()

        if not drive:
            return make_response(
                jsonify({"message": "Placement drive not found"}),
                404
            )
        if drive.status != "Approved":
            return make_response(
                jsonify({
                    "message": "Only approved drives can be closed."
                }),
                400
            )

        if drive.status == "Closed":
            return make_response(
                jsonify({"message": "Drive already closed"}),
                400
            )

        drive.status = "Closed"

        for application in drive.applications:
            if application.status in ("Applied", "Shortlisted"):
                application.status = "Rejected"
                if (
            application.interview and
            application.interview.status == "Scheduled"
        ):
                    application.interview.status="Cancelled"

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            return make_response(
                jsonify({
                    "message": "Unable to close drive",
                    "error": str(e)
                }),
                500
            )

        return make_response(
            jsonify({
                "message": "Drive closed successfully"
            }),
            200
        )

class CompanyInterview(Resource):

    @auth_token_required
    @roles_required('company')
    def post(self, application_id):

        data = request.get_json()

        if not data:
            return make_response(
                jsonify({"message": "Request body required"}),
                400
            )

        interview_datetime = data.get("interview_datetime")
        interview_details = data.get("interview_details", "").strip()

        if not interview_datetime or not interview_details:
            return make_response(
                jsonify({"message": "All fields are required"}),
                400
            )

        application = (
            Application.query
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Application.id == application_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not application:
            return make_response(
                jsonify({"message": "Application not found"}),
                404
            )

        if application.status != "Shortlisted":
            return make_response(
                jsonify({
                    "message":
                    "Interview can only be scheduled for shortlisted students."
                }),
                400
            )

        try:
            interview_datetime = datetime.strptime(
                interview_datetime,
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            return make_response(
                jsonify({"message": "Invalid date/time"}),
                400
            )
        if interview_datetime <= datetime.now():
            return make_response(
                jsonify({
                    "message": "Interview must be scheduled for a future date and time."
                }),
                400
            )

        interview = application.interview

        if interview:

            interview.interview_datetime = interview_datetime
            interview.interview_details = interview_details
            interview.status = "Scheduled"

            message = "Interview rescheduled successfully."

        else:

            interview = Interview(
                application=application,
                company_id=application.placement_drive.company.id,
                interview_datetime=interview_datetime,
                interview_details=interview_details
            )

            db.session.add(interview)

            message = "Interview scheduled successfully."

        db.session.commit()

        # TODO
        # celery.send_interview_email.delay(interview.id)

        return make_response(
            jsonify({"message": message}),
            200
        )

class CancelInterview(Resource):

    @auth_token_required
    @roles_required('company')
    def put(self, interview_id):

        interview = (
            Interview.query
            .join(Interview.application)
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Interview.id == interview_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not interview:
            return make_response(
                jsonify({"message": "Interview not found"}),
                404
            )

        if interview.status == "Cancelled":
            return make_response(
                jsonify({
                    "message": "Interview is already cancelled."
                }),
                400
            )

        if interview.status == "Completed":
            return make_response(
                jsonify({
                    "message": "Completed interviews cannot be cancelled."
                }),
                400
            )

        interview.status = "Cancelled"

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(
                jsonify({
                    "message": "Unable to cancel interview.",
                    "error": str(e)
                }),
                500
            )

        return make_response(
            jsonify({
                "message": "Interview cancelled successfully."
            }),
            200
        )  
    
class CompleteInterview(Resource):

    @auth_token_required
    @roles_required('company')
    def put(self, interview_id):

        interview = (
            Interview.query
            .join(Interview.application)
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Interview.id == interview_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not interview:
            return make_response(
                jsonify({"message": "Interview not found"}),
                404
            )
        if interview.status == "Completed":
            return make_response(
                jsonify({
                    "message": "Interview is already completed."
                }),
                400
            )

        if interview.status == "Cancelled":
            return make_response(
                jsonify({
                    "message": "Cancelled interviews cannot be marked as completed."
                }),
                400
            )

        interview.status = "Completed"

        try:
            db.session.commit()

        except Exception as e:

            db.session.rollback()

            return make_response(
                jsonify({
                    "message": "Unable to mark interview as complete.",
                    "error": str(e)
                }),
                500
            )

        return make_response(
            jsonify({
                "message": "Interview marked as completed."
            }),
            200
        )

class CompanyViewResume(Resource):

    @auth_token_required
    @roles_required('company')
    def get(self, application_id):

        application = (
            Application.query
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Application.id == application_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not application:
            return make_response(
                jsonify({"message": "Application not found"}),
                404
            )

        resume = application.resume


        if not resume:
            return make_response(
                jsonify({"message": "Resume not found"}),
                404
            )

        filename = os.path.basename(resume.file_path)

        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            "resumes",
            filename
        )

        if not os.path.isfile(filepath):
            return make_response(
                jsonify({"message": "Resume file not found."}),
                404
            )

        return send_from_directory(
            os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes"),
            filename,
            as_attachment=False
        )

def serialize_application(application):

    data = {

        "application_id": application.id,

        "student_id": application.student.roll_no,

        "roll_no": application.student.roll_no,

        "student_name": application.student.name,

        "cgpa": application.student.cgpa,

        "program_code": application.student.program.code,

        "program_name": application.student.program.name,

        "year": application.student.year_in_program,

        "application_date": application.application_date.isoformat()

    }

    if application.interview:

        data["interview"] = {

            "id": application.interview.id,

            "status": application.interview.status,

            "datetime": application.interview.interview_datetime.isoformat(),

            "details": application.interview.interview_details

        }

    else:

        data["interview"] = None

    if application.offer:

        data["offer"] = {

            "id": application.offer.id,

            "status": application.offer.status

        }

    else:

        data["offer"] = None

    return data

class CompanyDriveDetails(Resource):

    @auth_token_required
    @roles_required('company')
    def get(self, drive_id):

        drive = (
            Placement_Drive.query
            .join(Placement_Drive.company)
            .filter(
                Placement_Drive.id == drive_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not drive:
            return make_response(
                jsonify({"message": "Drive not found"}),
                404
            )

        summary = {
            "Applied": 0,
            "Shortlisted": 0,
            "Selected": 0,
            "Rejected": 0,
            "Upcoming Interviews": 0
        }

        for application in drive.applications:

            status = application.status

            if status in summary:
                summary[status] += 1

            if (
                application.interview and
                application.interview.status == "Scheduled"
            ):
                summary["Upcoming Interviews"] += 1

        eligibility = []

        for e in drive.eligibility:

            eligibility.append({

                "eligibility_id": e.eligibility_id,

                "program_code": e.program.code,

                "program_name": e.program.name,

                "min_cgpa": e.min_cgpa,

                "eligible_year": e.eligible_year

            })

        interviews = []

        for application in drive.applications:

            if application.interview:

                interview = application.interview

                interviews.append({

                    "id": interview.id,

                    "application_id": application.id,

                    "student_name": application.student.name,

                    "roll_no": application.student.roll_no,

                    "interview_datetime": interview.interview_datetime.isoformat(),

                    "interview_details": interview.interview_details,

                    "status": interview.status

                })

        return make_response(
            jsonify({

                "id": drive.id,

                "job_title": drive.job_title,

                "job_description": drive.job_description,

                "application_deadline": drive.application_deadline.isoformat(),

                "status": drive.status,

                "summary": summary,

                "eligibility": eligibility,

                "interviews": interviews

            }),
            200
        )

class CompanyDriveApplications(Resource):

    @auth_token_required
    @roles_required('company')
    def get(self, drive_id):

        drive = (
            Placement_Drive.query
            .join(Placement_Drive.company)
            .filter(
                Placement_Drive.id == drive_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not drive:
            return make_response(
                jsonify({"message": "Drive not found"}),
                404
            )

        result = {

            "Applied": [],

            "Shortlisted": [],

            "Selected": [],

            "Rejected": [],

        }

        for application in drive.applications:
            if application.status not in result:
                continue

            result[application.status].append(

                serialize_application(application)

            )

        return make_response(
            jsonify(result),
            200
        )

class UpdateApplicationStatus(Resource):

    @auth_token_required
    @roles_required("company")
    def put(self, application_id):

        data = request.get_json()

        if not data:
            return make_response(
                jsonify({
                    "message": "Request body is required."
                }),
                400
            )

        status = data.get("status")

        if not status:
            return make_response(
                jsonify({
                    "message": "Status is required."
                }),
                400
            )

        application = (
            Application.query
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Application.id == application_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not application:
            return make_response(
                jsonify({
                    "message": "Application not found."
                }),
                404
            )

        if application.placement_drive.status != "Approved":
            return make_response(
                jsonify({
                    "message": "Cannot update applications for this drive."
                }),
                400
            )

        current_status = application.status

        allowed_transitions = {
            "Applied": [
                "Shortlisted",
                "Rejected"
            ],
            "Shortlisted": [
                "Selected",
                "Rejected"
            ],
            "Selected": [],
            "Rejected": [],
            "Cancelled": []
        }

        if status not in allowed_transitions.get(current_status, []):
            return make_response(
                jsonify({
                    "message": f"Cannot change application status from '{current_status}' to '{status}'."
                }),
                400
            )

        if status == "Selected":

            if not application.interview:
                return make_response(
                    jsonify({
                        "message": "Interview must be scheduled before selecting the student."
                    }),
                    400
                )

            if application.interview.status != "Completed":
                return make_response(
                    jsonify({
                        "message": "Interview must be completed before selecting the student."
                    }),
                    400
                )

        application.status = status

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            return make_response(
                jsonify({
                    "message": "Unable to update application.",
                    "error": str(e)
                }),
                500
            )

        return make_response(
            jsonify({
                "message": "Application status updated successfully."
            }),
            200
        )

class CompanyOffer(Resource):

    @auth_token_required
    @roles_required("company")
    def post(self, application_id):

        application = (
            Application.query
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Application.id == application_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not application:
            return make_response(
                jsonify({
                    "message": "Application not found."
                }),
                404
            )

        if application.status != "Selected":
            return make_response(
                jsonify({
                    "message":
                    "Offer can only be issued to selected students."
                }),
                400
            )

        if application.offer:
            return make_response(
                jsonify({
                    "message":
                    "Offer has already been issued."
                }),
                400
            )

        package = request.form.get("package")
        job_role = request.form.get("job_role", "").strip()
        joining_date = request.form.get("joining_date")
        offer_letter = request.files.get("offer_letter")

        if not all([
            package,
            job_role,
            joining_date,
            offer_letter
        ]):
            return make_response(
                jsonify({
                    "message": "All fields are required."
                }),
                400
            )

        try:
            package = float(package)

            if package <= 0:
                raise ValueError

        except ValueError:

            return make_response(
                jsonify({
                    "message":
                    "Package must be a positive number."
                }),
                400
            )

        try:

            joining_date = datetime.strptime(
                joining_date,
                "%Y-%m-%d"
            )

        except ValueError:

            return make_response(
                jsonify({
                    "message":
                    "Invalid joining date."
                }),
                400
            )
        if joining_date <= date.today():

            return make_response(
                jsonify({
                    "message": "Joining date must be in the future."
                }),
                400
            )

        filename = secure_filename(
            offer_letter.filename
        )

        if (
            not filename or
            not filename.lower().endswith(".pdf")
        ):
            return make_response(
                jsonify({
                    "message":
                    "Offer letter must be a PDF."
                }),
                400
            )

        upload_folder = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            "offers"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        offer = Offer(
            application=application,
            package=package,
            job_role=job_role.strip(),
            joining_date=joining_date,
            offer_letter_path=""
        )

        db.session.add(offer)
        db.session.flush()

        filepath = os.path.join(
            upload_folder,
            f"offer_{offer.id}.pdf"
        )


        try:
            offer_letter.save(filepath)

            offer.offer_letter_path = f"offer_{offer.id}.pdf"

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            if os.path.exists(filepath):
                os.remove(filepath)

            return make_response(
                jsonify({
                    "message":
                    "Unable to create offer.",
                    "error":
                    str(e)
                }),
                500
            )

        # TODO
        # celery.send_offer_email.delay(offer.id)

        return make_response(
            jsonify({
    "message": "Offer issued successfully.",
    "offer_id": offer.id
}),
            201
        )

class CompanyOfferDetails(Resource):

    @auth_token_required
    @roles_required("company")
    def get(self, offer_id):

        offer = (
            Offer.query
            .join(Offer.application)
            .join(Application.placement_drive)
            .join(Placement_Drive.company)
            .filter(
                Offer.id == offer_id,
                Company.user_id == current_user.id
            )
            .first()
        )

        if not offer:
            return make_response(
                jsonify({
                    "message": "Offer not found."
                }),
                404
            )

        application = offer.application

        return make_response(
            jsonify({

                "id": offer.id,

                "student_name":
                    application.student.name,

                "roll_no":
                    application.student.roll_no,

                "program":
                    application.student.program.name,

                "package":
                    offer.package,

                "job_role":
                    offer.job_role,

                "joining_date":
                    offer.joining_date.strftime(
                        "%Y-%m-%d"
                    ),

                "status":
                    offer.status

            }),
            200
        )



