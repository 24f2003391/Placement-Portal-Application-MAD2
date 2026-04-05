from flask_restful import Resource
from flask import request,jsonify,make_response
from flask_security import utils,auth_token_required,roles_required 
from controller.datastore import user_datastore
from controller.models import Company,Student,Program,db

class GetCompanies(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = Company.query

        name = request.args.get('name')
        industry = request.args.get('industry')
        hr_phone = request.args.get('hr_phone')
        website = request.args.get('website')
        approval_status = request.args.get('approval_status')
        is_blacklisted = request.args.get('is_blacklisted')

        if name:
            query = query.filter(Company.name.ilike(f"%{name}%"))
        if industry:
            query = query.filter(Company.industry.ilike(f"%{industry}%"))
        if hr_phone:
            query = query.filter(Company.hr_phone == hr_phone)
        if website:
            query = query.filter(Company.website.ilike(f"%{website}%"))
        if approval_status:
            query = query.filter(Company.approval_status == approval_status)
        if is_blacklisted is not None:
            if is_blacklisted == 'true':
                query = query.filter(Company.user.has(active=True))
            elif is_blacklisted == 'false':
                query = query.filter(Company.user.has(active=False))
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