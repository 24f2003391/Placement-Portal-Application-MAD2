from flask_restful import Resource
from flask import request,jsonify,make_response
from flask_security import utils,auth_token_required,roles_required 
from controller.datastore import user_datastore
from controller.models import Company,Student,Program,db