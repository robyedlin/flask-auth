import os
from flask import jsonify
from pymongo import MongoClient
import app_admin.utils as utils


# this method is dangerous, but there are 3 checks in place to prevent a production accident
def reset(mongo):
    # only allow this if in development
    if os.environ['FLASK_ENV'] == 'development':
        # mongo will never be setup on localhost in production
        client = MongoClient('localhost', 27017)
        # mongo db will never be prepended with -dev in production
        client.drop_database('app-admin-dev')
        utils.setup_mongo_indexes(mongo)
        response = jsonify({})
        response.status_code = 200
        return response
