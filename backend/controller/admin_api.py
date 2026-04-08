from flask_restful import Resource
from flask import request,jsonify,make_response,send_from_directory,current_app
from flask_security import auth_token_required,roles_required 
from controller.models import Company,Student,db,Placement_Drive,Application
import os

from datetime import datetime

class GetCompanies(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = Company.query
        id = request.args.get('id')
        name = request.args.get('name')
        industry = request.args.get('industry')
        hr_phone = request.args.get('hr_phone')
        website = request.args.get('website')
        approval_status = request.args.get('approval_status')
        is_blacklisted = request.args.get('is_blacklisted')

        if id:
            query = query.filter(Company.id==int(id))
        if name:
            query = query.filter(Company.name.ilike(f"%{name}%"))
        if industry:
            query = query.filter(Company.industry.ilike(f"%{industry}%"))
        if hr_phone:
            query = query.filter(Company.hr_phone.ilike(f"%{hr_phone}%"))
        if website:
            query = query.filter(Company.website.ilike(f"%{website}%"))
        if approval_status:
            query = query.filter(Company.approval_status == approval_status)
        if is_blacklisted is not None:
            if is_blacklisted == 'true':
                query = query.filter(Company.user.has(active=False))
            elif is_blacklisted == 'false':
                query = query.filter(Company.user.has(active=True))
        companies = query.all()

        result = []
        for company in companies:
            result.append({
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
                "hr_phone": company.hr_phone,
                "website": company.website,
                "approval_status": company.approval_status,
                "is_blacklisted": not company.user.active 
            })

        return make_response(jsonify(result), 200)

class ApproveCompany(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, id):
        company = Company.query.get(id)
        if not company:
            return make_response(jsonify({"message": "Company not found"}),404)
        if company.approval_status == "Approved":
            return make_response(jsonify({"message": "Company registration already approved"}),400)
        if company.approval_status == "Rejected":
            return make_response(jsonify({"message": "Company registration already rejected"}),400)
        company.approval_status = "Approved"

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error approving company", "error": str(e)}),500)

        return make_response(
            jsonify({"message": "Company approved successfully",}),200)
    
class RejectCompany(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, id):
        company = Company.query.get(id)
        if not company:
            return make_response(jsonify({"message": "Company not found"}), 404)
        if company.approval_status == "Rejected":
            return make_response(jsonify({"message": "Company registration already rejected"}), 400)
        if company.approval_status == "Approved":
            return make_response(jsonify({"message": "Company already approved, cannot reject"}), 400)
        company.approval_status = "Rejected"
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error rejecting company", "error": str(e)}),500)
        return make_response(jsonify({"message": "Company rejected successfully"}),200)
    
class BlacklistCompany(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, id):
        company = Company.query.get(id)
        if not company:
            return make_response(jsonify({"message": "Company not found"}), 404)
        if company.user.active == False:
            return make_response(jsonify({"message": "Company already blacklisted"}), 400)
        company.user.active = False
        for drive in company.placement_drives:
            if drive.status in ['Pending', 'Approved']:
                drive.status = 'Closed'
            for app in drive.applications:  
                    app.status = 'Cancelled'
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error blacklisting company", "error": str(e)}),500)
        return make_response(jsonify({"message": "Company blacklisted successfully"}),200)
    
class UnblacklistCompany(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, id):
        company = Company.query.get(id)
        if not company:
            return make_response(jsonify({"message": "Company not found"}), 404)
        if company.user.active == True:
            return make_response(jsonify({"message": "Company is not blacklisted"}), 400)
        company.user.active = True
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(
                jsonify({"message": "Error unblacklisting company", "error": str(e)}),500)
        return make_response(jsonify({"message": "Company unblacklisted successfully"}),200)
    
class UnblacklistStudent(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, roll_no):
        student = Student.query.get(roll_no)
        if not student:
            return make_response(jsonify({"message": "Student not found"}), 404)
        if not student.user:
            return make_response(jsonify({"message": "No user linked to student"}), 400)
        if student.user.active == True:
            return make_response(jsonify({"message": "Student is not blacklisted"}), 400)
        student.user.active = True
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(
                jsonify({"message": "Error unblacklisting student","error": str(e)}),500)
        return make_response(jsonify({"message": "Student unblacklisted successfully"}),200)

class GetStudents(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = Student.query

        roll_no = request.args.get('roll_no')
        name = request.args.get('name')
        phone = request.args.get('phone')
        program_code = request.args.get('program')
        is_blacklisted = request.args.get('is_blacklisted')

        if name:
            query = query.filter(Student.name.ilike(f"%{name}%"))
        if roll_no:
            query = query.filter(Student.roll_no == int(roll_no))  
        if phone:
            query = query.filter(Student.phone_no.ilike(f"%{phone}%"))
        if program_code:
            query = query.filter(Student.program_code == program_code) 
        if is_blacklisted is not None:
            if is_blacklisted == 'true':
                query = query.filter(Student.user.has(active=False))  
            elif is_blacklisted == 'false':
                query = query.filter(Student.user.has(active=True))  

        students = query.all()
        result = []
        for s in students:
            result.append({
                "roll_no": s.roll_no,
                "name": s.name,
                "phone_no": s.phone_no,
                "program_name": s.program.name ,
                "cgpa": s.cgpa,
                "year_in_program": s.year_in_program,
                "is_blacklisted": not s.user.active 
            })

        return make_response(jsonify(result), 200)
    
class BlacklistStudent(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, roll_no):
        student = Student.query.get(roll_no)
        if not student:
            return make_response(jsonify({"message": "Student not found"}), 404)
        if not student.user:
            return make_response(jsonify({"message": "No user linked to student"}), 400)
        if student.user.active == False:
            return make_response(jsonify({"message": "Student already blacklisted"}), 400)
        student.user.active = False
        for app in student.applications:
            if app.status in ['Applied', 'Shortlisted']:
                app.status = 'Cancelled' 
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error blacklisting student","error": str(e)}),500)
        return make_response(jsonify({"message": "Student blacklisted and applications cancelled"}),200)
    
class GetDrives(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = Placement_Drive.query
        company_id = request.args.get('company_id')
        job_title = request.args.get('job_title')
        status = request.args.get('status')
        start_date = request.args.get('start_date')  
        end_date = request.args.get('end_date')      
        if company_id:
            query = query.filter(Placement_Drive.company_id == int(company_id))
        if job_title:
            query = query.filter(Placement_Drive.job_title.ilike(f"%{job_title}%"))
        if status:
            query = query.filter(Placement_Drive.status == status)
        if start_date:
           query = query.filter(Placement_Drive.application_deadline >= datetime.fromisoformat(start_date))
        if end_date:
           query = query.filter(Placement_Drive.application_deadline <= datetime.fromisoformat(end_date))
        drives = query.all()
        result = []
        for d in drives:
            result.append({
                "id": d.id,
                "company_id": d.company_id,
                "job_title": d.job_title,
                "application_deadline": d.application_deadline,
                "status": d.status
            })
        return make_response(jsonify(result), 200)
    
class GetDriveDetails(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, id):
        drive = Placement_Drive.query.get(id)
        if not drive:
            return make_response(jsonify({"message": "Drive not found"}), 404)
        result = {
            "id": drive.id,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "eligibility": [
                {
                    "id": e.eligibility_id,
                    "program": e.program,
                    "min_cgpa": e.min_cgpa,
                    "year": e.year
                } for e in drive.eligibility
            ]
        }
        return make_response(jsonify(result), 200)
    
class ApproveDrive(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, id):
        drive = Placement_Drive.query.get(id)
        if not drive:
            return make_response(jsonify({"message": "Drive not found"}), 404)
        if drive.status == "Approved":
            return make_response(jsonify({"message": "Already approved"}), 400)
        if drive.status == "Rejected":
            return make_response(jsonify({"message": "Already rejected"}), 400)
        drive.status = "Approved"
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error", "error": str(e)}), 500)
        return make_response(jsonify({"message": "Drive approved"}), 200)
    
class RejectDrive(Resource):
    @auth_token_required
    @roles_required('admin')
    def put(self, id):
        drive = Placement_Drive.query.get(id)
        if not drive:
            return make_response(jsonify({"message": "Drive not found"}), 404)
        if drive.status == "Rejected":
            return make_response(jsonify({"message": "Already rejected"}), 400)
        if drive.status == "Approved":
            return make_response(jsonify({"message": "Already approved"}), 400)
        drive.status = "Rejected"
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error", "error": str(e)}), 500)
        return make_response(jsonify({"message": "Drive rejected"}), 200)

class GetApplications(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = Application.query.join(Student).join(Placement_Drive)
        drive_id = request.args.get('drive_id')
        student_id = request.args.get('student_id')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if drive_id:
            query = query.filter(Application.drive_id == int(drive_id))
        if student_id:
            query = query.filter(Application.student_id == int(student_id))
        if status:
            query = query.filter(Application.status == status)
        if start_date:
            query = query.filter(Application.application_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Application.application_date <= datetime.fromisoformat(end_date))
        applications = query.all()
        result = []
        for app in applications:
            result.append({
                "id": app.id,
                "drive_id": app.drive_id,
                "job_title": app.placement_drive.job_title,
                "student_roll_no": app.student.roll_no,
                "student_name": app.student.name,
                "application_date": app.application_date,
                "status": app.status
            })

        return make_response(jsonify(result), 200) 

class GetResume(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, application_id):
        app = Application.query.get(application_id)
        if not app:
            return make_response(jsonify({"message": "Application not found"}), 404)
        resume = app.resume
        if not resume:
            return make_response(jsonify({"message": "Resume not found"}), 404)
        filename = os.path.basename(resume.file_path)
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=True
        )