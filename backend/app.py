from flask import Flask, jsonify,request
from flask_security import Security
from flask_restful import Api

from controller.models import db
from controller.datastore import user_datastore
from controller.config import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    security=Security(app,user_datastore)

    api=Api(app,prefix='/api')
    return app,api

app,api=create_app()

with app.app_context():
    db.create_all()

    admin_role=user_datastore.find_or_create_role(name='admin')
    company_role=user_datastore.find_or_create_role(name='company')
    student_role=user_datastore.find_or_create_role(name='student')

    if not user_datastore.find_user(email="admin@gmail.com"):
        user_datastore.create_user(email="admin@gmail.com",password="admin123",roles=[admin_role])
    db.session.commit()

from controller.auth_api import Login,Logout,StudentRegister,CompanyRegister

api.add_resource(Login,'/login')
api.add_resource(Logout,'/logout')
api.add_resource(CompanyRegister,'/company/register')
api.add_resource(StudentRegister,'/student/register')

if __name__ == '__main__':    
    app.run(debug=True)
