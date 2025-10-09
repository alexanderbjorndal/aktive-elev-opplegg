# aktive-elev-opplegg

Opplegg for aktive elever

Oppskrift for å gå fra vscode til pythonanywhere
I vs-code terminal:
git add .
git commit
git push

I pythonanywhere bash:
git pull
Deretter reload website

Oppskrift for å oppdatere databasen i PythonAnywhere:
Etter git pull
export FLASK_APP=website
flask db upgrade
For å sjekke om det funket:
sqlite3 instance/database.db
.tables
.exit eller CTRL D

Oppskrift for å endre databasen i PythonAnywhere:
08:34 ~/aktive-elev-opplegg (main)$ python

from website import create_app, db
from website.models import Trait, Opplegg, User # import whichever models you need

app = create_app()
app.app_context().push()

# Get one object by ID

trait = Trait.query.get(37)

# List all traits

traits = Trait.query.all()
for t in traits:
print(t.id, t.name, t.forklaring)

# Filter by column

Trait.query.filter_by(name="Eksamen").all()

# First match only

Trait.query.filter_by(name="Eksamen").first()

# Change a single field

trait = Trait.query.get(37)
trait.forklaring = "Egner seg til eksamenstrening"
db.session.commit()

# Verify change

print(trait.forklaring)

# Add new data

new_trait = Trait(name="Ny egenskap", forklaring="Dette er en test", klasse="ABC")
db.session.add(new_trait)
db.session.commit()

new_trait = Trait(name="Ny egenskap", forklaring="Dette er en test", klasse="ABC")
db.session.add(new_trait)
db.session.commit()

# Delete data

trait = Trait.query.get(50)
db.session.delete(trait)
db.session.commit()

# Relationships

opplegg = Opplegg.query.first()
print(opplegg.name, [t.name for t in opplegg.traits])

# Add a trait to an opplegg

trait = Trait.query.get(37)
opplegg.traits.append(trait)
db.session.commit()

db.session.rollback() # undo uncommitted changes if you made a mistake
db.session.commit() # save changes
