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
    fs_token_uniquifier=db.Column(db.String(255),unique=True,nullable=True)

    roles=db.relationship('Role',secondary='user_roles')
    company = db.relationship('Company',back_populates='user', uselist=False)
    student = db.relationship('Student',back_populates='user', uselist=False)

class Role(db.Model,RoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class Student(db.Model):
    __tablename__='student'
    roll_no = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable=False)  
    phone_no=db.Column(db.String(15), nullable=False)

    program_code = db.Column(db.String(10),db.ForeignKey('program.code'), nullable=False)  
    cgpa = db.Column(db.Float, nullable=False)  
    year_in_program= db.Column(db.Integer, nullable=False)
    placed=db.Column(db.Boolean,default=False)   

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False,unique=True)
    user = db.relationship('User',back_populates='student', uselist=False)
    resume = db.relationship("Resume", uselist=True)    
    applications = db.relationship('Application',  back_populates="student", uselist=True)
    program = db.relationship('Program', uselist=False)

class Program(db.Model):
    __tablename__='program'
    code=db.Column(db.String(10),primary_key=True)
    name=db.Column(db.String(100),nullable=False,unique=True)
    duration=db.Column(db.Integer,nullable=False)
    description=db.Column(db.Text,nullable=True)
    
class Resume(db.Model):
    __tablename__ = 'resume'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.roll_no'), nullable=False)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    name = db.Column(db.String(100), nullable=False)      
    industry =db.Column(db.String(100), nullable=False)   

    hr_phone = db.Column(db.String(15), nullable=False,unique=True)                     
    website = db.Column(db.Text, nullable=True)                        
    approval_status = db.Column(db.Enum('Applied','Approved','Rejected'), default='Applied',nullable=False)  

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User',back_populates='company', uselist=False)
    placement_drives = db.relationship('Placement_Drive', back_populates="company", uselist=True,lazy="selectin")

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.roll_no'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)

    application_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('Applied', 'Shortlisted', 'Selected', 'Rejected','Cancelled'),default='Applied',nullable=False)
    
    student = db.relationship('Student', back_populates="applications", uselist=False)
    placement_drive = db.relationship('Placement_Drive', back_populates="applications", uselist=False)
    resume = db.relationship('Resume', uselist=False)
    offer = db.relationship('Offer', back_populates='application', uselist=False)
    interview = db.relationship(
    "Interview",
    back_populates="application",
    uselist=False,
    cascade="all, delete-orphan"
)

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)

    package = db.Column(db.Float, nullable=False)  
    job_role = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.Enum('Offered', 'Accepted', 'Rejected'),default='Offered',nullable=False)
    offer_letter_path = db.Column(db.Text, nullable= False)

    application = db.relationship('Application', back_populates='offer',lazy="selectin",uselist=False
)

class Placement_Drive(db.Model):
    __tablename__ = 'placement_drive'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False) 

    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Closed', 'Rejected'),default='Pending',nullable=False)

    company = db.relationship('Company', back_populates="placement_drives", uselist=False)
    eligibility = db.relationship('Eligibility', back_populates="placement_drive", uselist=True)
    applications = db.relationship('Application', back_populates="placement_drive", uselist=True)

class Eligibility(db.Model):
    __tablename__ = "eligibility"

    eligibility_id = db.Column(db.Integer, primary_key=True)

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("placement_drive.id"),
        nullable=False
    )

    program_code = db.Column(
        db.String(10),
        db.ForeignKey("program.code"),
        nullable=False
    )

    min_cgpa = db.Column(db.Float, nullable=False)

    eligible_year = db.Column(db.Integer, nullable=False)

    placement_drive = db.relationship(
        "Placement_Drive",
        back_populates="eligibility"
    )

    program = db.relationship(
        "Program",
        uselist=False
    )

class Interview(db.Model):
    __tablename__ = "interview"

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("application.id"),
        nullable=False,
        unique=True
    )

    company_id = db.Column(
    db.Integer,
    db.ForeignKey("company.id"),
    nullable=False
)

    interview_datetime = db.Column(
        db.DateTime,
        nullable=False
    )

    interview_details = db.Column(
    db.Text,
    nullable=False
)

    status = db.Column(
        db.Enum(
            "Scheduled",
            "Completed",
            "Cancelled"
        ),
        default="Scheduled",
        nullable=False
    )

    application = db.relationship(
        "Application",
        uselist=False
    )