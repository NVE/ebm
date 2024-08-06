import pandas as pd

from loguru import logger

from ebm.model.building_condition import BuildingCondition

# Get condition lists via BuildingCondition class
scurve_condition_list = BuildingCondition.get_scruve_condition_list()
full_condition_list = BuildingCondition.get_full_condition_list()

print(scurve_condition_list)
print(full_condition_list)

l = []
for member in iter(BuildingCondition):
    l.append(member)

print(l)

print(BuildingCondition('SMALL measuRE'))