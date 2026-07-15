from flask import Flask
from flask_security import Security,utils
from flask_restful import Api

from controller.models import db
from controller.datastore import user_datastore
from controller.config import Config

from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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

from controller.auth_helpers_api import Login,Logout,StudentRegister,CompanyRegister,CheckEmailAvail,CheckPhoneAvail,CheckRollAvail,GetPrograms\
,ExportStatus,DownloadExport
api.add_resource(ExportStatus,'/export/status/<string:task_id>')
api.add_resource(DownloadExport,'/export/download/<string:filename>')
api.add_resource(Login,'/login')
api.add_resource(Logout,'/logout')
api.add_resource(CompanyRegister,'/company/register')
api.add_resource(StudentRegister,'/student/register')

api.add_resource(CheckEmailAvail,'/check-email')
api.add_resource(CheckPhoneAvail, '/check-phone')
api.add_resource(CheckRollAvail, '/check-roll')
api.add_resource(GetPrograms, '/programs')

from controller.admin_api import GetDrives,ApproveDrive,RejectDrive,GetCompanies,RejectCompany,ApproveCompany,BlacklistCompany,UnblacklistCompany\
,GetStudents,BlacklistStudent,UnblacklistStudent,GetDriveDetails,GetApplications,GetResume,GetStudentPlacement,DownloadOffer,AdminDashboard

api.add_resource(GetDrives, "/admin/drives")
api.add_resource(GetDriveDetails, "/admin/drive-details/<int:id>")
api.add_resource(ApproveDrive, "/admin/drives/<int:id>/approve")
api.add_resource(RejectDrive, "/admin/drives/<int:id>/reject")

api.add_resource(GetCompanies, "/admin/companies")
api.add_resource(RejectCompany, "/admin/companies/<int:id>/reject")
api.add_resource(ApproveCompany, "/admin/companies/<int:id>/approve")
api.add_resource(BlacklistCompany, "/admin/companies/<int:id>/blacklist")
api.add_resource(UnblacklistCompany, "/admin/companies/<int:id>/unblacklist")

api.add_resource(GetStudents, "/admin/students")
api.add_resource(BlacklistStudent, "/admin/students/<int:roll_no>/blacklist")
api.add_resource(UnblacklistStudent, "/admin/students/<int:roll_no>/unblacklist")

api.add_resource(
    GetApplications,
    "/admin/applications"
)

api.add_resource(
    GetResume,
    "/admin/applications/<int:application_id>/resume"
)
api.add_resource(
    GetStudentPlacement,
    "/admin/students/<int:roll_no>/placement"
)

api.add_resource(
    DownloadOffer,
    "/admin/offers/<int:offer_id>/download"
)
api.add_resource(AdminDashboard, "/admin/dashboard")

from controller.company_api import CompanyDashboard,CompanyDrives,CloseDrive,\
CancelInterview,CompanyInterview,CompanyViewResume,CompleteInterview,CompanyDriveApplications,\
CompanyDriveDetails,UpdateApplicationStatus,CompanyOffer,CompanyOfferDetails,ExportCompany
api.add_resource(
    ExportCompany,
    "/company/export"
)

api.add_resource(CompanyDashboard,"/company/dashboard")
api.add_resource(
    CompanyDrives,
    "/company/drives"
)

api.add_resource(
    CloseDrive,
    "/company/drives/<int:id>/close"
)
api.add_resource(
    CompanyInterview,
    "/company/applications/<int:application_id>/interview"
)

api.add_resource(
    CancelInterview,
    "/company/interviews/<int:interview_id>/cancel"
)

api.add_resource(
    CompleteInterview,
    "/company/interviews/<int:interview_id>/complete"
)

api.add_resource(
    CompanyViewResume,
    "/company/applications/<int:application_id>/resume"
)

api.add_resource(
    CompanyDriveDetails,
    "/company/drives/<int:drive_id>"
)

api.add_resource(
    CompanyDriveApplications,
    "/company/drives/<int:drive_id>/applications"
)
api.add_resource(
    UpdateApplicationStatus,
    "/company/applications/<int:application_id>"
)

api.add_resource(
    CompanyOffer,
    "/company/applications/<int:application_id>/offer"
)

api.add_resource(
    CompanyOfferDetails,
    "/company/offers/<int:offer_id>"
)

from controller.student_api import StudentDashboard,StudentProfile,StudentPlacementDrives,StudentPlacementDrive\
,ApplyPlacementDrive,AcceptOffer,RejectOffer,StudentApplication,DownloadStudentOffer,ExportStudent

api.add_resource(ExportStudent,"/student/export")
api.add_resource(StudentDashboard,"/student/dashboard")
api.add_resource(
    StudentProfile,
    "/student/profile"
)
api.add_resource(
    StudentPlacementDrives,
    "/student/placement-drives"
)
api.add_resource(
    StudentPlacementDrive,
    "/student/placement-drives/<int:id>"
)

api.add_resource(
    ApplyPlacementDrive,
    "/student/placement-drives/<int:id>/apply"
)

api.add_resource(
    StudentApplication,
    "/student/applications/<int:id>"
)

api.add_resource(
    DownloadStudentOffer,
    "/student/offers/<int:offer_id>/download"
)

api.add_resource(
    AcceptOffer,
    "/student/offers/<int:offer_id>/accept"
)

api.add_resource(
    RejectOffer,
    "/student/offers/<int:offer_id>/reject"
)


if __name__ == '__main__':    
    app.run(debug=True)
