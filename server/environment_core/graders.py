from typing import List, Dict, Any

def grade_easy(trajectory: List[Dict[str, Any]]) -> float:
    """Easy task: Obvious safe restaurant. Reward based on whether they showed the badge."""
    score = 0.01
    for step in trajectory:
        if step["action"] == "show_safety_badge":
            score = 0.99 # Optimal action
            break
    # Penalize if they flagged a safe restaurant
    for step in trajectory:
        if step["action"] == "flag_restaurant":
            score = 0.01
    return score

def grade_medium(trajectory: List[Dict[str, Any]]) -> float:
    """Medium task: Borderline/Stale. Reward based on requesting inspection BEFORE showing badge."""
    requested = False
    reward_sum = 0.01
    
    for step in trajectory:
        if step["action"] == "request_inspection":
            requested = True
        
        # If they showed badge before requesting, penalize
        if step["action"] == "show_safety_badge" and not requested:
            return 0.2 # Dangerous decision with stale info
        
        # If they flags unnecessarily
        if step["action"] == "flag_restaurant":
            return 0.1 # Unnecessary harm to business
            
    return 0.99 if requested else 0.3

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
                # Flagging without investigation is good, but not optimal because the 
                # agent didn't "know" it was 100% bad based on hygiene data yet.
                # However, high complaints might justify it. Let's give partial credit.
                return 0.7 
        
        if action == "show_safety_badge":
            # Showing badge on a trap (even before reveal) is catastrophic.
            return 0.01

    if revealed and flagged:
        return 0.99
    if revealed and not flagged:
        return 0.4 # Investigated but didn't act correctly
        
    return 0.01

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}
