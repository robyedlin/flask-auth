import os


ENV = {
    'COOKIE_DOMAIN': os.environ['COOKIE_DOMAIN'],
    'FLASK_ENV': os.environ['FLASK_ENV'],
    'JWT_SECRET_KEY': os.environ['JWT_SECRET_KEY'],
    'MONGO_URI': os.environ['MONGO_URI'],
    'SENDGRID_API_KEY': os.environ['SENDGRID_API_KEY'],
    'SUPPORT_EMAIL': os.environ['SUPPORT_EMAIL'],
    'WEBSITE_DOMAIN': os.environ['WEBSITE_DOMAIN'],
    'WEBSITE_NAME': os.environ['WEBSITE_NAME']
}
