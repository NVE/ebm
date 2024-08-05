import typing

from enum import Enum, unique

@unique
class BuildingCondition(Enum):
    SMALL_MEASURE = 1
    RENOVATION = 2
    RENOVATION_AND_SMALL_MEASURE = 3
    DEMOLITION = 4
    ORIGINAL_CONDITION = 5

    def __str__(self):
        return self.name.lower()
    
    @staticmethod
    def get_scruve_condition_list() -> typing.List[str]:
        """
        Retrieves a list with the building conditions used in S-curve calculatons (in lower case). 
        
        Returns:
        - condition_list (list[str]): list of building conditions
        """
        condition_list = [BuildingCondition(value).name.lower() for value in [1,2,4]]
        return condition_list
    
    @staticmethod
    def get_full_condition_list() -> typing.List[str]:
        """
        Retrieves a list with all building conditions (in lower case).
        
        Returns:
        - condition_list (list[str]): list of building conditions 
        """
        condition_list = [condition.name.lower() for condition in iter(BuildingCondition)]
        return condition_list
