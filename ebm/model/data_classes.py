from dataclasses import dataclass

@dataclass
class ScurveParameters:
    building_category: str
    condition: str	
    earliest_age: int
    average_age: int
    rush_years: int	
    last_age: int
    rush_share: float
    never_share: float