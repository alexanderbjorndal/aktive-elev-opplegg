# website/utils.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from website import db
from website.models import Opplegg, Trait, OppleggSimilarity

# Keep vectorizer uninitialized until we need it
vectorizer = None

def get_vectorizer():
    global vectorizer
    if vectorizer is None:
        # Import nltk lazily to avoid dependency during migrations
        import nltk
        from nltk.corpus import stopwords

        try:
            norwegian_stop_words = stopwords.words('norwegian')
        except LookupError:
            nltk.download('stopwords')
            norwegian_stop_words = stopwords.words('norwegian')

        vectorizer = TfidfVectorizer(stop_words=norwegian_stop_words)
    return vectorizer


def get_text_similarity(data1, data2):
    vec = get_vectorizer()
    tfidf_matrix = vec.fit_transform([data1, data2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]


def get_trait_similarity(opplegg1, opplegg2):
    # Use trait names or IDs to avoid object identity issues
    traits1 = {trait.name for trait in getattr(opplegg1, "traits", [])}
    traits2 = {trait.name for trait in getattr(opplegg2, "traits", [])}
    if not traits1 and not traits2:
        return 0
    common_traits = traits1.intersection(traits2)
    trait_score = len(common_traits) / max(len(traits1), len(traits2))
    return trait_score



def compare_opplegg(opplegg1_id, opplegg2_id):
    opplegg1 = Opplegg.query.get(opplegg1_id)
    opplegg2 = Opplegg.query.get(opplegg2_id)
    if not opplegg1 or not opplegg2:
        return None

    text_similarity = get_text_similarity(opplegg1.data, opplegg2.data)
    trait_similarity = get_trait_similarity(opplegg1, opplegg2)
    final_similarity = 0.2 * text_similarity + 0.8 * trait_similarity
    return final_similarity


def update_opplegg_similarity(new_opplegg):
    opplegg_list = Opplegg.query.all()
    for opplegg in opplegg_list:
        if opplegg.id == new_opplegg.id:
            continue

        existing_similarity = OppleggSimilarity.query.filter(
            (OppleggSimilarity.opplegg1_id == opplegg.id) &
            (OppleggSimilarity.opplegg2_id == new_opplegg.id)
        ).first()

        if existing_similarity is None:
            similarity_score = compare_opplegg(opplegg.id, new_opplegg.id)
            if similarity_score is not None:
                new_similarity = OppleggSimilarity(
                    opplegg1_id=opplegg.id,
                    opplegg2_id=new_opplegg.id,
                    similarity_score=similarity_score
                )
                db.session.add(new_similarity)

    db.session.commit()
    print(f"Similarity scores updated for {new_opplegg.name}")


def get_similar_opplegg(opplegg_id):
    opplegg = Opplegg.query.get(opplegg_id)
    if not opplegg:
        return None

    # Get all similarities for this opplegg
    similarities = OppleggSimilarity.query.filter(
        (OppleggSimilarity.opplegg1_id == opplegg_id) |
        (OppleggSimilarity.opplegg2_id == opplegg_id)
    ).all()

    similar_opplegg = []
    for similarity in similarities:
        other_id = similarity.opplegg2_id if similarity.opplegg1_id == opplegg_id else similarity.opplegg1_id
        other = Opplegg.query.get(other_id)
        if other:
            common_traits = get_trait_similarity(opplegg, other)
            similar_opplegg.append({
                "id": other.id,
                "name": other.name,
                "data": other.data,
                "similarity_score": similarity.similarity_score,
                "common_traits": common_traits,
            })

    # Sort in Python to ensure ordering is correct
    similar_opplegg.sort(key=lambda x: x['similarity_score'], reverse=True)

    # Return top 3
    return similar_opplegg[:3]

def compare_virtual_opplegg(virtual_opplegg, existing_opplegg):
    """
    Compare a not-yet-saved opplegg (virtual) with an existing one.
    """
    text_similarity = get_text_similarity(virtual_opplegg.data, existing_opplegg.data)
    trait_similarity = get_trait_similarity(virtual_opplegg, existing_opplegg)
    final_similarity = 0.2 * text_similarity + 0.8 * trait_similarity
    return final_similarity
