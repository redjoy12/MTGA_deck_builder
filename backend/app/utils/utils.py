from collections import Counter
from typing import List
from backend.app.models.schemas import DeckBase, DeckStatistics


def calculate_deck_statistics(deck: DeckBase) -> DeckStatistics:
    """
    Calculates deck statistics like average CMC, color distribution, and mana curve.

    Args:
        deck (DeckBase): The deck object for which to calculate the statistics.

    Returns:
        DeckStatistics: A DeckStatistics object containing the calculated statistics.
    """
    all_cards = deck.main_deck + deck.lands
    total_cards = len(all_cards)

    # Calculate average CMC (excluding lands)
    non_land_cards = [card for card in deck.main_deck if 'Land' not in card.type_line]
    avg_cmc = sum(card.cmc * card.quantity for card in non_land_cards) / sum(card.quantity for card in non_land_cards)

    # Distributions and curve calculations
    color_dist, type_dist, role_dist, curve, mana_sources = Counter(), Counter(), Counter(), Counter(), Counter()

    for card in all_cards:
        for color in card.colors:
            color_dist[color] += 1 / total_cards
        type_dist[card.type_line] += card.quantity
        role_dist[card.role.value] += card.quantity
        if card.mana_cost:
            curve[int(card.mana_cost.total)] += card.quantity

    # Land distribution by color
    mana_sources.update(deck.lands)

    return DeckStatistics(
        average_cmc=avg_cmc,
        color_distribution=dict(color_dist),
        type_distribution=dict(type_dist),
        role_distribution=dict(role_dist),
        mana_sources_by_color=dict(mana_sources),
        curve=dict(curve)
    )

def validate_mana_base(deck: DeckBase) -> List[str]:
    """
    Validates the mana base of a deck, checking for sufficient mana sources.

    Args:
        deck (DeckBase): The deck object to be validated.

    Returns:
        List[str]: A list of validation issues, if any.
    """
    issues = []
    stats = calculate_deck_statistics(deck)
    
    # Check color requirements
    for color, percentage in stats.color_distribution.items():
        required_sources = max(20 * percentage, 14 * percentage)  # Basic heuristic
        if stats.mana_sources_by_color.get(color, 0) < required_sources:
            issues.append(f"Insufficient {color} mana sources")
    
    # Check total lands
    total_lands = len(deck.lands)
    if total_lands < 20:
        issues.append("Too few lands")
    elif total_lands > 28:
        issues.append("Too many lands")
    
    return issues