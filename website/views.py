from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import event
from .models import Opplegg, Trait, User, Comment, Visitor
from .utils import get_similar_opplegg, compare_virtual_opplegg
from website.utils import update_opplegg_similarity
from . import db
import os
from collections import defaultdict
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home():
    # Fetch all opplegg, users, traits, and comments
    opplegg = Opplegg.query.all()
    users = User.query.all()
    traits = Trait.query.all()
    user_list = []

    # Create a list of users for easy lookup
    for u in users:
        user_list.append([u.id, u.first_name])

    # Group traits by klasse (assuming each trait has a 'klasse' attribute)
    klasse_groups = defaultdict(list)
    for trait in traits:
        klasse_groups[trait.klasse].append(trait)

    # Create a dictionary of opplegg ids with their respective comment count
    opplegg_comment_counts = {
        opplegget.id: Comment.query.filter_by(opplegg_id=opplegget.id).count()
        for opplegget in opplegg
    }

    # Create a dictionary of opplegg ids with the count of users who favorited it
    opplegg_favorites_counts = {
        opplegget.id: len([user for user in users if opplegget in user.favorites])
        for opplegget in opplegg
    }

    # Precompute comments text for each opplegg
    for o in opplegg:
        o.comments_text = ', '.join(getattr(c, 'content') for c in o.comments if getattr(c, 'content'))

    # Then pass to render_template
    return render_template(
        "home.html",
        user=current_user,
        users=user_list,
        all_opplegg=opplegg,
        traits=traits,
        klasse_groups=klasse_groups,
        opplegg_comment_counts=opplegg_comment_counts,
        opplegg_favorites_counts=opplegg_favorites_counts,
    )

@views.route('/add-opplegg', methods=['GET', 'POST'])
@login_required
def add_opplegg():
    traits = Trait.query.all()
    klasse_groups = defaultdict(list)
    for trait in traits:
        klasse_groups[trait.klasse].append(trait)

    if request.method == 'POST':
        name = request.form.get('opplegg')
        data = request.form.get('data')
        marked = []
        if len(data) < 1:
            flash('For kort beskrivelse', category='error')
        else:
            new_name = Opplegg(name=name, data=data ,user_id=current_user.id)
            db.session.add(new_name)  # add first!
            for mark in request.form.getlist('tags'):
                if mark:
                    new_trait = db.session.query(Trait).filter_by(name=mark).first()
                    if new_trait:
                        new_name.traits.append(new_trait)
            db.session.add(new_name)
            if any(trait is None for trait in new_name.traits):
                print(new_name.traits)
                raise ValueError("Opplegget må klassifiseres med minst en egenskap.")
            else:
                db.session.commit()
                flash('Opplegg lagt til', category='success')

                # Update the similarity for the new opplegg
                update_opplegg_similarity(new_name)

        return redirect(url_for('views.home'))

    return render_template("add_opplegg.html", user=current_user, klasse_groups=klasse_groups)

@views.route('/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite():
    opplegg_id = request.form.get('opplegg_id')
    favorite = request.form.get('favorite') == 'true'

    opplegg = Opplegg.query.get(opplegg_id)
    if not opplegg:
        flash('Opplegg ikke funnet.', category='error')
        return redirect(url_for('views.home'))

    if favorite:
        current_user.favorites.remove(opplegg)
    else:
        current_user.favorites.append(opplegg)

    db.session.commit()
    return redirect(url_for('views.home'))

@views.route('/se-opplegg', methods=['GET', 'POST'])
def se_opplegg():
    # Handle displaying the opplegg and comments
    opplegg_id = request.args.get('opplegg_id')  # Get the query parameter
    if not opplegg_id:
        return "Missing opplegg_id", 400  # Handle case where opplegg_id is not provided

    opplegg = Opplegg.query.get_or_404(opplegg_id)  # Get the opplegg details
    users = User.query.all()  # Get all users for displaying author info
    traits = Trait.query.all()  # Get all traits for classifying opplegg
    comments = Comment.query.filter_by(opplegg_id=opplegg_id).all()  # Get all comments for this opplegg

    # Prepare a list of users to display the user names
    user_list = []
    for u in users:
        user_list.append([u.id, u.first_name])

    # Organize traits by class
    klasse_groups = defaultdict(list)
    for trait in traits:
        klasse_groups[trait.klasse].append(trait)

    checked_trait_ids = {trait.id for trait in opplegg.traits}

    # Handle new comment submission
    if request.method == 'POST' and 'content' in request.form:
        # If the "content" field is present, we assume this is a comment submission
        content = request.form.get('content')
        if content:
            new_comment = Comment(content=content, opplegg_id=opplegg_id, user_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added!', category='success')
            return redirect(url_for('views.se_opplegg', opplegg_id=opplegg_id))  # Refresh the page

    # Handle form submission to update opplegg
    if request.method == 'POST' and 'opplegg' in request.form:
        # If the "opplegg" field is present, we assume this is the form for updating the opplegg
        if current_user.role != 'admin':
            abort(403)

        name = request.form.get('opplegg')
        data = request.form.get('data')
        marked = []
        if len(data) < 1:
            flash('For kort', category='error')
        else:
            # Update the existing Opplegg
            opplegg.name = name
            opplegg.data = data
            opplegg.traits.clear()  # Clear existing traits before adding new ones
            
            # Add the newly selected traits
            for mark in request.form.getlist('tags'):
                if mark:
                    new_trait = db.session.query(Trait).filter_by(name=mark).first()
                    if new_trait:
                        opplegg.traits.append(new_trait)

            # Ensure that at least one trait is selected
            if not opplegg.traits:
                flash('Opplegget må klassifiseres med minst en egenskap.', category='error')
                db.session.rollback()  # Rollback in case of error
            else:
                db.session.commit()  # Commit changes to the database
                flash('Opplegg oppdatert', category='success')
        
        return redirect(url_for('views.home'))

    # Render the page with opplegg, users, traits, and comments
    return render_template(
        'se_opplegg.html',
        opplegg=opplegg,
        user=current_user,
        klasse_groups=klasse_groups,
        checked_trait_ids=checked_trait_ids,
        comments=comments,  # Pass comments to the template
        user_list=user_list
    )

@views.route('/compare', methods=['GET', 'POST'])
def compare_opplegg():
    opplegg_id = request.args.get('opplegg_id')
    
    # Query the Opplegg table for the opplegg based on the ID
    opplegg = Opplegg.query.filter_by(id=opplegg_id).first()

    if not opplegg:
        return jsonify({"error": "Opplegg not found"}), 404

    # Call the utility function to get similar opplegg (now including ids)
    similar_opplegg = get_similar_opplegg(opplegg.id)

    return jsonify(similar_opplegg)

@views.route('/live-compare', methods=['POST'])
@login_required
def live_compare():
    data = request.json
    name = data.get("name", "")
    description = data.get("description", "")
    selected_traits = data.get("traits", [])

    # Turn trait names into Trait objects
    traits = Trait.query.filter(Trait.name.in_(selected_traits)).all()

    # Construct a "virtual opplegg" (not saved in DB)
    virtual_opplegg = Opplegg(name=name, data=description)
    virtual_opplegg.traits = traits

    # Compare against all existing opplegg
    results = []
    with db.session.no_autoflush:
        for opplegg in Opplegg.query.all():
            score = compare_virtual_opplegg(virtual_opplegg, opplegg)
            results.append({
                "id": opplegg.id,
                "name": opplegg.name,
                "data": opplegg.data[:150] + "..." if len(opplegg.data) > 150 else opplegg.data,
                "similarity_score": score
            })

    # Sort by similarity and return top 3
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return jsonify(results[:3])

@views.before_app_request
def track_visitor():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        visitor = Visitor.query.filter_by(ip=ip).first()
        if visitor:
            visitor.last_seen = datetime.now()
        else:
            db.session.add(Visitor(ip=ip))
        db.session.commit()

@event.listens_for(User.__table__, 'after_create')
def create_admin_user(*args, **kwargs):
    admin_user = User.query.filter_by(email=os.environ.get('ADMIN_EMAIL')).first()
    if admin_user is None:
        # Get admin email and password from environment variables
        admin_email = os.getenv('ADMIN_MAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            raise ValueError("Admin email and password must be set in environment variables.")
        
        # Create a new admin user with secure details
        new_user = User(
            email=admin_email,
            first_name='Alexander Bjørndal',
            role='admin', 
            password=generate_password_hash(admin_password, method='pbkdf2:sha256'),
            is_email_confirmed=True
        )

        db.session.add(new_user)
        db.session.commit()
        print(f"Admin user {admin_email} created successfully.")
    else:
        print(f"Admin user {admin_user.email} already exists.")


@event.listens_for(Trait.__table__, 'after_create')
def create_traits(*args, **kwargs):
    db.session.add(Trait(name='Vurdering', klasse='Type', forklaring='Opplegget passer til å vurdere kompetanse')) 
    db.session.add(Trait(name='Fysisk', klasse='Type', forklaring='Elevene må være tilstede på skolen'))
    db.session.add(Trait(name='Digitalt', klasse='Type', forklaring='Elevene kan være på Teams'))
    db.session.add(Trait(name='Hjemmearbeid', klasse='Type', forklaring='Egner seg som lekse'))
    db.session.add(Trait(name='Lek/Spill', klasse='Type', forklaring='Er en lek eller ett spill'))
    db.session.add(Trait(name='Tverrfagelig', klasse='Type', forklaring='Passer til å kombinere fag'))
    db.session.add(Trait(name='Lærerstyrt', klasse='Type', forklaring='Styres av læreren'))
    db.session.add(Trait(name='Elevstyrt', klasse='Type', forklaring='Styres av elevene'))

    db.session.add(Trait(name='Individuelt', klasse='Antall elever', forklaring='Elevene jobber en og en'))
    db.session.add(Trait(name='Par', klasse='Antall elever', forklaring='Elevene jobber i par'))
    db.session.add(Trait(name='Liten gruppe', klasse='Antall elever', forklaring='Elevene jobber i små grupper'))
    db.session.add(Trait(name='Stor gruppe', klasse='Antall elever', forklaring='Elevene jobber i store grupper'))
    db.session.add(Trait(name='Flere klasser', klasse='Antall elever', forklaring='Opplegget egner seg til flere klasser som har undervisning sammen'))

    db.session.add(Trait(name='-10 min', klasse='Tid', forklaring='Opplegget tar under 10 minutter'))
    db.session.add(Trait(name='10-30 min', klasse='Tid', forklaring='Opplegget tar mellom 10 og 30 minutter'))
    db.session.add(Trait(name='30-90 min', klasse='Tid', forklaring='Opplegget tar mellom 30 og 90 minutter'))
    db.session.add(Trait(name='90+ min', klasse='Tid', forklaring='Opplegget tar over 90 minutter'))

    db.session.add(Trait(name='Klasserom', klasse='Sted', forklaring='Kan gjøres i klasserommet'))
    db.session.add(Trait(name='Hjemme', klasse='Sted', forklaring='Kan gjøres hjemme'))
    db.session.add(Trait(name='Ute', klasse='Sted', forklaring='Kan gjøres ute'))
    db.session.add(Trait(name='Fellesareal', klasse='Sted', forklaring='Kan gjøres i fellesareal'))
    db.session.add(Trait(name='Gymsal', klasse='Sted', forklaring='Kan gjøres i gymsal'))

    db.session.add(Trait(name='PC', klasse='Trenger', forklaring='Elevene/lærer trenger PC/Mac'))
    db.session.add(Trait(name='Mobil', klasse='Trenger', forklaring='Elevene/lærer må ha mobiltelefon'))
    db.session.add(Trait(name='Internett', klasse='Trenger', forklaring='Elevene/lærer må ha internett'))
    db.session.add(Trait(name='Utskrift', klasse='Trenger', forklaring='Opplegget krever utskrift på forhånd eller underveis'))
    db.session.add(Trait(name='Smartskjerm', klasse='Trenger', forklaring='Opplegget krever smartskjerm'))
    db.session.add(Trait(name='Innkjøp', klasse='Trenger', forklaring='Lærer må kjøpe inn noe på forhånd'))
    db.session.add(Trait(name='Forberedelser', klasse='Trenger', forklaring='Læreren må forberede noe (spørsmål, oppgaver, grupper eller annet)'))

    db.session.add(Trait(name='Bli kjent', klasse='Hensikt', forklaring='Opplegget passer til å bli kjent'))
    db.session.add(Trait(name='Roe ned', klasse='Hensikt', forklaring='Opplegget passer til å roe ned elevene'))
    db.session.add(Trait(name='Aktivere', klasse='Hensikt', forklaring='Opplegget passer for å aktivisere elevene'))
    db.session.add(Trait(name='Utforske', klasse='Hensikt', forklaring='Elevene får utforsket i opplegget'))
    db.session.add(Trait(name='Kritisk tenkning', klasse='Hensikt', forklaring='Elevene må tenke kristisk i dette opplegget'))
    db.session.add(Trait(name='Oppstart', klasse='Hensikt', forklaring='Opplegget egner seg til oppstart av timen eller tema'))
    db.session.add(Trait(name='Oppsummere', klasse='Hensikt', forklaring='Opplegget egner seg til oppsummering av timen eller tema'))
    db.session.add(Trait(name='Eksamen', klasse='Hensikt', forklaring='Egner seg til eksamenstrening'))

    db.session.commit()
