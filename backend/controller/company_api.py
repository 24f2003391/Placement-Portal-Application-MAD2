from flask_restful import Resource
from flask import request,jsonify,make_response,current_app
from flask_security import auth_token_required,roles_required ,current_user
from controller.models import Company,Student,db,Placement_Drive,Application

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

        active_drives = sum(
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
                "active_drives": active_drives,
                "pending_drives": pending_drives,
                "closed_drives": closed_drives,
                "total_applications": total_applications,
                "shortlisted": shortlisted,
                "selected": selected
            },

            "recent_drives": recent
        }

        return make_response(jsonify(result), 200)