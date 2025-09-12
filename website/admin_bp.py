from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import Opplegg, Trait, User, Comment, ApprovedEmail
from . import db
import json
import random, string
from urllib.parse import quote

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route('/admin', methods=['GET'])
@login_required
def admin():
    if current_user.role != 'admin':
        abort(403)

    # Example analytics queries
    total_users = User.query.count()
    total_opplegg = Opplegg.query.count()

    # Most common traits
    from sqlalchemy import func
    trait_counts = (
        db.session.query(Trait.name, func.count(Opplegg.id))
        .join(Opplegg.traits)
        .group_by(Trait.name)
        .order_by(func.count(Opplegg.id).desc())
        .all()
    )

    # Optionally: last logins if you have a login history table
    # last_logins = LoginHistory.query.order_by(LoginHistory.timestamp.desc()).limit(10).all()

    return render_template(
        'admin/admin.html',
        total_users=total_users,
        total_opplegg=total_opplegg,
        trait_counts=trait_counts,
        user=current_user
        # last_logins=last_logins
    )


@admin_bp.route('/add-bruker', methods=['GET', 'POST'])
@login_required
def add_bruker():
    if current_user.role != 'admin':
        flash("Du har ikke tilgang til denne siden.", category="error")
        abort(403)

    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("Du må skrive inn en e-post.", category="error")
        else:
            existing = ApprovedEmail.query.filter_by(email=email).first()
            if existing:
                flash("Denne e-posten er allerede i listen.", category="error")
            else:
                new_email = ApprovedEmail(email=email)
                db.session.add(new_email)
                db.session.commit()
                flash("E-posten ble lagt til i listen over godkjente brukere.", category="success")
        return redirect(url_for('admin.add_bruker'))

    # Get all approved emails and check if each has a user
    approved_emails = ApprovedEmail.query.all()
    email_status = []
    for approved in approved_emails:
        user = User.query.filter_by(email=approved.email).first()
        email_status.append({
            "id": approved.id,
            "email": approved.email,
            "is_used": user is not None,
            "user_name": user.first_name if user else None
        })

    return render_template("admin/add_bruker.html", user=current_user, email_status=email_status)

@admin_bp.route('/delete-approved-email/<int:approved_id>', methods=['POST'])
@login_required
def delete_approved_email(approved_id):
    if current_user.role != 'admin':
        flash("Du har ikke tilgang til denne funksjonen.", category="error")
        abort(403)

    approved = ApprovedEmail.query.get_or_404(approved_id)
    db.session.delete(approved)
    db.session.commit()
    flash(f"E-posten {approved.email} ble slettet fra listen.", category="success")
    return redirect(url_for('admin.add_bruker'))


@admin_bp.route('/delete-opplegg', methods=['POST'])
@login_required
def delete_opplegg():
    if current_user.role != 'admin':
        abort(403) 

    opplegg = json.loads(request.data)
    oppleggId = opplegg['oppleggId']
    opplegg = Opplegg.query.get(oppleggId)
    if opplegg:
        Comment.query.filter_by(opplegg_id=opplegg.id).delete()
        db.session.delete(opplegg)
        db.session.commit()
    return jsonify({})

@admin_bp.route("/reset-password/<int:user_id>")
@login_required
def reset_password(user_id):
    if current_user.role != 'admin':
        flash("Du har ikke tilgang til admin-siden.", category="error")
        abort(403)

    user = User.query.get(user_id)
    if not user:
        flash("Bruker ikke funnet.", category="error")
        return redirect(url_for("admin.list_users"))

    # Generate temporary password
    temp_password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    user.password = generate_password_hash(temp_password, method="pbkdf2:sha256")
    user.is_temp_password = True
    db.session.commit()

    # Prepare mailto link
    body_text = (
        f"Hei {user.first_name}!\n\n"
        "Ditt passord på nettsiden Opplegg for aktive elever er tilbakestilt. Her er ditt midlertidige passord:\n\n"
        f"{temp_password}\n\n"
        "Vennligst logg inn på https://alexandebj.pythonanywhere.com/login med dette passordet og endre det til et selvvalgt passord.\n\n"
        "Mvh\nAlexander Bjørndal"
    )
    mailto_link = f"mailto:{user.email}?subject=Tilbakestilling%20av%20passord&body={quote(body_text)}"

    return redirect(mailto_link)

@admin_bp.route('/delete-comment', methods=['POST'])
def delete_comment():
    if current_user.role != 'admin':
        abort(403)  # Only admins can delete comments

    comment_id = request.form.get('comment_id')  # Get the comment ID from the form
    opplegg_id = request.form.get('opplegg_id')  # Get the opplegg ID (optional, for redirect)

    # Fetch the comment to be deleted
    comment = Comment.query.get(comment_id)
    
    if comment:
        # Delete the comment from the database
        db.session.delete(comment)
        db.session.commit()
        flash('Kommentar slettet', category='success')
    else:
        flash('Kommentar ikke funnet', category='error')

    # Redirect back to the opplegg page
    return redirect(url_for('views.se_opplegg', opplegg_id=opplegg_id))


@admin_bp.route('/brukere', methods=['GET'])
@login_required
def brukere():
    # Ensure the current user is an admin
    if current_user.role != 'admin':
        abort(403)  # Forbidden access if the user is not an admin
    
    # Get all users from the database
    users = User.query.all()

    # Fetch opplegg and favorites for each user (with relationships)
    user_data = []
    for user in users:
        user_opplegg = user.opplegg  # All opplegg linked to the user
        user_favorites = user.favorites  # All favorites linked to the user
        user_data.append({
            'user': user,
            'opplegg': user_opplegg,
            'favorites': user_favorites
        })
    
    return render_template('admin/brukere.html', user=current_user, user_data=user_data)

@admin_bp.route("/admin-users")
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash("Du har ikke tilgang til admin-siden.", category="error")
        abort(403)

    users = User.query.all()


    # Get temp password info from query parameters (optional)
    temp_password_user_id = request.args.get("temp_password_user_id", type=int)
    temp_password = request.args.get("temp_password", default="")

    return render_template(
        "admin/admin_users.html",
        users=users,
        temp_password_user_id=temp_password_user_id,
        temp_password=temp_password,
        user=current_user
    )