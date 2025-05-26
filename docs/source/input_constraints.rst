Input constraints
=================

.. contents:: Table of Contents
   :depth: 2
   :local:


area_parameters
----------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``TEK``
 - required
 - values: Any string containing ``TEK``

``area``
 - required
 - float using a decimal point ('.') as the separator
 - **≥** 0.0

tek_parameters
--------------

``TEK``
 - required
 - values: Any string containing ``TEK``

``building_year``
 - required
 - integer value
 - **≥** 1940
 - **≤** 2070

``period_start_year``
 - required
 - integer value
 - **≥** 0
 - **≤** 2070
 - < period_end_year
 - = previous period_end_year + 1

``period_end_year``
 - required
 - integer value
 - **≥** 0
 - **≤** 2070
 - > period_start_year
 - = next period_start_year -1

must cover all years within lowest period_start_year to highest period_end_year

construction_building_category_yearly
-------------------------------------

``year``
 - required
 - integer
 - Values outside of model start year and model start year +1 might not be supported (2020, 2021)

``house``
 - required
 - float using a decimal point ('.') as the separator
 - **≥** 0.0

``apartment_block``
 - required
 - float using a decimal point ('.') as the separator
 - **≥** 0.0

new_buildings_house_share
-------------------------

``year``
 - required
 - integer value
 - **≥** 0
 - **≤** 2070

``new_house_share``
 - required
 - float using a decimal point ('.') as the separator
 - **≥** 0.0
 - **≤** 1.0

``new_apartment_block_share``
 - required
 - float using a decimal point ('.') as the separator
 - 0.0 **≤** value **≤** 1.0

``floor_area_new_house``
 - required
 - Integer
 - 0 **≤** value **≤** 1000

``flood_area_new_apartment_block``
 - required
 - Integer
 - 0 **≤** value **≤** 1000

population
----------

``year``
 - required
 - Integer value
 - 1900 **≤** year **≤** 2070

``population``
 - Required
 - Integer value
 - population **≥** 0

``household_size``
 - required
 - value **≥** 0
 - float using a decimal point ('.') as the separator

scurve_parameters
-----------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``condition``
 - required
 - values: original_condition, small_measure, renovation, renovation_and_small_measure, demolition

``earliest_age_for_measure``
 - required
 - value **≥** 0.0

``average_age_for_measure``
 - required
 - value **≥** 0.0

``rush_period_years``
 - required
 - integer
 - value **≥** 0.0

``last_age_for_measure``
 - required
 - integer
 - value **≥** 0.0

``rush_share``
 - required
 - float using a decimal point ('.') as the separator
 - **0.0** < value ≤ **1.0** (not including zero)

``never_share``
 - required
 - float using a decimal point ('.') as the separator
 - **0.0** < value ≤ **1.0** (not including zero)

energy_requirement_original_condition
-------------------------------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``TEK``
 - required
 - values: Any string containing ``TEK``

``purpose``
 - required
 - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling'

``kwh_m2``
 - required
 - float using a decimal point ('.') as the separator
 - value **≥** 0.0

energy_requirement_reduction_per_condition
------------------------------------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``TEK``
 - required
 - values: Any string containing ``TEK``

``purpose``
 - required
 - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling'

``condition``
 - required
 - values: original_condition, small_measure, renovation, renovation_and_small_measure, demolition

``reduction_share``
 - required
 - float using a decimal point ('.') as the separator
 - **0.0** ≤ value ≤ **1.0**

energy_requirement_yearly_improvements
--------------------------------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``TEK``
 - required
 - values: Any string containing ``TEK``

``purpose``
 - required
 - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling'

``yearly_efficiency_improvement``
 - required
 - float using a decimal point ('.') as the separator
 - **0.0** ≤ value ≤ **1.0**

energy_requirement_policy_improvements
--------------------------------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``TEK``
 - required
 - values: Any string containing ``TEK``

``purpose``
 - required
 - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling'

``period_start_year``
 - required
 - integer value
 - value **≥** 0

``period_end_year``
 - required
 - integer value
 - value **≥** 0

``improvement_at_period_end``
 - required
 - float using a decimal point ('.') as the separator
 - **0.0** ≤ value ≤ **1.0**

energy_need_improvements
------------------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

``TEK``
 - required
 - values: Any string containing ``TEK``

``purpose``
 - required
 - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling, default'

``start_year``
 - integer
 - **0** ≤ value ≤ **end_year**
 - default 2020

``function``
 - required
 - values: yearly_reduction, improvement_at_end_year

``value``
 - required
 - float using a decimal point ('.') as the separator
 - **0.0** ≤ value

``end_year``
 - required
 - integer
 - **start_year** ≤ value ≤ **2070**
 - default 2050


holiday_home_by_year
--------------------

``year``
 - required
 - integer

``Existing buildings Chalet, summerhouses and other holiday house``
 - required
 - integer

``Existing buildings Detached houses and farmhouses used as holiday houses``
 - required
 - integer

holiday_home_energy_consumption
-------------------------------

``year``
 - required
 - integer

``electricity``
 - integer

``fuelwood``
 - integer or empty

``fossil``
 - integer or empty

heating_systems_shares_start_year
---------------------------------

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``TEK``
 - required
 - values: Any string containing ``TEK``

``year``
 - required
 - integer

``heating_systems``
 - required
 - string
 - value: 'Electricity', 'Electricity - Bio', 'Electric boiler', 'Electric boiler - Solar', 'Gas', 'DH', 'DH - Bio

.. |date| date::

Last Updated on |date|.

 Version: |version|.