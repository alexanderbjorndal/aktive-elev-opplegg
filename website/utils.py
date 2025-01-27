from .models import Opplegg, Trait, db  
from sqlalchemy.orm import joinedload

def compare_opplegg(opplegg_name):
    """
    Sammenligner opplegget med andre opplegg basert på traits.

    Args:
        opplegg_name (str): Navnet på opplegget som skal sammenlignes.

    Returns:
        list: En liste med opplegg som er sammenlignet, inkludert likhetsscore og felles traits.
    """
    # Hent det nåværende opplegget  
    current_opplegg = Opplegg.query.filter_by(name=opplegg_name).first()
    if not current_opplegg:
        return {"error": f"Opplegg '{opplegg_name}' not found"}, 404

    current_traits = set(trait.id for trait in current_opplegg.traits)

    # Hent alle andre opplegg med traits  
    all_opplegg = Opplegg.query.options(joinedload(Opplegg.traits)).all()
    comparison_results = []

    for opp in all_opplegg:
        if opp.id == current_opplegg.id:
            continue  # Hoppe over seg selv

        opp_traits = set(trait.id for trait in opp.traits)
        similarity = len(current_traits & opp_traits)  # Felles traits  
        total_traits = len(current_traits | opp_traits)  # Totalt traits  
        similarity_score = similarity / total_traits if total_traits > 0 else 0

        comparison_results.append({
            "name": opp.name,
            "similarity_score": similarity_score,
            "common_traits": list(current_traits & opp_traits),
            "date": opp.date,  # Ekstra informasjon  
            "comments_count": len(opp.comments)  # Antall kommentarer  
        })

    # Sorter etter likhetsscore (høyest først)
    comparison_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return comparison_results