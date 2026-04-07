from enum import Enum

class Action(str, Enum):
    SHOW_BADGE = "show_safety_badge"
    HIDE_INFO = "hide_info"
    REQUEST_INSPECTION = "request_inspection"
    FLAG_RESTAURANT = "flag_restaurant"
