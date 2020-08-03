from flask import jsonify
from pymongo import MongoClient
from flask_auth.env import ENV
import flask_auth.utils as utils


# this method is dangerous, but there are checks in place to prevent a production accident
def reset(mongo):
    # only allow this if in development
    if ENV['FLASK_ENV'] == 'development':
        # mongo should never be setup on localhost in production
        client = MongoClient('localhost', 27017)
        client.drop_database(ENV['DB_NAME'])
        utils.setup_mongo_indexes(mongo)
        response = jsonify({})
        response.status_code = 200
        return response
