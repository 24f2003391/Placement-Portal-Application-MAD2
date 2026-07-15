from flask_restful import Resource
from flask import request,jsonify,make_response,current_app,send_from_directory
from flask_security import utils,auth_token_required,roles_required
from controller.datastore import user_datastore
from controller.models import Company,Student,Program,db

from email_validator import validate_email, EmailNotValidError
import phonenumbers
from celery.result import AsyncResult
import os


class ExportStatus(Resource):

    @auth_token_required
    @roles_required("student","company")
    def get(self, task_id):
        from celery_app import celery
        result = AsyncResult(
            task_id,
            app=celery
        )

        if result.successful():

            return make_response(
                jsonify({
                    "status": "SUCCESS",
                    "filename": result.result
                }),
                200
            )

        return make_response(
            jsonify({
                "status": result.status
            }),
            200
        )
class DownloadExport(Resource):

    @auth_token_required
    @roles_required("student","company")
    def get(self, filename):
        from celery_app import celery
        filepath = os.path.join(
            current_app.config["EXPORT_FOLDER"],
            filename
        )

        if not os.path.isfile(filepath):

            return make_response(
                jsonify({
                    "message": "Export not found."
                }),
                404
            )

        return send_from_directory(
            current_app.config["EXPORT_FOLDER"],
            filename,
            as_attachment=True
        )
    
class GetPrograms(Resource):
    def get(self):
        programs = Program.query.all()
        result = []
        for p in programs:
            result.append({
                "code": p.code,
                "name": p.name,
                "duration": p.duration
            })

        return make_response(jsonify(result), 200)

class CheckEmailAvail(Resource):
    def post(self):
        crediential = request.get_json()
        if not crediential:
            result = {'message': 'Request body is required.'}
            return make_response(jsonify(result), 400)
        
        email = crediential.get('email', None)
        if not email:
            result = {'message': 'Email is required.'}
            return make_response(jsonify(result), 400)
        
        user = user_datastore.find_user(email=email)
        if user:
            return make_response(jsonify({'available': False}), 200)
        else:
            return make_response(jsonify({'available': True}), 200)
        
class CheckPhoneAvail(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({'message': 'Request body is required.'}), 400)
        phone = data.get('phone_no')
        if not phone:
            return make_response(jsonify({'message': 'Phone number is required.'}), 400)

        company = Company.query.filter_by(hr_phone=phone).first()
        student = Student.query.filter_by(phone_no=phone).first()
        if company or student:
            return jsonify({'available': False})
        else:
            return jsonify({'available': True})
        
class CheckRollAvail(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({'message': 'Request body is required.'}), 400)
        roll_no = data.get('roll_no')
        if not roll_no:
            return make_response(jsonify({'message': 'Roll number is required.'}), 400)
        existing = Student.query.filter_by(roll_no=roll_no).first()
        if existing:
            return make_response(jsonify({'available': False}), 200)
        else:
            return make_response(jsonify({'available': True}), 200)

class Login(Resource):
    def post(self):
        login_credentials= request.get_json()
        if not login_credentials:
            result={'message':'Login credentials are required'}
            return make_response(jsonify(result),400)
            
        email=login_credentials.get('email')
        password=login_credentials.get('password')

        if not email or not password:
            result={'message':'Email and password are required'}
            return make_response(jsonify(result),400)
        
        user=user_datastore.find_user(email=email)
        if not user:
            result={'message':'User not found'}
            return make_response(jsonify(result),404)
        
        if not utils.verify_password(password,user.password):
            result={'message':'Invalid credentials'}
            return make_response(jsonify(result),401)
        
        if not user.active:
            response={'message':'User has been blacklisted'}
            return make_response(jsonify(response),403)
        
        if user.has_role('company'):
            if user.company.approval_status=='Applied':
                response={'message':'Company registration has not been approved yet'}
                return make_response(jsonify(response),403)
            elif user.company.approval_status=='Rejected':
                response={'message':'Company registration has been rejected'}
                return make_response(jsonify(response),403)

        auth_token=user.get_auth_token()
        utils.login_user(user)
        response= {
            'message':'Login successful',
            'data':{
                'user':{
                    'id':user.id,
                    'roles':[role.name for role in user.roles]},
                'auth_token':auth_token
            }
        }
        return make_response(jsonify(response),200)
    
class Logout(Resource):
    @auth_token_required
    def post(self):
        utils.logout_user()
        response={'message':'Logged out successfully'}
        return make_response(jsonify(response),200)
    
class StudentRegister(Resource):
    def post(self):
        registration_details= request.get_json()
        if not registration_details:
            response={'message':'registration_details are required'}
            return make_response(jsonify(response),400)
        
        email=registration_details.get('email')
        password=registration_details.get('password')
        name = registration_details.get('name')
        roll_no = registration_details.get('roll_no')
        phone_no = registration_details.get('phone_no')
        program_code = registration_details.get('program_code')
        cgpa = registration_details.get('cgpa')
        year_in_program = registration_details.get('year_in_program')

        if not all([email,password,name,roll_no,phone_no,program_code,cgpa,year_in_program]):
            response={'message':'All fields are required'}
            return make_response(jsonify(response),400)
        
        if not all(char.isalpha() or char.isspace() for char in name) or len(name) > 100:
            response={'message':'Name can only contain letters and should be maximum 100 characters'}
            return make_response(jsonify(response),400)
        
        try:
            valid = validate_email(email)
            email = valid.email  
        except EmailNotValidError as e:
            response = {'message': 'Invalid email'}
            return make_response(jsonify(response), 400)
        existing_user = user_datastore.find_user(email=email)
        if existing_user:
            return make_response(jsonify({'message': f'Email "{email}" is already registered'}), 400)
        
        try:
            phone_obj = phonenumbers.parse(phone_no, "IN")  
            if not phonenumbers.is_valid_number(phone_obj):
                raise ValueError()
        except Exception:
            return make_response(jsonify({'message': 'Invalid phone number'}), 400)

        if not str(roll_no).isdigit():
            response = {'message': 'Roll number must be numeric'}
            return make_response(jsonify(response), 400)
        existing_student = Student.query.filter_by(roll_no=roll_no).first()
        if existing_student:
            return make_response(jsonify({'message': f'Roll number "{roll_no}" is already registered'}), 400)
        
        program = Program.query.filter_by(code=program_code).first()
        if not program:
            response={'message': 'Program does not exist'}
            return make_response(jsonify(response), 400)

        try:
            cgpa = float(cgpa)
            if not (0.0 <= cgpa <= 10.0):
                raise ValueError()
        except ValueError:
            response = {'message': 'CGPA must be a number between 0 and 10'}
            return make_response(jsonify(response), 400)

        try:
            year_in_program = int(year_in_program)
        except ValueError:
            response={'message': 'Year in program must be a positive integer'}
            return make_response(jsonify(response), 400)
        if year_in_program <= 0:
            response={'message': 'Year in program must be greater than 0'}
            return make_response(jsonify(response), 400)
        if year_in_program > program.duration:
            response={'message': f'Year in program cannot exceed program duration: ({program.duration} years)'}
            return make_response(jsonify(response), 400)
        
        if len(password)<8:
             return make_response(jsonify({'message': 'Password should be atleast 8 characters'}), 400)
        
        student_role = user_datastore.find_role('student')
        student = Student(
            roll_no=roll_no,
            name=name,
            phone_no=phone_no,
            program=program,
            cgpa=cgpa,
            year_in_program=year_in_program
        )

        user_datastore.create_user(
            email=email,
            password=utils.hash_password(password),
            roles=[student_role],
            student=student 
        )
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error registering student", "error": str(e)}),500)
        return make_response(jsonify({'message': 'Student registered successfully'}), 201)

class CompanyRegister(Resource):
    def post(self):
        registration_details = request.get_json()
        if not registration_details :
            return make_response(jsonify({'message': 'registration details are required'}), 400)

        email = registration_details.get('email')
        password = registration_details.get('password')
        name = registration_details.get('name')
        industry =registration_details.get('industry')
        hr_phone = registration_details.get('hr_phone')
        website = registration_details.get('website')

        if not all([email, password, name, industry, hr_phone]):
            return make_response(jsonify({'message': 'All fields except website are required'}), 400)

        try:
            validate_email(email)
        except EmailNotValidError:
            return make_response(jsonify({'message': 'Invalid Email'}), 400)
        if user_datastore.find_user(email=email):
            return make_response(jsonify({'message': f'Email "{email}" is already registered'}), 400)
        
        try:
            phone_parsed = phonenumbers.parse(hr_phone,"IN")
            if not phonenumbers.is_valid_number(phone_parsed):
                raise ValueError()
        except Exception:
            return make_response(jsonify({'message': 'Invalid phone number'}), 400)
        existing_comp= Company.query.filter_by(hr_phone=hr_phone).first()
        if existing_comp:
            return make_response(jsonify({'message': f'Phone no. "{hr_phone}" is already registered'}), 400)
        
        if len(name) > 100:
            return make_response(jsonify({'message': 'Name can only contain letters and spaces, max 100 chars'}), 400)

        if not all(char.isalpha() or char.isspace() for char in industry) or len(industry) > 100:
            return make_response(jsonify({'message': 'Industry can only contain letters and spaces, max 100 chars'}), 400)
        
        if len(password)<8:
             return make_response(jsonify({'message': 'Password should be atleast 8 characters'}), 400)


        company_role = user_datastore.find_role('company')
        company_obj = Company(
            name=name,
            industry=industry,
            hr_phone=hr_phone,
            website=website
        )
        user_datastore.create_user(
            email=email,
            password=utils.hash_password(password),
            roles=[company_role],
            company=company_obj 
        )
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Error registering company", "error": str(e)}),500)
        return make_response(jsonify({'message': 'Company registered successfully, Wait for approval'}), 201)