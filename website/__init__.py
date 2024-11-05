from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
mail = Mail()  # Initialize the mail object
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '8a7df6oliqwjh5l'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Mail configuration
    #app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
    #app.config['MAIL_PORT'] = 587
    #app.config['MAIL_USERNAME'] = '59e06506963569'
    #app.config['MAIL_PASSWORD'] = '3cf541e7cb072e'
    #app.config['MAIL_USE_TLS'] = True
    #app.config['MAIL_USE_SSL'] = False
    #app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    # Mail configuration
    app.config['MAIL_SERVER']='smtp.mailgun.org'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'postmaster@sandbox4f941c1197764b379d99228a1cca131f.mailgun.org69'
    app.config['MAIL_PASSWORD'] = 'def'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    db.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail with the app

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Opplegg, Trait

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    login_manager.login_message = "Funksjonen du prøvde å bruke krever innlogging."

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Ingen tilgang'}), 403

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print('Created Database!')
