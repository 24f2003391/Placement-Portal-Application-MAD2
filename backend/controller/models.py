from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin,RoleMixin

db=SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    email=db.Column(db.String(320),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)

    active = db.Column(db.Boolean, default=True, nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier=db.Column(db.String(255),unique=True,nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role=db.relationship('Role',uselist=False,)

class Role(db.Model,RoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Student(db.Model):
    __tablename__='student'
    roll_no = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable=False)  
    phone_no=db.Column(db.String(15), nullable=False)

    program = db.Column(db.String(100), nullable=False)  
    cgpa = db.Column(db.Float, nullable=False)  
    year_in_program= db.Column(db.Integer, nullable=False)   

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', uselist=False)
    resume = db.relationship("Resume", uselist=True)    
    applications = db.relationship('Application',  back_populates="student", uselist=True)
    
class Resume(db.Model):
    __tablename__ = 'resume'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    name = db.Column(db.String(100), nullable=False)      
    industry =db.Column(db.String(100), nullable=False)   

    hr_email=db.Column(db.String(320),unique=True,nullable=False)
    hr_phone = db.Column(db.String(15), nullable=False)                     
    website = db.Column(db.Text, nullable=True)                        
    approval_status = db.Column(db.Enum('Applied','Approved','Rejected'), default='Applied',nullable=False)  

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', uselist=False)
    placement_drive = db.relationship('Placement_Drive', back_populates="company", uselist=True)

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)

    application_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('Applied', 'Shortlisted', 'Selected', 'Rejected'),default='Applied',nullable=False)
    
    student = db.relationship('Student', back_populates="applications", uselist=False)
    placement_drive = db.relationship('Placement_Drive', back_populates="applications", uselist=False)
    resume = db.relationship('Resume', uselist=False)

class Placement_Drive(db.Model):
    __tablename__ = 'placement_drive'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False) 

    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Closed', 'Rejected'),default='Pending',nullable=False)

    company = db.relationship('Company', back_populates="placement_drive", uselist=False)
    eligibility = db.relationship('Eligibility', back_populates="placement_drive", uselist=True)
    applications = db.relationship('Application', back_populates="placement_drive", uselist=True)

class Eligibility(db.Model):
    __tablename__ = 'eligibility'
    eligibility_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)  
    
    program = db.Column(db.String(100), nullable=False)  
    min_cgpa = db.Column(db.Float, nullable=False)       
    year = db.Column(db.Integer, nullable=False)         
    
    placement_drive = db.relationship('Placement_Drive', back_populates="eligibility", uselist=False)