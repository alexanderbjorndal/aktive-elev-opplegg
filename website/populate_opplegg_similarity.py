# populate_opplegg_similarity.py
from website import create_app, db
from website.models import Opplegg, OppleggSimilarity
from website.utils import compare_opplegg

app = create_app()

# Initialize the app context
with app.app_context():
    # Get all Opplegg from the database
    opplegg_list = Opplegg.query.all()
    
    # Loop through each pair of Opplegg (no self-comparison)
    for i in range(len(opplegg_list)):
        for j in range(i + 1, len(opplegg_list)):  # j starts from i + 1 to avoid repeating comparisons
            opplegg1 = opplegg_list[i]
            opplegg2 = opplegg_list[j]

            # Calculate similarity score using the compare_opplegg function
            similarity_score = compare_opplegg(opplegg1.id, opplegg2.id)

            # If similarity_score is None or very low, you may choose not to insert it
            if similarity_score is not None and similarity_score > 0:
                # Insert the similarity into the OppleggSimilarity table
                opplegg_similarity = OppleggSimilarity(
                    opplegg1_id=opplegg1.id,
                    opplegg2_id=opplegg2.id,
                    similarity_score=similarity_score
                )
                db.session.add(opplegg_similarity)

    # Commit all the changes to the database
    db.session.commit()

    print("OppleggSimilarity table has been populated successfully!")
