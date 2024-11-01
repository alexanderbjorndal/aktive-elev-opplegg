from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import event
from .models import Opplegg, Trait, User
from . import db
import json
from collections import defaultdict

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():
    opplegg = Opplegg.query.all()
    users = User.query.all()
    traits = Trait.query.all()
    user_list = []

    for u in users:
        user_list.append([u.id, u.first_name])

    klasse_groups = defaultdict(list)
    for trait in traits:
        klasse_groups[trait.klasse].append(trait)

    return render_template("home.html", user=current_user, users=user_list, all_opplegg=opplegg, traits=traits, klasse_groups=klasse_groups)

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
            flash('For kort', category='error')
        else:
            new_name = Opplegg(name=name, data=data ,user_id=current_user.id)
            for mark in request.form.getlist('tag'):
                if mark:
                    new_trait = db.session.query(Trait).filter_by(name=mark).first()
                    new_name.traits.append(new_trait)
            db.session.add(new_name)
            if any(trait is None for trait in new_name.traits):
                print(new_name.traits)
                raise ValueError("Traits collection cannot contain None values.")
            else:
                db.session.commit()
            flash('Opplegg lagt til', category='success')
            opplegg = Opplegg.query.all()
            users = User.query.all()
            traits = Trait.query.all()
            user_list = []

            for u in users:
                user_list.append([u.id, u.first_name])

            klasse_groups = defaultdict(list)
            for trait in traits:
                klasse_groups[trait.klasse].append(trait)
        return redirect(url_for('views.home'))
    return render_template("add_opplegg.html", user=current_user, klasse_groups=klasse_groups)

@views.route('/delete-opplegg', methods=['POST'])
@login_required
def delete_opplegg():
    if current_user.role != 'Admin':
        abort(403) 

    opplegg = json.loads(request.data)
    oppleggId = opplegg['oppleggId']
    opplegg = Opplegg.query.get(oppleggId)
    if opplegg:
        db.session.delete(opplegg)
        db.session.commit()
    return jsonify({})

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

@event.listens_for(User.__table__, 'after_create')
def create_users(*args, **kwargs):
    new_user = User(email='admin@adminmail.nimda', first_name='Alexander Bjørndal', role = 'Admin', password=generate_password_hash('nimdaadmin', method='pbkdf2:sha256'))
    db.session.add(new_user)
    db.session.commit()

@event.listens_for(Trait.__table__, 'after_create')
def create_traits(*args, **kwargs):
    db.session.add(Trait(name='Vurdering', klasse='Type'))
    db.session.add(Trait(name='Fysisk', klasse='Type'))
    db.session.add(Trait(name='Digitalt', klasse='Type'))
    db.session.add(Trait(name='Forbredelser', klasse='Type'))
    db.session.add(Trait(name='Hjemmearbeid', klasse='Type'))
    db.session.add(Trait(name='Lek', klasse='Type'))
    db.session.add(Trait(name='Spill', klasse='Type'))
    db.session.add(Trait(name='Tverrfagelig', klasse='Type'))
    db.session.add(Trait(name='Lærerstyrt', klasse='Type'))
    db.session.add(Trait(name='Uten lærer', klasse='Type'))

    db.session.add(Trait(name='Individuelt', klasse='Antall elever'))
    db.session.add(Trait(name='Par', klasse='Antall elever'))
    db.session.add(Trait(name='Liten gruppe', klasse='Antall elever'))
    db.session.add(Trait(name='Stor gruppe', klasse='Antall elever'))
    db.session.add(Trait(name='Flere klasser', klasse='Antall elever'))

    db.session.add(Trait(name='-10 min', klasse='Tid'))
    db.session.add(Trait(name='10-30 min', klasse='Tid'))
    db.session.add(Trait(name='30-90 min', klasse='Tid'))
    db.session.add(Trait(name='90+ min', klasse='Tid'))

    db.session.add(Trait(name='Klasserom', klasse='Sted'))
    db.session.add(Trait(name='Hjemme', klasse='Sted'))
    db.session.add(Trait(name='Ute', klasse='Sted'))
    db.session.add(Trait(name='Fellesareal', klasse='Sted'))
    db.session.add(Trait(name='Gymsal', klasse='Sted'))

    db.session.add(Trait(name='PC', klasse='Trenger'))
    db.session.add(Trait(name='Mobil', klasse='Trenger'))
    db.session.add(Trait(name='Internett', klasse='Trenger'))
    db.session.add(Trait(name='Printing', klasse='Trenger'))
    db.session.add(Trait(name='Smartskjerm', klasse='Trenger'))
    db.session.add(Trait(name='Innkjøp', klasse='Trenger'))

    db.session.add(Trait(name='Bli kjent', klasse='Hensikt'))
    db.session.add(Trait(name='Roe ned', klasse='Hensikt'))
    db.session.add(Trait(name='Aktivere', klasse='Hensikt'))
    db.session.add(Trait(name='Utforske', klasse='Hensikt'))
    db.session.add(Trait(name='Kritisk tenkning', klasse='Hensikt'))
    db.session.add(Trait(name='Oppstart', klasse='Hensikt'))
    db.session.add(Trait(name='Oppsummering', klasse='Hensikt'))
    db.session.add(Trait(name='Eksamen', klasse='Hensikt'))

    db.session.commit()