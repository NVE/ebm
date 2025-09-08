Input
#############################

Each input file is described here. The heading is the file name, followed by a short description of its contents and constraints. Text in orange is the column name.

Input constraints
=================


area
----------------
Useful floor area in the start year 2020 distributed by building category and building code.

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``building_code``
 - required
 - values: Any string containing ``TEK``

``area``
 - required
 - float using a decimal point ('.') as the separator
 - **≥** 0.0

area_new_residential_buildings
-------------------------------------
New useful floor area for residential buildings in 2020 and 2021 from statistics.

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

area_per_person
---------------
Useful floor area for new non-residential buildings based on population growth.

``building_category``
 - required
 - values: kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``area_per_person``
 - required
 - value **≥** 0
 - float using a decimal point ('.') as the separator


building_code
--------------
Year of operation for the different building codes. 

``building_code``
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


new_buildings_residential
-------------------------
Average size of new apartments and houses. Proportion of new homes that are apartments and houses per year. 

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

population_forecast
----------
Population forecast from Statistics Norway and average household size.

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

s_curve
-----------------
Parameters to create S-curves. Parameters are given for small measures, renovation and demolition for each building category.

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

energy_need_original_condition
-------------------------------------
Energy need per square meter for various energy purposes differentiated by building code and building category. The given energy need is only for a buildings
original purpose. 

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``building_code``
 - required
 - values: Any string containing ``TEK``

``purpose``
 - required
 - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling'

``kwh_m2``
 - required
 - float using a decimal point ('.') as the separator
 - value **≥** 0.0

improvment_building_upgrade
----------------------------
Reduction in heating energy need from completed small measures, renovation and small measures + renovation. Percentage reduction compared to the original condition. 

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``building_code``
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

energy_need_behaviour_factor
--------------------------------------
Changes in energy need not related to the improvements in heating need from the s-curves. 

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``building_code``
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
Reduction in lighting and equipment energy need from implementation of ecodesign.

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

``building_code``
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


.. csv-table:: input/energy_need_improvements.csv
   :file: ../../ebm/data/energy_need_improvements.csv
   :header-rows: 1



holiday_home_stock
--------------------
Stock of holiday homes per year from 2001. Statistics from Statistics Norway. 

``year``
 - required
 - integer

``Existing buildings Chalet, summerhouses and other holiday houses``
 - required
 - integer

``Existing buildings Detached houses and farmhouses used as holiday houses``
 - required
 - integer

holiday_home_energy_consumption
-------------------------------
Historical energy use of fuel wood, electricity and fossil fuel in holiday homes.


``year``
 - required
 - integer

``electricity``
 - integer

``fuelwood``
 - integer or empty

``fossilfuel``
 - integer or empty

heating_system_forecast
-----------------------
Defines the rate of change in heating systems towards 2050. The change is made on a percentage basis compared with the start year.


heating_system_initial_shares
---------------------------------
Distribution of heating systems per building category and building code in the start year.

``building_category``
 - required
 - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

``building_code``
 - required
 - values: Any string containing ``TEK``

``year``
 - required
 - integer

``heating_systems``
 - required
 - string
 - value: 'Electricity', 'Electricity - Bio', 'Electric boiler', 'Electric boiler - Solar', 'Gas', 'DH', 'DH - Bio'

 ``heating_system_share``
 - required
 - float
 - float using a decimal point ('.') as the separator
 - **0.0** ≤ value

heating_systems_efficiencies
----------------------------
Parameters of the various heating technologies. Includes load shares, efficiencies and the related energy product.

``heating_systems``
 - required
 - string

``Grunnlast``
 - required
 - string

``Spisslast``
 - required
 - string

``Ekstralast``
 - required
 - string

``Grunnlast energivare``
 - required
 - string

``Spisslast energivare``
 - required
 - string

``Ekstralast energivare``
 - required
 - string

``Ekstralast andel``
 - required
 - float
 - float using a decimal point ('.') as the separator
 - **0.0** ≤ value ≤ **1.0**

``Grunnlast andel``
 - required
 - float
 - **0.0** ≤ value ≤ **1.0**

``Spisslast andel``
 - required
 - float
 - **0.0** ≤ value ≤ **1.0**

``Grunnlast virkningsgrad``
 - required
 - float
 - value > **0.0**

``Spisslast virkningsgrad``
 - required
 - float
 - value > **0.0**

``Ekstralast virkningsgrad``
 - required
 - float
 - value > **0.0**

``Tappevann``
 - required
 - string

``Tappevann energivare``
 - required
 - string

``Tappevann virkningsgrad``
 - required
 - float
 - value > **0.0**

``Spesifikt elforbruk``
 - required
 - float

``Kjoling virkningsgrad``
 - required
 - float
 - value > **0.0**

.. |date| date::

Last Updated on |date|.

 Version: |version|.
