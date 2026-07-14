from flask_restful import Resource
from flask import jsonify, make_response, request
from flask_security import auth_token_required, current_user,hash_password,roles_required

from models import (
    db,
    Student,
    Application,
    Interview,
    Offer,User,Company,Eligibility,Placement_Drive
)
from datetime import datetime


class StudentDashboard(Resource):

    @auth_token_required
    @roles_required('student')
    def get(self):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        if not student:
            return make_response(
                jsonify({
                    "message": "Student not found."
                }),
                404
            )

        total_applications = len(student.applications)

        total_interviews = (
            Interview.query
            .join(Application)
            .filter(Application.student_id == student.roll_no)
            .count()
        )

        total_offers = (
            Offer.query
            .join(Application)
            .filter(Application.student_id == student.roll_no)
            .count()
        )

        applications = []

        for application in (
            Application.query
            .join(Application.placement_drive)
            .join(Application.placement_drive, aliased=False)
            .filter(Application.student_id == student.roll_no)
            .order_by(Application.application_date.desc())
            .all()
        ):

            applications.append({
                "id": application.id,
                "company": application.placement_drive.company.name,
                "job_title": application.placement_drive.job_title,
                "application_date": application.application_date.strftime("%d %b %Y"),
                "status": application.status
            })

        interview_order = {
            "Scheduled": 0,
            "Completed": 1,
            "Cancelled": 2
        }

        interviews = []

        interview_list = (
            Interview.query
            .join(Application)
            .join(Application.placement_drive)
            .filter(Application.student_id == student.roll_no)
            .all()
        )

        interview_list.sort(
            key=lambda x: (
                interview_order[x.status],
                x.interview_datetime
            )
        )

        for interview in interview_list:

            interviews.append({
                "id": interview.id,
                "application_id": interview.application_id,
                "company": interview.application.placement_drive.company.name,
                "job_title": interview.application.placement_drive.job_title,
                "datetime": interview.interview_datetime.strftime("%d %b %Y %I:%M %p"),
                "status": interview.status
            })

        return make_response(
            jsonify({

                "student": {
                    "name": student.name,
                    "placed": student.placed
                },

                "statistics": {
                    "total_applications": total_applications,
                    "total_interviews": total_interviews,
                    "total_offers": total_offers,
                    "placed": student.placed
                },

                "applications": applications,
                "interviews": interviews

            }),
            200
        )
    

    from flask import request, jsonify, make_response


class StudentProfile(Resource):

    @auth_token_required
    @roles_required('student')
    def get(self):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        if not student:
            return make_response(
                jsonify({
                    "message": "Student not found."
                }),
                404
            )

        return make_response(
            jsonify({
                "name": student.name,
                "email": student.user.email,
                "phone_no": student.phone_no,
                "program": student.program.name,
                "cgpa": student.cgpa,
                "year_in_program": student.year_in_program
            }),
            200
        )

    @auth_token_required
    @roles_required('student')
    def put(self):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        if not student:
            return make_response(
                jsonify({
                    "message": "Student not found."
                }),
                404
            )

        data = request.get_json()

        if not data:
            return make_response(
                jsonify({
                    "message": "No data received."
                }),
                400
            )

        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        phone_no = data.get("phone_no", "").strip()
        cgpa = data.get("cgpa")
        year_in_program = data.get("year_in_program")
        password = data.get("password", "").strip()

        if not all([name, email, phone_no]):
            return make_response(
                jsonify({
                    "message": "Name, email and phone number are required."
                }),
                400
            )

        if cgpa is None or cgpa < 0 or cgpa > 10:
            return make_response(
                jsonify({
                    "message": "CGPA must be between 0 and 10."
                }),
                400
            )

        if year_in_program is None or year_in_program < 1:
            return make_response(
                jsonify({
                    "message": "Invalid year in program."
                }),
                400
            )
        if year_in_program > student.program.duration:
            return make_response(
                jsonify({
                    "message": f"Year cannot exceed {student.program.duration}."
                }),
                400
            )

        existing_user = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_user:
            return make_response(
                jsonify({
                    "message": "Email already exists."
                }),
                409
            )

        student.name = name
        student.phone_no = phone_no
        student.cgpa = cgpa
        student.year_in_program = year_in_program

        student.user.email = email

        if password:

            if len(password) < 8:
                return make_response(
                    jsonify({
                        "message": "Password must be at least 8 characters."
                    }),
                    400
                )

            student.user.password = hash_password(password)

        db.session.commit()

        return make_response(
            jsonify({
                "message": "Profile updated successfully."
            }),
            200
        )


class StudentPlacementDrives(Resource):

    @auth_token_required
    @roles_required("student")
    def get(self):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        if not student:
            return make_response(
                jsonify({
                    "message": "Student not found."
                }),
                404
            )

        company = request.args.get("company", "").strip()
        job_title = request.args.get("job_title", "").strip()
        deadline = request.args.get("deadline")

        query = (
            Placement_Drive.query
            .join(Placement_Drive.company)
            .filter(
                Placement_Drive.status == "Approved",
                Placement_Drive.application_deadline >= datetime.now()
            )
        )

        if company:
            query = query.filter(
                Company.name.ilike(f"%{company}%")
            )

        if job_title:
            query = query.filter(
                Placement_Drive.job_title.ilike(f"%{job_title}%")
            )

        if deadline:
            try:
                deadline_date = datetime.strptime(
                    deadline,
                    "%Y-%m-%d"
                ).date()

                query = query.filter(
                    db.func.date(
                        Placement_Drive.application_deadline
                    ) == deadline_date
                )

            except ValueError:

                return make_response(
                    jsonify({
                        "message": "Invalid deadline."
                    }),
                    400
                )

        drives = []

        for drive in query.order_by(
            Placement_Drive.application_deadline
        ).all():

            # Skip if already applied
            already_applied = Application.query.filter_by(
                student_id=student.roll_no,
                drive_id=drive.id
            ).first()

            if already_applied:
                continue

            # Check whether the student satisfies ANY eligibility row
            eligible = False

            for eligibility in drive.eligibility:

                if (
                    eligibility.program_code == student.program_code
                    and student.cgpa >= eligibility.min_cgpa
                    and student.year_in_program == eligibility.eligible_year
                ):
                    eligible = True
                    break

            if not eligible:
                continue

            drives.append({

                "id": drive.id,
                "company": drive.company.name,
                "job_title": drive.job_title,
                "application_deadline": drive.application_deadline.strftime(
                    "%d %b %Y"
                )

            })

        return make_response(
            jsonify({
                "drives": drives
            }),
            200
        )


class StudentPlacementDrive(Resource):

    @auth_token_required
    @roles_required("student")
    def get(self, id):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        if not student:
            return make_response(
                jsonify({"message": "Student not found."}),
                404
            )

        drive = Placement_Drive.query.get(id)

        if not drive:
            return make_response(
                jsonify({"message": "Placement drive not found."}),
                404
            )

        if drive.status != "Approved":
            return make_response(
                jsonify({"message": "Placement drive unavailable."}),
                404
            )

        can_apply = True
        reason = None

        if student.placed:
            can_apply = False
            reason = "placed"

        elif drive.application_deadline < datetime.now():
            can_apply = False
            reason = "deadline_passed"

        elif Application.query.filter_by(
            student_id=student.roll_no,
            drive_id=drive.id
        ).first():
            can_apply = False
            reason = "already_applied"

        eligibility = []

        for item in drive.eligibility:

            eligibility.append({
                "id": item.eligibility_id,
                "program": item.program.name,
                "min_cgpa": item.min_cgpa,
                "eligible_year": item.eligible_year
            })

        return make_response(
            jsonify({

                "drive": {

                    "id": drive.id,
                    "company": drive.company.name,
                    "industry": drive.company.industry,
                    "website": drive.company.website,

                    "job_title": drive.job_title,
                    "job_description": drive.job_description,

                    "application_deadline":
                        drive.application_deadline.strftime(
                            "%d %b %Y %I:%M %p"
                        )

                },

                "eligibility": eligibility,

                "can_apply": can_apply,
                "reason": reason

            }),
            200
        )
    

class ApplyPlacementDrive(Resource):

    @auth_token_required
    @roles_required("student")
    def post(self, id):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        if not student:
            return make_response(
                jsonify({"message": "Student not found."}),
                404
            )

        drive = Placement_Drive.query.get(id)

        if not drive:
            return make_response(
                jsonify({"message": "Placement drive not found."}),
                404
            )

        if drive.status != "Approved":
            return make_response(
                jsonify({"message": "Placement drive unavailable."}),
                400
            )

        if student.placed:
            return make_response(
                jsonify({
                    "message": "You have already been placed."
                }),
                400
            )

        if drive.application_deadline < datetime.now():
            return make_response(
                jsonify({
                    "message": "Application deadline has passed."
                }),
                400
            )

        existing = Application.query.filter_by(
            student_id=student.roll_no,
            drive_id=drive.id
        ).first()

        if existing:
            return make_response(
                jsonify({
                    "message": "You have already applied."
                }),
                400
            )

        eligible = False

        for item in drive.eligibility:

            if (
                item.program_code == student.program_code
                and student.cgpa >= item.min_cgpa
                and student.year_in_program == item.eligible_year
            ):
                eligible = True
                break

        if not eligible:
            return make_response(
                jsonify({
                    "message": "You are not eligible for this drive."
                }),
                400
            )

        resume = request.files.get("resume")

        if not resume:
            return make_response(
                jsonify({
                    "message": "Resume is required."
                }),
                400
            )

        if not resume.filename.lower().endswith(".pdf"):
            return make_response(
                jsonify({
                    "message": "Resume must be a PDF."
                }),
                400
            )

        filename = f"{uuid4()}.pdf"

        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        resume.save(filepath)

        resume_record = Resume(
            file_path=filepath,
            student_id=student.roll_no
        )

        db.session.add(resume_record)
        db.session.flush()

        application = Application(

            resume_id=resume_record.id,
            student_id=student.roll_no,
            drive_id=drive.id,

            application_date=datetime.now(),
            status="Applied"

        )

        db.session.add(application)
        db.session.commit()

        return make_response(
            jsonify({
                "message": "Application submitted successfully."
            }),
            201
        )

from flask import jsonify, make_response

class StudentApplication(Resource):

    @auth_token_required
    @roles_required("student")
    def get(self, id):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        application = Application.query.filter_by(
            id=id,
            student_id=student.roll_no
        ).first()

        if not application:
            return make_response(
                jsonify({
                    "message": "Application not found."
                }),
                404
            )

        interview = None

        if application.interview:

            interview = {
                "status": application.interview.status,
                "datetime": application.interview.interview_datetime.strftime(
                    "%d %b %Y %I:%M %p"
                ),
                "details": application.interview.interview_details
            }

        offer = None

        if application.offer:

            offer = {
                "id": application.offer.id,
                "job_role": application.offer.job_role,
                "package": application.offer.package,
                "joining_date":
                    application.offer.joining_date.strftime("%d %b %Y")
                    if application.offer.joining_date else None,
                "status": application.offer.status
            }

        return make_response(
            jsonify({

                "application": {

                    "id": application.id,

                    "company":
                        application.placement_drive.company.name,

                    "job_title":
                        application.placement_drive.job_title,

                    "application_date":
                        application.application_date.strftime(
                            "%d %b %Y"
                        ),

                    "status":
                        application.status

                },

                "interview": interview,

                "offer": offer

            }),
            200
        )
    
from flask import send_file

class DownloadOffer(Resource):

    @auth_token_required
    @roles_required("student")
    def get(self, offer_id):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        offer = (
            Offer.query
            .join(Offer.application)
            .filter(
                Offer.id == offer_id,
                Application.student_id == student.roll_no
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

        return send_file(
            offer.offer_letter_path,
            as_attachment=True
        )

class AcceptOffer(Resource):

    @auth_token_required
    @roles_required("student")
    def post(self, offer_id):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        offer = (
            Offer.query
            .join(Offer.application)
            .filter(
                Offer.id == offer_id,
                Application.student_id == student.roll_no
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

        if offer.status != "Offered":

            return make_response(
                jsonify({
                    "message": "Offer has already been responded to."
                }),
                400
            )

        offer.status = "Accepted"

        student.placed = True

        for application in student.applications:

            if application.id == offer.application_id:
                continue

            if application.status in [
                "Applied",
                "Shortlisted"
            ]:

                application.status = "Cancelled"

        db.session.commit()

        return make_response(
            jsonify({
                "message": "Offer accepted successfully."
            }),
            200
        )
    
class RejectOffer(Resource):

    @auth_token_required
    @roles_required("student")
    def post(self, offer_id):

        student = Student.query.filter_by(
            user_id=current_user.id
        ).first()

        offer = (
            Offer.query
            .join(Offer.application)
            .filter(
                Offer.id == offer_id,
                Application.student_id == student.roll_no
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

        if offer.status != "Offered":

            return make_response(
                jsonify({
                    "message": "Offer has already been responded to."
                }),
                400
            )

        offer.status = "Rejected"

        db.session.commit()

        return make_response(
            jsonify({
                "message": "Offer rejected successfully."
            }),
            200
        )
    
    