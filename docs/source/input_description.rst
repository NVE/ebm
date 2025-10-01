Input files
###########

Each input file is described here in alphabetical order. The heading is the file name, followed by a short description of its contents. Constraints are given in the tab 
formatted box after the descriptions.

Description
===========

.. _area csv:

**area.csv** |br|
Useful floor area in the start year 2020 distributed by building category and building code.

.. _area_new_residential_buildings csv:

**area_new_residential_buildings.csv** |br|
New built useful floor area for residential buildings in 2020 and 2021 from statistics. Statistics source is Statistics Norway.

.. _area_per_person csv:

**area_per_person.csv** |br|
Useful floor area for new non-residential buildings based on population growth.

.. _building_code_parameters csv:

**building_code_parameters.csv** |br|
Year of operation for the different building codes in Norway. New area is built after a new building code a few years after it is implemented.

.. _energy_need_behaviour_factor csv:

**energy_need_behaviour_factor.csv** |br|
Changes in energy need not related to the improvements in heating need from small measures and renovation. 

.. _energy_need_improvements csv:

**energy_need_improvements.csv** |br|
Reduction in energy need for lighting and electrical equipment from implementation of eco design, energy labeling and other measures. 

.. _energy_need_original_condition csv:

**energy_need_original_condition.csv** |br|
Energy need per square meter for various energy purposes differentiated by building code and building category. The given energy need is only for a building's original condition.

.. _heating_system_efficiencies csv:

**heating_system_efficiencies.csv** |br|
Parameters of the various heating technologies. Includes load shares, efficiencies and the related energy product.

.. _heating_system_forecast csv:

**heating_system_forecast.csv** |br|
Defines the rate of change in heating systems towards 2050. The change is made on a percentage basis compared to the start year. Described in more detail here :any:`Forecasting of heating systems`.

.. _heating_system_initial_shares csv:

**heating_system_initial_shares.csv** |br|
Distribution of heating systems per building category and building code in the start year.

.. _holiday_home_energy_consumption csv:

**holiday_home_energy_consumption.csv** |br|
Historical energy use of fuel wood, electricity and fossil fuel in holiday homes.

.. _holiday_home_stock csv:

**holiday_home_stock.csv** |br|
Stock of holiday homes per year from 2001. Statistics from Statistics Norway.

.. _improvement_building_upgrade csv:

**improvement_building_upgrade.csv** |br|
Reduction in heating energy need from completed small measures, renovation and small measures + renovation. Percentage reduction compared to the original condition.

.. _new_buildings_residential csv:

**new_buildings_residential.csv** |br|
Average size of new apartments and houses. Proportion of new homes that are apartments and houses per year.

.. _population_forecast csv:

**population_forecast.csv** |br|
Population forecast from Statistics Norway and average household size.

.. _s_curve csv:

**s_curve.csv** |br|
Parameters to create S-curves. Parameters are given for small measures, renovation and demolition for each building category.


Input constraints
=================
The input constraints, datatypes and accepted values are listed per input file in the respective tabs. Text in orange is the column name.

.. tabs::
   .. tab:: Area
      .. tabs::
         .. tab:: area
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

         .. tab:: area_new_residential_buildings
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

         .. tab:: area_per_person
            ``building_category``
            - required
            - values: kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

            ``area_per_person``
            - required
            - value **≥** 0
            - float using a decimal point ('.') as the separator

         .. tab:: new_buildings_residential
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

            ``floor_area_new_apartment_block``
            - required
            - Integer
            - 0 **≤** value **≤** 1000

   .. tab:: Energy need
      .. tabs::
         .. tab:: energy_need_original_condition
            ``building_category``
            - required
            - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

            ``building_code``
            - required
            - values: Any string containing ``TEK``, 'default' 

            ``purpose``
            - required
            - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling, default'

            ``kwh_m2``
            - required
            - float using a decimal point ('.') as the separator
            - value **≥** 0.0

         .. tab:: improvement_building_upgrade
            ``building_category``
            - required
            - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

            ``building_code``
            - required
            - values: Any string containing ``TEK``, 'default' 

            ``purpose``
            - required
            - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling, default'

            ``condition``
            - required
            - values: original_condition, small_measure, renovation, renovation_and_small_measure, demolition

            ``reduction_share``
            - required
            - float using a decimal point ('.') as the separator
            - **0.0** ≤ value ≤ **1.0**
         
         .. tab:: energy_need_behaviour_factor
            ``building_category``
            - required
            - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

            ``building_code``
            - required
            - values: Any string containing ``TEK``, 'default' 

            ``purpose``
            - required
            - values: 'heating_rv, heating_dhw, fans_and_pumps, lighting, electrical_equipment, cooling, default'

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

         .. tab:: energy_need_improvements
            ``building_category``
            - required
            - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

            ``building_code``
            - required
            - values: Any string containing ``TEK``, 'default' 

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

   .. tab:: Holiday home
      .. tabs::
         .. tab:: holiday_home_stock
            ``year``
            - required
            - integer

            ``Existing buildings Chalet, summerhouses and other holiday houses``
            - required
            - integer

            ``Existing buildings Detached houses and farmhouses used as holiday houses``
            - required
            - integer

         .. tab:: holiday_home_energy_consumption
            ``year``
            - required
            - integer

            ``electricity``
            - integer

            ``fuelwood``
            - integer or empty

            ``fossilfuel``
            - integer or empty

   .. tab:: Heating systems 
      .. tabs::
         .. tab:: heating_system_forecast
            ``building_category``
            - required
            - values: house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs, default, residential, non_residential

            ``building_code``
            - required
            - values: Any string containing ``TEK``, 'default'
            
            ``heating_systems``
            - required
            - string
            - value: 'DH', 'DH - Bio', 'HP Central heating - Bio', 'HP Central heating - Electric boiler', 'HP Central heating - Gas', 'Electric boiler', 'Electric boiler - Solar', 'Gas', 'Electricity', 'Electricity - Bio', 'HP - Bio - Electricity', 'HP - Electricity'
            
            ``new_heating_systems``
            - required
            - string
            - value: 'DH', 'DH - Bio', 'HP Central heating - Bio', 'HP Central heating - Electric boiler', 'HP Central heating - Gas', 'Electric boiler', 'Electric boiler - Solar', 'Gas', 'Electricity', 'Electricity - Bio', 'HP - Bio - Electricity', 'HP - Electricity'

            Year columns: ``2024-2050``
            - required
            - float using a decimal point ('.') as the separator
            - **0** ≤ value ≤ **1**

         .. tab:: heating_system_initial_shares
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
            - value: 'DH', 'DH - Bio', 'HP Central heating - Bio', 'HP Central heating - Electric boiler', 'HP Central heating - Gas', 'Electric boiler', 'Electric boiler - Solar', 'Gas', 'Electricity', 'Electricity - Bio', 'HP - Bio - Electricity', 'HP - Electricity'

            ``heating_system_share``
            - required
            - float
            - float using a decimal point ('.') as the separator
            - **0.0** ≤ value

         .. tab:: heating_system_efficiencies
            ``heating_systems``
            - required
            - string

            ``base_load_energy_product``
            - required
            - string

            ``peak_load_energy_product``
            - required
            - string

            ``tertiary_load_energy_product``
            - required
            - string

            ``tertiary_load_coverage``
            - required
            - float
            - float using a decimal point ('.') as the separator
            - **0.0** ≤ value ≤ **1.0**

            ``"base_load_coverage``
            - required
            - float
            - **0.0** ≤ value ≤ **1.0**

            ``peak_load_coverage``
            - required
            - float
            - **0.0** ≤ value ≤ **1.0**

            ``base_load_efficiency``
            - required
            - float
            - value > **0.0**

            ``peak_load_efficiency``
            - required
            - float
            - value > **0.0**

            ``tertiary_load_efficiency``
            - required
            - float
            - value > **0.0**

            ``domestic_hot_water_energy_product``
            - required
            - string

            ``domestic_hot_water_efficiency``
            - required
            - float
            - value > **0.0**

            ``cooling_efficiency``
            - required
            - float
            - value > **0.0**

   .. tab:: Other
      .. tabs::
         .. tab:: building_code_parameters
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

         .. tab:: population_forecast
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
            - float using a decimal point ('.') as the separator.

         .. tab:: s_curve
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

Use of "default" and categorisation
===================================
When making changes to an input file, for example **energy_need_improvements**, you can use aggregated 
commands instead of specifying each individual *building category*, *building code* and *purpose*. The common aggregated
command is **default**. When **default** is input the model chooses all valid options. For example **default** 
building code means all building codes. 

*Building category* has two additional categories: **residential** and
**non-residental**. **residential** consists of houses and apartment blocks and **non-residential** are the other
building categories. In the input constraint overview these aggregated categories are specified when available. 


.. |br| raw:: html

      <br>

.. |date| date::

Last Updated on |date|.

 Version: |version|.
