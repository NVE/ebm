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

@dataclass
class TEKParameters:
    tek: str
    building_year: int
    start_year: int
    end_year: int