from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    SUSPENDED = "suspended"

class RestaurantState(BaseModel):
    restaurant_id: str = ""
    restaurant_name: str = ""
    description: str = ""
    hygiene_score: float = Field(default=0.0, ge=0.0, le=100.0)
    inspection_age_days: int = Field(default=0, ge=0)
    complaints_count: int = Field(default=0, ge=0)
    order_volume: int = Field(default=0, ge=0)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    badge_visible: bool = False
    flagged: bool = False
    
    # Advanced metrics
    user_trust: float = Field(default=50.0, ge=0.0, le=100.0)
    is_hidden_risk: bool = False # Used for the "Trap Hygiene" scenario

class EnvironmentState(BaseModel):
    restaurant: RestaurantState
    step_count: int = 0
    max_steps: int = 10
    total_reward: float = 0.0
    is_done: bool = False
    history: List[str] = []
