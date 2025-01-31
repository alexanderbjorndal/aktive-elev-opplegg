# website/utils.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from website import db
from website.models import Opplegg, Trait, OppleggSimilarity
import nltk
from nltk.corpus import stopwords

# Make sure to download the stopwords first if you haven't already
nltk.download('stopwords')

# Load Norwegian stopwords from nltk
norwegian_stop_words = stopwords.words('norwegian')
vectorizer = TfidfVectorizer(stop_words=norwegian_stop_words)


# Function to calculate text similarity using TF-IDF
def get_text_similarity(data1, data2):
    tfidf_matrix = vectorizer.fit_transform([data1, data2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

def get_trait_similarity(opplegg1, opplegg2):
    # Get all the traits of both opplegg
    traits1 = {trait.name for trait in opplegg1.traits}
    traits2 = {trait.name for trait in opplegg2.traits}
    
    # Calculate trait similarity (only count if both have the trait)
    common_traits = traits1.intersection(traits2)
    
    # Return a similarity score based on how many common traits they share
    trait_score = len(common_traits) / max(len(traits1), len(traits2)) if max(len(traits1), len(traits2)) > 0 else 0
    
    return trait_score  # Return the numeric score based on common traits


def compare_opplegg(opplegg1_id, opplegg2_id):
    # Get the Opplegg objects
    opplegg1 = Opplegg.query.get(opplegg1_id)
    opplegg2 = Opplegg.query.get(opplegg2_id)
    
    if not opplegg1 or not opplegg2:
        return None  # Either opplegg does not exist
    
    # Calculate text similarity
    text_similarity = get_text_similarity(opplegg1.data, opplegg2.data)
    
    # Calculate trait similarity
    trait_similarity = get_trait_similarity(opplegg1, opplegg2)
    
    # Combine the two scores with weights
    final_similarity = 0.2 * text_similarity + 0.8 * trait_similarity
    
    return final_similarity


def get_similar_opplegg(opplegg_id):
    # Get the Opplegg object corresponding to the given opplegg_id
    opplegg = Opplegg.query.get(opplegg_id)

    if not opplegg:
        return None  # If the opplegg doesn't exist

    similarities = OppleggSimilarity.query.filter(
        (OppleggSimilarity.opplegg1_id == opplegg_id) |
        (OppleggSimilarity.opplegg2_id == opplegg_id)
    ).order_by(OppleggSimilarity.similarity_score.desc()).limit(3).all()

    similar_opplegg = []
    for similarity in similarities:
        # Get the other Opplegg object based on which opplegg_id is the current one
        other_opplegg_id = similarity.opplegg2_id if similarity.opplegg1_id == opplegg_id else similarity.opplegg1_id
        other_opplegg = Opplegg.query.get(other_opplegg_id)
        
        if other_opplegg:
            # Get common traits for the two Opplegg
            common_traits = get_trait_similarity(opplegg, other_opplegg)  # Pass the correct opplegg

            similar_opplegg.append({
                "id": other_opplegg.id,
                "name": other_opplegg.name,
                "data": other_opplegg.data,
                "similarity_score": similarity.similarity_score,
                "common_traits": common_traits,  # Dynamically filled with real common traits
            })

    return similar_opplegg

