from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from .models import User
from . import db
import os
from dotenv import load_dotenv

load_dotenv()
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if not user.is_email_confirmed:
                flash('Vennligst bekreft eposten din før du logger inn.', category='error')
                return redirect(url_for('auth.login'))
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logget inn!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Feil passord, prøv igjen.', category='error')
        else:
            flash('Eposten finnes ikke i systemet.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

s = URLSafeTimedSerializer('Nesbru144')  # Replace with your secret key

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        one_time_password = request.form.get('one_time_password')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        one_time_password_from_env = os.environ.get('ONE_TIME_PASSWORD')
        print(one_time_password_from_env)
        
        if not one_time_password:
            raise ValueError("One time password must be set in environment variables.")

        user = User.query.filter_by(email=email).first()
        if user:
            flash('En bruker med denne eposten finnes allerede.', category='error')
        elif len(email) < 4:
            flash('Eposten må inneholde flere enn tre tegn.', category='error')
        elif len(first_name) < 2:
            flash('Navn må ha flere enn ett tegn.', category='error')
        elif password1 != password2:
            flash('Passordene er ikke like.', category='error')
        elif len(password1) < 5:
            flash('Passordet må inneholde minst fem tegn.', category='error')
        elif one_time_password != one_time_password_from_env:
            flash('Engangspassordet stemmer ikke, ta kontakt på alexandebj@afk.no for å få nytt engangspassord.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'), is_email_confirmed=True)
            db.session.add(new_user)
            db.session.commit()

            flash('Konto opprettet!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
