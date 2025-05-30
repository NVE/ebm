from ebm.model.building_category import BuildingCategory


START_ROWS_CONSTRUCTION_BUILDING_CATEGORY = {
    BuildingCategory.HOUSE: 11,
    BuildingCategory.APARTMENT_BLOCK: 23,
    BuildingCategory.KINDERGARTEN: 41,
    BuildingCategory.SCHOOL: 55,
    BuildingCategory.UNIVERSITY: 69,
    BuildingCategory.OFFICE: 83,
    BuildingCategory.RETAIL: 97,
    BuildingCategory.HOTEL: 111,
    BuildingCategory.HOSPITAL: 125,
    BuildingCategory.NURSING_HOME: 139,
    BuildingCategory.CULTURE: 153,
    BuildingCategory.SPORTS: 167,
    BuildingCategory.STORAGE: 182
}


def get_building_category_sheet(building_category: BuildingCategory, area_sheet: bool = True) -> str:
    """
    Returns the appropriate sheet name based on the building category and area sheet type.

    Parameters:
    - building_category: An instance of BuildingCategory.
    - area_sheet (bool): Determines whether to return the area sheet ('A') or rates sheet ('R') name. Defaults to True for the area sheet.

    Returns:
    - sheet (str): The sheet name corresponding to the building category and sheet type.
    """
    building_category_sheets = {
        BuildingCategory.HOUSE: ['A hus', 'R hus'],
        BuildingCategory.APARTMENT_BLOCK: ['A leil', 'R leil'],
        BuildingCategory.KINDERGARTEN: ['A bhg', 'R bhg'],
        BuildingCategory.SCHOOL: ['A skole', 'R skole'],
        BuildingCategory.UNIVERSITY: ['A uni', 'R uni'],
        BuildingCategory.OFFICE: ['A kont', 'R kont'],
        BuildingCategory.RETAIL: ['A forr', 'R forr'],
        BuildingCategory.HOTEL: ['A hotell', 'R hotell'],
        BuildingCategory.HOSPITAL: ['A shus', 'R shus'],
        BuildingCategory.NURSING_HOME: ['A shjem', 'R shjem'],
        BuildingCategory.CULTURE: ['A kult', 'R kult'],
        BuildingCategory.SPORTS: ['A idr', 'R idr'],
        BuildingCategory.STORAGE: ['A ind', 'R ind']
    }

    if area_sheet:
        sheet = building_category_sheets[building_category][0]
    else:
        sheet = building_category_sheets[building_category][1]

    return sheet


