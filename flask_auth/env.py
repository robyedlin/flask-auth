import os


ENV = {
    'COOKIE_DOMAIN': os.environ['COOKIE_DOMAIN'],
    'DB_NAME': os.environ['DB_NAME'],
    'FLASK_ENV': os.environ['FLASK_ENV'],
    'JWT_SECRET_KEY': os.environ['JWT_SECRET_KEY'],
    'MONGO_URI': os.environ['MONGO_URI'],
    'SENDGRID_API_KEY': os.environ['SENDGRID_API_KEY'],
    'SUPPORT_EMAIL': os.environ['SUPPORT_EMAIL'],
    'WEBSITE_URL': os.environ['WEBSITE_URL'],
    'WEBSITE_NAME': os.environ['WEBSITE_NAME']
}
