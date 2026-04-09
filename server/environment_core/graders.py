from typing import List, Dict, Any

def grade_easy(trajectory: List[Dict[str, Any]]) -> float:
    """Easy task: Obvious safe restaurant. Reward based on whether they showed the badge."""
    score = 0
    for step in trajectory:
        if step["action"] == "show_safety_badge":
            score = 1 # Optimal action
            break
    # Penalize if they flagged a safe restaurant
    for step in trajectory:
        if step["action"] == "flag_restaurant":
            score = 0
    return score

def grade_medium(trajectory: List[Dict[str, Any]]) -> float:
    """Medium task: Borderline/Stale. Reward based on requesting inspection BEFORE showing badge."""
    requested = False
    return 1 if requested else 0

def grade_hard(trajectory: List[Dict[str, Any]]) -> float:
    """Hard task: Trap Hygiene. 
    MUST request_inspection (reveals hygiene 45.0) THEN flag_restaurant.
    """
    revealed = False
    flagged = False
    
    for step in trajectory:
        action = step["action"]
        current_hygiene = step["state"]["hygiene_score"]
        
        if action == "request_inspection":
            revealed = True
        
        if action == "flag_restaurant":
            if revealed:
                flagged = True
            else:
                return 0 
        
        if action == "show_safety_badge":
            return 0

    if revealed and flagged:
        return 1
    if revealed and not flagged:
        return 0 
        
    return 0

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
