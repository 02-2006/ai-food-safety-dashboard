import random
from typing import Dict, List, Any
from .state import RestaurantState, VerificationStatus

BENGALURU_PROFILES = [
    {"name": "CTR Malleshwaram", "desc": "Famous for its crisp Benne Masala Dosa, CTR is a Bangalore legacy since the 1920s."},
    {"name": "Vidyarthi Bhavan", "desc": "An iconic heritage restaurant in Gandhi Bazaar known for its historic ambiance and dosa."},
    {"name": "Empire Restaurant Indiranagar", "desc": "A late-night staple in Bangalore, famous for its ghee rice and kebabs."},
    {"name": "Meghana Foods Koramangala", "desc": "Renowned for its spicy Andhra-style biryani and massive student following."},
    {"name": "Rameshwaram Cafe Rajajinagar", "desc": "A high-volume, quick-service eatery specializing in traditional South Indian tiffin."},
    {"name": "Truffles Bangalore", "desc": "The go-to spot for burgers and continental comfort food in the city's heart."},
    {"name": "Corner House Ice Cream", "desc": "A local legend famous for the 'Death by Chocolate' sundae."},
    {"name": "MTR Lalbagh", "desc": "Mavalli Tiffin Rooms, the pioneer of Rava Idli, representing authentic Brahmin cuisine."},
    {"name": "Byg Brewski Brewing Company", "desc": "One of Asia's largest microbreweries, known for its open-air seating and craft beers."},
    {"name": "Sri Sagar (CTR)", "desc": "The local favorite in Malleshwaram, maintaining consistency for generations."}
]

def _get_random_profile():
    return random.choice(BENGALURU_PROFILES)

def get_easy_task() -> RestaurantState:
    profile = _get_random_profile()
    return RestaurantState(
        restaurant_id=f"#GB-{random.randint(1000, 9999)}-X",
        restaurant_name=profile["name"],
        description=profile["desc"],
        hygiene_score=98.0,
        inspection_age_days=5,
        complaints_count=0,
        order_volume=500,
        verification_status=VerificationStatus.VERIFIED,
        badge_visible=False,
        flagged=False,
        user_trust=95.0,
        is_hidden_risk=False
    )

def get_medium_task() -> RestaurantState:
    profile = _get_random_profile()
    return RestaurantState(
        restaurant_id=f"#GB-{random.randint(1000, 9999)}-M",
        restaurant_name=profile["name"],
        description=profile["desc"],
        hygiene_score=85.0,
        inspection_age_days=400,
        complaints_count=1,
        order_volume=1200,
        verification_status=VerificationStatus.PENDING,
        badge_visible=False,
        flagged=False,
        user_trust=65.0,
        is_hidden_risk=False
    )

def get_hard_task() -> RestaurantState:
    profile = _get_random_profile()
    return RestaurantState(
        restaurant_id=f"#GB-{random.randint(1000, 9999)}-H",
        restaurant_name=profile["name"],
        description=profile["desc"],
        hygiene_score=95.0,
        inspection_age_days=300,
        complaints_count=22,
        order_volume=8000,
        verification_status=VerificationStatus.VERIFIED,
        badge_visible=False,
        flagged=False,
        is_hidden_risk=True,
        user_trust=40.0
    )

TASKS = {
    "easy": get_easy_task,
    "medium": get_medium_task,
    "hard": get_hard_task
}
