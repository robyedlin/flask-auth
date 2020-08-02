import os
import argon2
from app_admin.utils import (
    add_jwt_to_db,
    format_email_address,
    send_email,
    validate_data
)
from flask import abort, jsonify, request, current_app
from jsonschema import validate
from datetime import datetime
from flask_pymongo import ObjectId
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    decode_token, fresh_jwt_required, get_jwt_identity,
    jwt_refresh_token_required, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)


pw_hasher = argon2.PasswordHasher()

TYPES = {
    'email': {
        'type': 'string',
        'minLength': 3,
        'format': 'email'
    },
    'password': {
        'type': 'string',
        'minLength': 8,
        'maxLength': 50
    },
    'token': {
        'type': 'string'
    }
}


def auth_token_delete():
    response = jsonify({})
    response.status_code = 204
    unset_jwt_cookies(response)
    return response


def auth_token_post(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'email': TYPES['email'],
            'password': TYPES['password']
        },
        'required': ['email', 'password'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    # business logic and data prep
    data = post_data
    data['email'] = format_email_address(data['email'])

    # find user
    user = mongo.db.users.find_one({
        'email': data['email']
    })
    if not user:
        abort(401)

    # verify password
    try:
        pw_hasher.verify(user['password'], data['password'])
    except Exception as e:
        print(e)
        abort(401)

    # create the tokens to be sent back to the user
    access_token = create_access_token(identity=user['_id'], fresh=True)
    refresh_token = create_refresh_token(identity=user['_id'])

    # store the tokens in our store with a status of not currently revoked.
    add_jwt_to_db(
        mongo,
        access_token,
        current_app.config['JWT_IDENTITY_CLAIM']
    )
    add_jwt_to_db(
        mongo,
        refresh_token,
        current_app.config['JWT_IDENTITY_CLAIM']
    )

    response = jsonify({'userId': user['_id']})
    response.status_code = 201

    # set tokens in cookies
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    # return jwt
    return response


@jwt_refresh_token_required
def auth_token_put(mongo):
    # create the new access token
    user_id = get_jwt_identity()

    # create the tokens to be sent back to the user
    access_token = create_access_token(identity=user_id, fresh=False)
    refresh_token = create_refresh_token(identity=user_id)

    # store the tokens in our store with a status of not currently revoked.
    add_jwt_to_db(
        mongo,
        access_token,
        current_app.config['JWT_IDENTITY_CLAIM']
    )
    add_jwt_to_db(
        mongo,
        refresh_token,
        current_app.config['JWT_IDENTITY_CLAIM']
    )

    response = jsonify({'user_id': user_id})
    response.status_code = 204

    # set tokens in cookies
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response


def email_availability_post(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'email': TYPES['email']
        },
        'required': ['email'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    # data prep
    data = post_data

    # find user by email
    user = mongo.db.users.find_one({
        'email': data['email']
    })

    available = False if user else True

    response = jsonify({
        'available': available
    })
    response.status_code = 200
    return response


@fresh_jwt_required
def email_put(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'email': TYPES['email']
        },
        'required': ['email'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    user_id = get_jwt_identity()

    data = post_data
    data['email'] = format_email_address(data['email'])
    current_time = datetime.utcnow()
    data['updated'] = current_time
    # new email, so it's unverified
    data['verified'] = False

    # check for existing user before inserting
    existing_user = mongo.db.users.find_one({
        'email': data['email']
    })
    if existing_user:
        abort(409)

    # update email
    mongo.db.users.find_one_and_update({'_id': ObjectId(str(user_id))}, {
        '$set': data
    })

    response = jsonify({})
    response.status_code = 201
    return response


def password_forgot_post(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'email': TYPES['email']
        },
        'required': ['email'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    # business logic and data prep
    data = post_data
    data['email'] = format_email_address(data['email'])

    # find user
    user = mongo.db.users.find_one({'email': data['email']})

    # if user, create token and send email
    if user:
        token = create_access_token(identity=user['_id'], fresh=True)
        send_email(
            to_email=user['email'],
            subject='Reset Your Password',
            html_content='''
                <p>Hello,</p>
                <p>Someone (you, we hope) requested to reset the password for {email} on the {website_name} website.</p>
                <p>Here is a link to  <a href="{website_domain}/users/password/reset?token={token}">reset your password</a></p>
                <p>Alternatively, you may paste the following url in your browser: {website_domain}/users/password/reset?token={token}</p>
                <p><strong>For your security, you have 15 minutes to reset this password. Afterward, this link will expire.</strong></p>
                <p>If you did not request to reset your password, you can ignore this, or reply to this email and let us know.</p>
                <p>- The App Admin Team</p>
            '''.format(
                email=user['email'],
                token=token,
                website_domain=os.environ['WEBSITE_DOMAIN'],
                website_name=os.environ['WEBSITE_NAME']
            )
        )

    response = jsonify({})
    response.status_code = 201
    return response


def password_forgot_put(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'password': TYPES['password'],
            'token': TYPES['token']
        },
        'required': ['password', 'token'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    # business logic and data prep
    data = post_data

    try:
        user_id = decode_token(data['token'])['identity']
    except Exception as e:
        print(e)
        abort(401)

    del data['token']
    data['password'] = pw_hasher.hash(data['password'])
    current_time = datetime.utcnow()
    data['updated'] = current_time
    mongo.db.users.find_one_and_update({'_id': ObjectId(str(user_id))}, {
        '$set': data
    })

    response = jsonify({
        'userId': user_id
    })
    response.status_code = 204
    return response


@fresh_jwt_required
def password_put(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'password': TYPES['password']
        },
        'required': ['password'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    user_id = get_jwt_identity()

    data = post_data
    data['password'] = pw_hasher.hash(data['password'])
    current_time = datetime.utcnow()
    data['updated'] = current_time

    # update email
    mongo.db.users.find_one_and_update({'_id': ObjectId(str(user_id))}, {
        '$set': data
    })

    response = jsonify({})
    response.status_code = 204
    return response


def post(mongo):
    # get post data
    post_data = request.get_json()

    # validate post data
    schema = {
        'type': 'object',
        'properties': {
            'email': TYPES['email'],
            'password': TYPES['password']
        },
        'required': ['email', 'password'],
        'additionalProperties': False
    }
    validate_data(post_data, schema)

    # business logic and data prep
    data = post_data
    data['email'] = format_email_address(data['email'])
    data['verified'] = False
    data['password'] = pw_hasher.hash(data['password'])
    current_time = datetime.utcnow()
    data['created'] = current_time
    data['updated'] = current_time

    # check for existing user before inserting
    existing_user = mongo.db.users.find_one({
        'email': data['email']
    })
    if existing_user:
        abort(409)

    # insert document. mongo unique index on email property exists as a race condition fail-safe
    user = mongo.db.users.insert_one(data)

    send_email(
        to_email=data['email'],
        subject='Your App Admin Account',
        html_content='''
            <p>Welcome,</p>
            <p>You have successfully created an account for {email} on the App Admin website.</p>
            <p>Here is a link to <a href="{website_domain}/users/login">login</a></p>
            <p>Alternatively, you may paste the following url in your browser: {website_domain}/users/login</p>
            <p>If you did not create an account, please reply to this email and let us know immediately.</p>
            <p>- The {website_name} Team</p>
        '''.format(
            email=data['email'],
            website_domain=os.environ['WEBSITE_DOMAIN'],
            website_name=os.environ['WEBSITE_NAME']
        )
    )

    # return id
    response = jsonify({
        'userId': user.inserted_id
    })
    response.status_code = 201
    return response
