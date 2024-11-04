from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from .models import User
from . import db, mail
from flask_mail import Mail, Message

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
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

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
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'), is_email_confirmed=False)
            db.session.add(new_user)
            db.session.commit()

            # Generate verification token
            token = s.dumps(email, salt='email-confirm')

            # Send verification email
            msg = Message('Vennligst bekreft eposten din', recipients=[email])
            link = url_for('auth.confirm_email', token=token, _external=True)
            msg.body = f'Hei {first_name},<br><br>Velkommen til Opplegg for aktive elever! Ved å bekrefte eposten din får du tilgang til å legge inn nye opplegg samt å lagre favoritter blant oppleggene.<br><br>Klikk på lenken for å bekrefte eposten din: <a href="{link}">Bekreft epost</a><br><br>Takk for at du registrerte deg, og velkommen til vårt fellesskap! <br><br><br><br><br> Mvh. <br> Alexander Bjørndal <br> alexandebj@afk.no'
            msg.html = msg.body  # Set the HTML body
            mail.send(msg)

            flash('Konto opprettet! Sjekk e-posten din for å bekrefte kontoen.', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # Token valid for 1 hour
    except Exception as e:
        flash('Lenken til å bekrefte eposten er ugyldig eller har utløpt', category='error')
        return redirect(url_for('auth.sign_up'))

    user = User.query.filter_by(email=email).first()
    if user:
        user.is_email_confirmed = True  # Update the user's email confirmation status
        db.session.commit()
        flash('E-posten din har blitt bekreftet!', category='success')
        return redirect(url_for('auth.login'))
    else:
        flash('Bruker ikke funnet', category='error')
        return redirect(url_for('auth.sign_up'))
