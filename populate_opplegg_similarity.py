from website import create_app, db
from website.models import Opplegg, OppleggSimilarity
from website.utils import compare_opplegg

app = create_app()

# Create the app context
with app.app_context():
    # Get all the Opplegg in the database
    opplegg_list = Opplegg.query.all()

    # Loop through all pairs of Opplegg
    for i, opplegg1 in enumerate(opplegg_list):
        for opplegg2 in opplegg_list[i + 1:]:  # Avoid comparing the same pair twice
            # Check if the similarity entry already exists
            existing_similarity = OppleggSimilarity.query.filter(
                (OppleggSimilarity.opplegg1_id == opplegg1.id) & 
                (OppleggSimilarity.opplegg2_id == opplegg2.id)
            ).first()

            if existing_similarity is None:  # No existing entry, so we calculate and insert
                similarity_score = compare_opplegg(opplegg1.id, opplegg2.id)

                # Only insert if similarity score is valid
                if similarity_score is not None:
                    new_similarity = OppleggSimilarity(
                        opplegg1_id=opplegg1.id,
                        opplegg2_id=opplegg2.id,
                        similarity_score=similarity_score
                    )
                    db.session.add(new_similarity)

    # Commit the changes to the database
    db.session.commit()

    print("Finished populating OppleggSimilarity table.")
