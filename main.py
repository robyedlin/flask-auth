from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from env import ENV
import flask_auth.resolvers.users as user_resolvers
import flask_auth.utils as utils


app = Flask(__name__)

# mongodb
app.config['MONGO_URI'] = ENV['MONGO_URI']
# update json encoding for mongo data types
app.json_encoder = utils.MongoEngineJSONEncoder
mongo = PyMongo(app)
utils.setup_mongo_indexes(mongo)

# jwt
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
if ENV['FLASK_ENV'] != 'development':
    app.config['JWT_COOKIE_DOMAIN'] = ENV['COOKIE_DOMAIN']
app.config['JWT_COOKIE_SECURE'] = False if ENV['FLASK_ENV'] == 'development' else True
app.config['JWT_REFRESH_CSRF_HEADER_NAME'] = 'X-CSRF-REFRESH-TOKEN'
app.config['JWT_SECRET_KEY'] = ENV['JWT_SECRET_KEY']
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
jwt = JWTManager(app)

# cors
CORS(app)


# JWT methods
@jwt.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'subStatus': 'token_expired',
        'msg': 'The {} token has expired'.format(token_type)
    }), 401


@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    jti = decoded_token['jti']
    token = mongo.db.jwt.find_one({'jti': jti})
    if token:
        return token['revoked']
    else:
        return True


@app.route('/users', methods=['POST'])
def users():
    # user sign up
    if request.method == 'POST':
        response = user_resolvers.post(mongo)
        return response


@app.route('/users/auth-token', methods=['POST', 'PUT', 'DELETE'])
def users_auth_token():
    # create jwt (login)
    if request.method == 'POST':
        response = user_resolvers.auth_token_post(mongo)
        return response
    # refresh jwt
    if request.method == 'PUT':
        response = user_resolvers.auth_token_put(mongo)
        return response
    # delete jwt (logout)
    if request.method == 'DELETE':
        response = user_resolvers.auth_token_delete()
        return response


@app.route('/users/email/availability', methods=['POST'])
def users_availability():
    # checks if an email address is available
    if request.method == 'POST':
        response = user_resolvers.email_availability_post(mongo)
        return response


@app.route('/users/email', methods=['PUT'])
def users_email():
    # reset user email
    if request.method == 'PUT':
        response = user_resolvers.email_put(mongo)
        return response


@app.route('/users/password/forgot', methods=['POST', 'PUT'])
def users_password_forgot():
    # send forgot password email
    if request.method == 'POST':
        response = user_resolvers.password_forgot_post(mongo)
        return response
    # reset password from forgot email
    if request.method == 'PUT':
        response = user_resolvers.password_forgot_put(mongo)
        return response


@app.route('/users/password', methods=['PUT'])
def users_password():
    # reset password
    if request.method == 'PUT':
        response = user_resolvers.password_put(mongo)
        return response
