import random
import copy
from typing import Dict, Tuple, Any
from .state import EnvironmentState, RestaurantState, VerificationStatus
from .actions import Action

_singleton_instance = None

def get_env(seed: int = 42) -> 'FoodSafetyEnv':
    """Global factory function to access the shared environment singleton."""
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = FoodSafetyEnv(seed=seed)
    return _singleton_instance

class FoodSafetyEnv:
    _instantiated = False

    def __init__(self, seed: int = 42):
        if FoodSafetyEnv._instantiated:
            print(f"CRITICAL ERROR [ENV {id(self)}]: MULTIPLE ENV INSTANCES DETECTED")
            raise RuntimeError("MULTIPLE ENV INSTANCES DETECTED: Illegal constructor call outside of get_env()")
        
        FoodSafetyEnv._instantiated = True
        self._state: RestaurantState = self._initial_default_state()
        self.step_count = 0
        self.max_steps = 10
        self.total_reward = 0.000001
        self.is_done = False
        self.history = []
        self.seed = seed
        random.seed(seed)
        print(f"DEBUG [ENV {id(self)}]: Singleton instance initialized")

    def _initial_default_state(self) -> RestaurantState:
        # Realistic initial state to avoid "Loading..." placeholders
        return RestaurantState(
            restaurant_id="#GB-START-01",
            restaurant_name="Obsidian Sentinel Hub",
            description="Monitoring live food safety intelligence across Bengaluru...",
            hygiene_score=100.0,
            inspection_age_days=0,
            complaints_count=0,
            order_volume=0,
            verification_status=VerificationStatus.VERIFIED,
            badge_visible=False,
            flagged=False,
            user_trust=100.0
        )

    def reset(self, initial_state: RestaurantState = None) -> Dict[str, Any]:
        if initial_state:
            self._state = copy.deepcopy(initial_state)
        else:
            self._state = self._initial_default_state()
            
        self.step_count = 0
        self.total_reward = 0.000001
        self.is_done = False
        self.history = []
        
        print(f"STATE UPDATED (RESET) [ENV {id(self)}]: {self._state.restaurant_name}")
        return self._get_obs()

    def _get_obs(self) -> Dict[str, Any]:
        """ALWAYS returns a nested 'restaurant' object for frontend consistency."""
        return {"restaurant": self._state.model_dump()}

    def state(self) -> Dict[str, Any]:
        """Direct exposure of the current unified state."""
        return self._get_obs()

    def step(self, action: Action) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if self.is_done:
            # Clamp even the early finish reward
            return self._get_obs(), 0.000001, True, {"info": {"reason": "Episode already finished.", "expected_action": "N/A"}}

        self.step_count += 1
        self.history.append(action.value)

        reward, info_dict = self._calculate_reward(action)
        self.total_reward += reward
        
        # Apply the action effects directly to self.state
        self._apply_action(action)
        
        if self.step_count >= self.max_steps:
            self.is_done = True

        print(f"STATE UPDATED (STEP) [ENV {id(self)}]: Action={action.value}, State={self._state.restaurant_name}")
        return self._get_obs(), reward, self.is_done, {"info": info_dict}

    def _update_trust(self, delta: float):
        self._state.user_trust = max(0.0, min(100.0, self._state.user_trust + delta))

    def _apply_action(self, action: Action):
        if action == Action.SHOW_BADGE:
            self._state.badge_visible = True
            self._state.flagged = False
        elif action == Action.HIDE_INFO:
            self._state.badge_visible = False
        elif action == Action.REQUEST_INSPECTION:
            # Multi-step dependency: Revealed hidden risk
            if self._state.is_hidden_risk:
                self._state.hygiene_score = 45.0 # Revealed true low score
                self._state.is_hidden_risk = False
            self._state.inspection_age_days = 0 
            self._state.complaints_count = max(0, self._state.complaints_count - 1)
        elif action == Action.FLAG_RESTAURANT:
            self._state.flagged = True
            self._state.badge_visible = False

    def _calculate_reward(self, action: Action) -> Tuple[float, Dict[str, str]]:
        """Bounded reward [0.0, 1.0] with tiered logic and explainability."""
        res = self._state
        tier = 0.4 # Default Neutral
        reason = "Neutral action taken."
        expected = "unknown"

        # Check for High Risk
        # True risk = (visible hygiene < 70) OR (is_hidden_risk AND high complaints)
        is_risky = res.hygiene_score < 70.0 or res.complaints_count > 10 or res.is_hidden_risk
        is_very_safe = res.hygiene_score > 90.0 and res.complaints_count == 0 and not res.is_hidden_risk

        if action == Action.FLAG_RESTAURANT:
            if is_risky:
                tier = 0.99
                reason = "Correctly flagged a high-risk restaurant, protecting public health."
                expected = "flag_restaurant"
                self._update_trust(5.0)
            else:
                tier = 0.01
                reason = "Falsely flagged a safe restaurant, causing unfair economic harm."
                expected = "show_safety_badge"
                self._update_trust(-15.0)
        
        elif action == Action.SHOW_BADGE:
            if is_very_safe:
                tier = 0.99
                reason = "Promoted a high-standard, verified restaurant. Boosts user trust."
                expected = "show_safety_badge"
                self._update_trust(10.0)
            elif is_risky:
                tier = 0.01
                reason = "DANGEROUS: Displayed safety badge for a restaurant with safety hazards."
                expected = "flag_restaurant" if not res.is_hidden_risk else "request_inspection"
                self._update_trust(-25.0)
            else:
                tier = 0.7
                reason = "Reasonable to show badge, but minor concerns exist."
                expected = "show_safety_badge"
                self._update_trust(2.0)

        elif action == Action.REQUEST_INSPECTION:
            if res.is_hidden_risk or res.inspection_age_days > 180:
                tier = 0.99
                reason = "Pre-emptive investigation of stale or suspicious data is optimal."
                expected = "request_inspection"
                self._update_trust(5.0)
            elif res.inspection_age_days < 30:
                tier = 0.01
                reason = "Wasteful: Requested inspection for very recent, high-quality data."
                expected = "show_safety_badge"
                self._update_trust(-2.0)
            else:
                tier = 0.7
                reason = "Reasonable to refresh data, even if not extremely old."
                expected = "request_inspection"

        elif action == Action.HIDE_INFO:
            if is_risky:
                tier = 0.7
                reason = "Cautious choice to hide info on risky restaurant, but flagging is better."
                expected = "flag_restaurant"
                self._update_trust(-2.0)
            elif is_very_safe:
                tier = 0.01
                reason = "Failure of transparency: Hiding information for a very safe restaurant."
                expected = "show_safety_badge"
                self._update_trust(-10.0)

        # Clamp reward to be strictly between 0 and 1 (exclusive) for validator compliance
        epsilon = 0.01
        final_reward = max(epsilon, min(1.0 - epsilon, float(tier)))
        return final_reward, {"reason": reason, "expected_action": expected}
