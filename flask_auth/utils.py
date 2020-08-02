import datetime
from jsonschema import validate, FormatChecker
from flask_auth.env import ENV
from flask import abort
from flask.json import JSONEncoder
from flask_pymongo import ObjectId
from flask_jwt_extended import decode_token
import sendgrid


sg = sendgrid.SendGridAPIClient(api_key=ENV['SENDGRID_API_KEY'])


class MongoEngineJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.date):
            return str(obj)
        return JSONEncoder.default(self, obj)


def _epoch_utc_to_datetime(epoch_utc):
    return datetime.datetime.fromtimestamp(epoch_utc)


def add_jwt_to_db(mongo, encoded_token, identity_claim):
    decoded_token = decode_token(encoded_token)
    data = {
        'jti': decoded_token['jti'],
        'tokenType': decoded_token['type'],
        'userIdentity': decoded_token[identity_claim],
        'expires': _epoch_utc_to_datetime(decoded_token['exp']),
        'revoked': False
    }
    mongo.db.jwt.insert_one(data)
    return


def format_email_address(email):
    return email.lower().strip()


def send_email(
    to_email,
    subject,
    html_content,
    from_email=ENV['SUPPORT_EMAIL']
):
    data = {
        'personalizations': [
            {
                'to': [
                    {
                        'email': to_email
                    }
                ],
                'subject': subject
            }
        ],
        'from': {
            'email': from_email
        },
        'content': [
            {
                'type': 'text/html',
                'value': html_content
            }
        ]
    }
    if ENV['FLASK_ENV'] == 'development':
        response = data
        print(response)
    else:
        response = sg.client.mail.send.post(request_body=data)
    return response


def setup_mongo_indexes(mongo):
    # create indexes
    mongo.db.jwt.create_index([('jti', 1)], unique=True)
    mongo.db.users.create_index([('email', 1)], unique=True)


def validate_data(data, schema):
    try:
        validate(instance=data, schema=schema, format_checker=FormatChecker())
        return
    except Exception as e:
        print(e)
        abort(422)
