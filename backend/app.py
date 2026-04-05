from flask import Flask, jsonify,request
from flask_security import Security,utils
from flask_restful import Api

from controller.models import db
from controller.datastore import user_datastore
from controller.config import config

from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    security=Security(app,user_datastore)

    api=Api(app,prefix='/api')
    return app,api

app,api=create_app()
CORS(app, origins="http://localhost:5173")

with app.app_context():
    db.create_all()

    admin_role=user_datastore.find_or_create_role(name='admin')
    company_role=user_datastore.find_or_create_role(name='company')
    student_role=user_datastore.find_or_create_role(name='student')

    if not user_datastore.find_user(email="admin@gmail.com"):
        user_datastore.create_user(email="admin@gmail.com",password=utils.hash_password("admin123"),roles=[admin_role])
    db.session.commit()

from controller.auth_api import Login,Logout,StudentRegister,CompanyRegister,CheckEmailAvail,CheckPhoneAvail,CheckRollAvail,GetPrograms

api.add_resource(Login,'/login')
api.add_resource(Logout,'/logout')
api.add_resource(CompanyRegister,'/company/register')
api.add_resource(StudentRegister,'/student/register')

api.add_resource(CheckEmailAvail,'/check-email')
api.add_resource(CheckPhoneAvail, '/check-phone')
api.add_resource(CheckRollAvail, '/check-roll')
api.add_resource(GetPrograms, '/programs')

if __name__ == '__main__':    
    app.run(debug=True)
