from types import MappingProxyType

from ebm.model.building_category import BuildingCategory
from ebm.model.building_condition import BuildingCondition

_building_category_order = {BuildingCategory.HOUSE: 1, BuildingCategory.APARTMENT_BLOCK: 2, BuildingCategory.RETAIL: 3,
    BuildingCategory.OFFICE: 4, BuildingCategory.KINDERGARTEN: 5, BuildingCategory.SCHOOL: 6,
    BuildingCategory.UNIVERSITY: 7, BuildingCategory.HOSPITAL: 8, BuildingCategory.NURSING_HOME: 9,
    BuildingCategory.HOTEL: 10, BuildingCategory.SPORTS: 11, BuildingCategory.CULTURE: 12, BuildingCategory.STORAGE: 13}

BUILDING_CATEGORY_ORDER = MappingProxyType(_building_category_order)
"""A immutable dict of BeMa sorting order for building_category"""

_tek_order = {'PRE_TEK49': 1, 'TEK49': 2, 'TEK69': 3, 'TEK87': 4, 'TEK97': 5, 'TEK07': 6, 'TEK10': 7, 'TEK17': 8,
              9: 'TEK21'}

TEK_ORDER = MappingProxyType(_tek_order)
"""A dict of BeMa sorting order for TEK"""

_building_condition_order = {BuildingCondition.ORIGINAL_CONDITION: 1, BuildingCondition.SMALL_MEASURE: 2,
    BuildingCondition.RENOVATION: 3, BuildingCondition.RENOVATION_AND_SMALL_MEASURE: 4, BuildingCondition.DEMOLITION: 5}

BUILDING_CONDITION_ORDER = MappingProxyType(_building_condition_order)
"""A dict of BeMa sorting order for building_condition"""

_start_row_building_category_construction = {BuildingCategory.HOUSE: 11, BuildingCategory.APARTMENT_BLOCK: 23,
    BuildingCategory.KINDERGARTEN: 41, BuildingCategory.SCHOOL: 55, BuildingCategory.UNIVERSITY: 69,
    BuildingCategory.OFFICE: 83, BuildingCategory.RETAIL: 97, BuildingCategory.HOTEL: 111,
    BuildingCategory.HOSPITAL: 125, BuildingCategory.NURSING_HOME: 139, BuildingCategory.CULTURE: 153,
    BuildingCategory.SPORTS: 167, BuildingCategory.STORAGE: 182}

START_ROWS_CONSTRUCTION_BUILDING_CATEGORY = MappingProxyType(_start_row_building_category_construction)
"""A dict of BeMa sorting order for start row of each building category in the sheet `nybygging`"""



def get_building_category_sheet(building_category: BuildingCategory, area_sheet: bool = True) -> str:
    """
    Returns the appropriate sheet name based on the building category and area sheet type.

    Parameters
    ----------
    - building_category: An instance of BuildingCategory.
    - area_sheet (bool): Determines whether to return the area sheet ('A') or rates sheet ('R') name. Defaults to True for the area sheet.

    Returns
    -------
    - sheet (str): The sheet name corresponding to the building category and sheet type.
    """
    building_category_sheets = {BuildingCategory.HOUSE: ['A hus', 'R hus'],
        BuildingCategory.APARTMENT_BLOCK: ['A leil', 'R leil'], BuildingCategory.KINDERGARTEN: ['A bhg', 'R bhg'],
        BuildingCategory.SCHOOL: ['A skole', 'R skole'], BuildingCategory.UNIVERSITY: ['A uni', 'R uni'],
        BuildingCategory.OFFICE: ['A kont', 'R kont'], BuildingCategory.RETAIL: ['A forr', 'R forr'],
        BuildingCategory.HOTEL: ['A hotell', 'R hotell'], BuildingCategory.HOSPITAL: ['A shus', 'R shus'],
        BuildingCategory.NURSING_HOME: ['A shjem', 'R shjem'], BuildingCategory.CULTURE: ['A kult', 'R kult'],
        BuildingCategory.SPORTS: ['A idr', 'R idr'], BuildingCategory.STORAGE: ['A ind', 'R ind']}

    if area_sheet:
        sheet = building_category_sheets[building_category][0]
    else:
        sheet = building_category_sheets[building_category][1]

    return sheet
