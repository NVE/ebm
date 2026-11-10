.. |user_case_bc| replace:: ``📁custom-building-categories``


Custom building category
========================

.. admonition:: Endringsforslag

   *custom building categories* som alternativ tittel for å variere språket i menyen. Det sto tidligere *Add new building categories*.

This example demonstrates how to use ``EBM`` scenario functionality by adding a new building building categories. There
are two different types of building categories in ebm with different input file requirements. The difference defines how
ebm will calculate constructed floor area for the building category.

Plan
----

To add a building category to ebm you have to edit a number of files in the subdirectory |user_case_bc|.

 - Add the new building category to the model to |building_category_ref|
 - Add existing area to |area_ref|
 - Define s-curves for the building category in |s_curve_ref|
 - Define energy need for the building category in |energy_need_original_condition_ref|
 - Specify heating system shares in |heating_system_initial_shares_ref|
 - Define heating system transitions in |heating_system_forecast_ref|
 - Define construction for the new building category in one of the following ways:

   + Construction based on area per person in  |area_per_person_ref|
   + Construction based on changes in households in |new_buildings_residential_ref|

The following files contain definitions for building categories and may be updated to include the new building category if deemed necessary:

 - |heating_system_forecast_ref|
 - |improvement_building_upgrade_ref|
 - |energy_need_behaviour_factor_ref|
 - calibration files


Create a new input directory
----------------------------

It is necessary to create a new input directory for EBM. To do this, open your preferred terminal and run the following command:

.. code-block:: bash

   ebm create-input short_analysis_2025 --input=custom-building-categories

.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

       Using data from "custom-building-categories"
       Copy input from C:\dev\ws\Energibruksmodell\ebm\data\short_analysis_2025
       Creating directory custom-building-categories
       Creating missing file  custom-building-categories\building_code_parameters.csv
       Creating missing file  custom-building-categories\s_curve.csv
       Creating missing file  custom-building-categories\population_forecast.csv
       Creating missing file  custom-building-categories\new_buildings_residential.csv
       Creating missing file  custom-building-categories\area_new_residential_buildings.csv
       Creating missing file  custom-building-categories\area.csv
       Creating missing file  custom-building-categories\energy_need_behaviour_factor.csv
       Creating missing file  custom-building-categories\energy_need_original_condition.csv
       Creating missing file  custom-building-categories\improvement_building_upgrade.csv
       Creating missing file  custom-building-categories\energy_need_improvements.csv
       Creating missing file  custom-building-categories\holiday_home_energy_consumption.csv
       Creating missing file  custom-building-categories\holiday_home_stock.csv
       Creating missing file  custom-building-categories\area_per_person.csv
       Creating missing file  custom-building-categories\heating_system_initial_shares.csv
       Creating missing file  custom-building-categories\heating_system_efficiencies.csv
       Creating missing file  custom-building-categories\heating_system_forecast.csv
       Creating missing file  custom-building-categories\building_category.csv
       Creating missing file  custom-building-categories\README.md
       Finished creating input files in custom-building-categories


The input directory is created based on the dataset ``short_analysis_2025``. The new input files will be copied to the subdirectory, |user_case_bc|, as defined by the ``--input`` option.

.. seealso::
    :doc:`Working with input<working_with_input>` for more information on creating and using input directories in EBM.


Update building category listing
--------------------------------

EBM reads building categories from |building_category_ref|.

You also define the group to which each building category belongs. Building group are used to define input for multiple
building categories at once, and for aggragating results.

In this example we will add two new building categories to the model. The residential building category Terraced house, and the non-residential prison.

You can edit |building_category_ref| using a
plain text editor (e.g., Notepad) or spreadsheet software such as Microsoft Excel or LibreOffice Calc.

Add the following lines to |building_category_ref| in  |user_case_bc| to define new building categories and their groups:

.. code-block:: text

   terraced_house,residential
   prison,non_residential

Both ``terraced_house`` and ``prison`` must be present in |building_category_ref|.

When done correctly |building_category_ref| in  |user_case_bc| should look like the example below.

.. tabs::

   .. tab:: Formatted table

        Below is the updated content of |building_category_ref|. The new entries are highlighted in bold.

        .. csv-table:: Complete building_category.csv
           :header: building_category,building_group
           :widths: 15,16

               house,residential
               apartment_block,residential
               **terraced_house**,**residential**
               **prison**,**non_residential**
               kindergarten,non_residential
               school,non_residential
               university,non_residential
               office,non_residential
               retail,non_residential
               hotel,non_residential
               hospital,non_residential
               nursing_home,non_residential
               culture,non_residential
               sports,non_residential
               storage_repairs,non_residential
               holiday_home,holiday_homes


   .. tab:: Raw CSV

        You can add the raw excel content at the end of |building_category_ref| using notepad or a similar text editor.

        .. code-block:: text

            building_category,building_group
            house,residential
            apartment_block,residential
            terraced_house,residential
            prison,non_residential
            kindergarten,non_residential
            school,non_residential
            university,non_residential
            office,non_residential
            retail,non_residential
            hotel,non_residential
            hospital,non_residential
            nursing_home,non_residential
            culture,non_residential
            sports,non_residential
            storage_repairs,non_residential
            holiday_home,holiday_homes


   .. tab:: Download

        Optionally, `Download building_category.csv <../_static/user_case/custom_building_category/building_category.csv>`_ working example.


Define existing floor area
--------------------------

For each building category and building code, you need to define the existing area in |area_ref| in |user_case_bc|. The floor area is defined as m^2 in the column named area.

Both ``terraced_house`` and ``prison`` must be present in |area_ref|.

.. tabs::

   .. tab:: Summary table

        Open *formatted table* and *raw csv* for complete listings

        .. csv-table:: Summary area.csv
           :header: building_category,building_code,area

               apartment_block,PRE_TEK49,12777246
               apartment_block,TEK49,12793316
               …,…,…
               house,TEK10,14011006
               terraced_house,PRE_TEK49,9881650
               terraced_house,TEK49,14238371
               terraced_house,TEK69,15002051
               terraced_house,TEK87,5360923
               terraced_house,TEK97,4832332
               terraced_house,TEK07,1786721
               terraced_house,TEK10,3502751
               prison,PRE_TEK49,198292
               prison,TEK49,276796
               prison,TEK69,296393
               prison,TEK87,134188
               prison,TEK97,285580
               prison,TEK07,57877
               prison,TEK10,126163
               kindergarten,PRE_TEK49,360687
               …,…,…
               storage_repairs,TEK87,2039191
               storage_repairs,TEK97,3081789
               storage_repairs,TEK07,1953926
               storage_repairs,TEK10,3562046


   .. tab:: formatted table

       You should be able to paste the content of this table into |area_ref| when using Excel

        .. csv-table:: Content area.csv
           :file: ../_static/user_case/custom_building_category/area.csv
           :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |area_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/area.csv
           :language: csv



   .. tab:: Download

        Download `area.csv <../_static/user_case/custom_building_category/area.csv>`_ complete with all area.


.. important::

   For this example, we will define area based on a very simple assumption that in no way reflects reality.


Define S-curves
---------------

The new building categories also require s-curve definitions for small_measure, renovation and demolition. S-curves are defined in |s_curve_ref| in |user_case_bc|.

Both ``terraced_house`` and ``prison`` must be present in |s_curve_ref|.

.. tabs::

   .. tab:: Summary table

        Open *formatted table* and *raw csv* for complete listings

        .. csv-table:: Summary s_curve.csv
           :header: building_category,condition,earliest_age_for_measure,average_age_for_measure,rush_period_years,last_age_for_measure,rush_share,never_share

               apartment_block,small_measure,5,20,20,50,0.8,0.1
               apartment_block,renovation,10,30,14,60,0.6,0.15
               apartment_block,demolition,1,90,76,200,0.152,0.798485
               …,…,…,…,…,…,…,…
               terraced_house,small_measure,3,23,30,80,0.8,0.01
               terraced_house,renovation,10,37,24,75,0.65,0.05
               terraced_house,demolition,1,90,76,200,0.20,0.74
               prison,small_measure,5,25,20,50,0.8,0.01
               prison,renovation,15,60,30,100,0.6,0.05
               prison,demolition,50,100,30,130,0.7,0.05
               …,…,…,…,…,…,…,…
               storage_repairs,small_measure,3,20,20,50,0.8,0.01
               storage_repairs,renovation,5,45,40,80,0.7,0.05
               storage_repairs,demolition,50,100,30,130,0.7,0.05

   .. tab:: formatted table

       You should be able to paste the content of this table into |s_curve_ref| when using Excel

        .. csv-table:: Content s_curve.csv
           :file: ../_static/user_case/custom_building_category/s_curve.csv
           :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |s_curve_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/s_curve.csv
           :language: csv

   .. tab:: Download

        Download `s_curve.csv <../_static/user_case/custom_building_category/s_curve.csv>`_ complete with all s-curves.

.. admonition:: Endringsforslag

   Skal det legges inn at det på dette tidspunkt er mulig å kjøre area-forecast med de nye kategoriene? Ulempe er at TEK17
   ikke har nybyggingsareal da dette ikke er definert ennå.


Energy need
-----------

The energy need for each building category, building code and purpose is defined in |energy_need_original_condition_ref| in |user_case_bc|. The energy need is defined as kWh/m^2/year in the column named energy_need.
The file must have definitions for the new building categories.

.. tip::

   When using spreadsheet software, ensure the correct formatting is preserved when saving as CSV.
    - Use comma ``,`` as the delimiter
    - Use full stop ``.`` as the decimal separator

EBM allows multiple building categories and building codes to be defined in a single line by using default, +, and the
residential/non_residential groups. In this example, house and terraced_house are combined using +. The default definition
specifies the most common values, while building codes that differ override those defaults.

Both ``terraced_house`` and ``prison`` must be present in |energy_need_original_condition_ref|.

.. tabs::

   .. tab:: Summary table

        .. csv-table:: Summary energy_need_original_condition.csv
           :header: building_category,building_code,purpose,kwh_m2

            apartment_block,PRE_TEK49,cooling,0
            apartment_block,PRE_TEK49,electrical_equipment,17.52
            apartment_block,PRE_TEK49,fans_and_pumps,0.578888889
            apartment_block,PRE_TEK49,heating_dhw,29.76888889
            apartment_block,PRE_TEK49,heating_rv,126.7397389
            apartment_block,PRE_TEK49,lighting,8.1968
            …,…,…,…
            **terraced_house** +house,default,lighting,8.199
            **terraced_house** +house,default,cooling,0
            **terraced_house** +house,default,electrical_equipment,17.51875
            **terraced_house** +house,default,fans_and_pumps,0.58125
            **terraced_house** +house,default,heating_dhw,29.78125
            **terraced_house** +house,default,heating_rv,155.290712
            **terraced_house** +house,TEK87,heating_rv,123.2885809
            **terraced_house** +house,TEK97,heating_rv,89.65613092
            **terraced_house** +house,TEK07,fans_and_pumps,7.925
            **terraced_house** +house,TEK07,heating_rv,58.72567782
            **terraced_house** +house,TEK10,fans_and_pumps,7.81405
            **terraced_house** +house,TEK10,heating_rv,57.90351833
            **terraced_house** +house,TEK17,fans_and_pumps,6.407521
            **terraced_house** +house,TEK17,heating_rv,47.48088503
            **prison**,default,lighting,18.8
            **prison**,default,cooling,0.0
            **prison**,default,electrical_equipment,5.2
            **prison**,default,fans_and_pumps,34.0
            **prison**,default,heating_dhw,10.0
            **prison**,default,heating_rv,170.4
            **prison**,TEK49,fans_and_pumps,34.0
            **prison**,TEK87,heating_rv,138.9
            **prison**,TEK97,heating_rv,111.4
            **prison**,TEK07,fans_and_pumps,22.9
            **prison**,TEK07,heating_rv,91.6
            **prison**,TEK10+TEK17,fans_and_pumps,22.5
            **prison**,TEK10+TEK17,heating_rv,74.2


   .. tab:: formatted table

       You should be able to paste the content of this table into |energy_need_original_condition_ref| when using Excel

        .. csv-table:: Content energy_need_original_condition.csv
           :file: ../_static/user_case/custom_building_category/energy_need_original_condition.csv
           :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |energy_need_original_condition_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/energy_need_original_condition.csv
           :language: csv


   .. tab:: Download

        Optionally, `Download energy_need_original_condition.csv <../_static/user_case/custom_building_category/energy_need_original_condition.csv>`_ working example.

Specify heating system shares
-----------------------------

|heating_system_initial_shares_ref| define the shares of heating systems across all building categories and building codes.
This file tells ``EBM`` what the share of each heating system is for a given building code. The new building categories must
be added to the file |heating_system_initial_shares_ref| in |user_case_bc|.

Both ``terraced_house`` and ``prison`` must be present in |heating_system_initial_shares_ref|.

.. note::
   As of version 1.2.0, |heating_system_initial_shares_ref| does not support multiple definitions by combining building
   categories and building codes with ``+``. ``default``, ``non_residential``, and ``residential`` will work.


.. tabs::

   .. tab:: Summary table

        .. csv-table:: Summary heating_system_initial_shares.csv
           :header: building_category,building_code,heating_systems,year,heating_system_share

            terraced_house,default,DH,2023,0.0213315113565833
            terraced_house,default,DH - Bio,2023,0.0076580066831269
            terraced_house,default,Electric boiler,2023,0.0256775930931896
            terraced_house,default,Electric boiler - Solar,2023,0.0003008594060781
            terraced_house,default,Electricity,2023,0.0521984906804366
            terraced_house,default,Electricity - Bio,2023,0.2247326376682365
            terraced_house,default,HP - Bio - Electricity,2023,0.5649908788840201
            terraced_house,default,HP - Electricity,2023,0.0992947318980815
            terraced_house,default,HP Central heating - Electric boiler,2023,0.0038152903302471
            prison,default,DH,2023,0.318
            prison,default,Electric boiler,2023,0.06
            prison,default,Electricity,2023,0.071
            prison,default,Electricity - Bio,2023,0.022
            prison,default,Gas,2023,0.002
            prison,default,HP - Electricity,2023,0.163
            prison,default,HP Central heating - Electric boiler,2023,0.364


   .. tab:: formatted table

       You should be able to paste the content of this table into |heating_system_initial_shares.csv| when using Excel

        .. csv-table:: Content heating_system_initial_shares.csv
           :file: ../_static/user_case/custom_building_category/heating_system_initial_shares.csv
           :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |heating_system_initial_shares.csv| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/heating_system_initial_shares.csv
           :language: csv


   .. tab:: Download

        Download `heating_system_initial_shares.csv <../_static/user_case/custom_building_category/heating_system_initial_shares.csv>`_ complete with all heating systems.


Non-residential construction
----------------------------

EBM calculates new construction for non-residential building categories based on area per person. The area per person
is defined in |area_per_person_ref| in |user_case_bc|.

The file must have definitions for the new ``prison`` building category.



.. tabs::

   .. tab:: formatted table

        .. csv-table:: Summary area_per_person.csv
           :header: building_category,area_per_person

            kindergarten,0.6
            retail,6.0
            hotel,1.6
            sports,1.3
            office,5.5
            culture,1.3
            school,2.8
            nursing_home,1.3
            hospital,0.6
            university,0.6
            storage_repairs,3.4
            **prison**,**0.06**

   .. tab:: raw csv

      You can add the raw csv content at the end of |area_per_person_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/area_per_person.csv
           :language: csv


   .. tab:: Download

        Download `area_per_person.csv <../_static/user_case/custom_building_category/area_per_person.csv>`_.


Residential construction
------------------------

Residential require definitions for yearly share of building category and the average floor area of new buildings. These are defined in |new_buildings_residential_ref| and |area_new_residential_buildings_ref| in |user_case_bc|. The files must have definitions for the new ``terraced_house`` building category.

Define avarage floor area and building category share
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Share of new terraced house buildings and average floor area for terraced house are defined in two new columns. The columns must be named *new_terraced_house_share* and *floor_area_new_terraced_house*.

*new_terraced_house_share* is a value between 0.0 and 1.0. The sum of *new_house_share*, *new_terraced_house_share* and *new_apartment_block_share* should be equal to 1.0 for each year. Any positive value will work for *floor_area_new_terraced_house*. The values in the example below are not based on any real data.


.. tabs::

   .. tab:: Summary table

        .. csv-table:: Summary new_buildings_residential.csv
           :header: year,new_house_share,new_terraced_house_share,new_apartment_block_share,floor_area_new_house,floor_area_new_apartment_block,floor_area_new_terraced_house

            2020,0.24,**0.2**,0.56,154,69,**105**
            2021,0.22,**0.21**,0.57,154,69,**105**
            2022,0.23,**0.22**,0.55,154,69,**105**
            2023,0.16,**0.23**,0.61,154,69,**105**
            2024,0.14,**0.23**,0.63,154,69,**105**
            2025,0.21,**0.24**,0.55,154,69,**105**
            2026,0.21,**0.24**,0.55,154,69,**105**
            2027,0.2,**0.24**,0.56,154,69,**105**
            2028,0.2,**0.24**,0.56,154,69,**105**
            2029,0.19,**0.25**,0.56,154,69,**105**
            2030,0.19,**0.25**,0.56,154,69,**105**
            2031,0.19,**0.25**,0.56,154,69,**105**
            2032,0.19,**0.25**,0.56,154,69,**105**
            2033,0.18,**0.25**,0.57,154,69,**105**
            2034,0.18,**0.25**,0.57,154,69,**105**
            2035,0.18,**0.25**,0.57,154,69,**105**
            2036,0.18,**0.25**,0.57,154,69,**105**
            2037,0.18,**0.25**,0.57,154,69,**105**
            2038,0.16,**0.26**,0.58,154,69,**105**
            2039,0.16,**0.26**,0.58,154,69,**105**
            2040,0.16,**0.26**,0.58,154,69,**105**
            2041,0.16,**0.26**,0.58,154,69,**105**
            2042,0.16,**0.26**,0.58,154,69,**105**
            2043,0.15,**0.26**,0.59,154,69,**105**
            2044,0.15,**0.26**,0.59,154,69,**105**
            2045,0.15,**0.26**,0.59,154,69,**105**
            2046,0.15,**0.26**,0.59,154,69,**105**
            2047,0.14,**0.27**,0.59,154,69,**105**
            2048,0.13,**0.27**,0.6,154,69,**105**
            2049,0.13,**0.27**,0.6,154,69,**105**
            2050,0.12,**0.28**,0.6,154,69,**105**

   .. tab:: formatted table

       You should be able to paste the content of this table into |new_buildings_residential_ref| when using Excel

        .. csv-table:: Content new_buildings_residential.csv
           :file: ../_static/user_case/custom_building_category/new_buildings_residential.csv
           :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |new_buildings_residential_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/new_buildings_residential.csv
           :language: csv


   .. tab:: Download

        Download `new_buildings_residential.csv <../_static/user_case/custom_building_category/new_buildings_residential.csv>`_.

Define counstruction in the first two years
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Define construction in the first two years of the model in |area_new_residential_buildings_ref|. The file must have definitions for the new ``terraced_house`` building category.

.. tabs::

   .. tab:: Summary table

        .. csv-table:: Summary area_new_residential_buildings.csv
           :header: year,house,apartment_block,terraced_house

            2020,0.0,0.0,**0.0**
            2021,2186969.198192,1152796.0,**546742.299548**



   .. tab:: formatted table

       You should be able to paste the content of this table into |area_new_residential_buildings_ref| when using Excel

        .. csv-table:: Content area_new_residential_buildings.csv
           :file: ../_static/user_case/custom_building_category/area_new_residential_buildings.csv
           :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |area_new_residential_buildings_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/area_new_residential_buildings.csv
           :language: csv

   .. tab:: Download

      Download `area_new_residential_buildings.csv <../_static/user_case/custom_building_category/area_new_residential_buildings.csv>`_.


Run the model
----------------

Once you have adapted all the input files listed abouve, you can run the model using the following command:

.. code-block:: powershell

   ebm --input=custom-building-categories

.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

       Using data from "custom-building-categories"
       Input directory "custom-building-categories" contains calibration files
       Using YearRange(start=2020, end=2030)
       Area forecast to area
       Wrote output\area.xlsx
       Energy use to energy_purpose
       Heating_system_share
       Wrote output\heating_system_share.xlsx
       heat_prod_hp
       Wrote output\heat_prod_hp.xlsx
       Energy_use
       Wrote output\energy_use.xlsx
       Wrote output\energy_purpose.xlsx
       demolition_construction
       Wrote output\demolition_construction.xlsx


The model results can be found in the subdirectory named |output_directory|.



.. admonition:: Endringsforslag

   Dette begynner å bli langt. Skulle innholdet vært fordelt over flere sider?


Optional input files
--------------------

All the files listed so far must include the new building categories. There are also some input file that you can add
the new building categories to if deemed necessary.


Heating system transitions
^^^^^^^^^^^^^^^^^^^^^^^^^^

Heating system forcast is defined in |heating_system_forecast_ref| in |user_case_bc|. The file should have definitions for
the new terraced_house building category. Prison is already covered by ``non_residential`` and does not need to be added.


.. tabs::

   .. tab:: Summary table

        .. csv-table:: Summary heating_system_forecast.csv
           :header: building_category,building_code,heating_systems,new_heating_systems,2024,…,2030

            terraced_house,default,HP Central heating - Gas,HP Central heating - Electric boiler,0.2,…,1.0
            terraced_house,default,Electricity - Bio,HP - Bio - Electricity,0.03,…,0.24375

   .. tab:: formatted table

      You should be able to paste the content of this table into |heating_system_forecast_ref| when using Excel

      .. csv-table:: Content heating_system_forecast.csv
           :file: ../_static/user_case/custom_building_category/heating_system_forecast.csv
           :header-rows: 1


   .. tab:: raw csv

      You can add the raw csv content at the end of |heating_system_forecast_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/heating_system_forecast.csv
           :language: csv

   .. tab:: Download

      Download `heating_system_forecast.csv <../_static/user_case/custom_building_category/heating_system_forecast.csv>`_.


Building condition improvements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The new building categories are already covered by |improvement_building_upgrade_ref| using the ``default`` building category. There is
no need to add the new building categories to this file unless you want to define specific improvements

.. tabs::

   .. tab:: formatted table

      .. csv-table:: Content improvement_building_upgrade.csv
          :file: ../_static/user_case/custom_building_category/improvement_building_upgrade.csv
          :header-rows: 1



Behaviour factor
^^^^^^^^^^^^^^^^

Behaviour factor already defines values by using ``residential`` and ``non_residential``. Any missing combination of
building category, building code an purpose missing in this file will have the behaviour factor set to ``1.0``.


.. tabs::

   .. tab:: formatted table

      .. csv-table:: Content energy_need_behaviour_factor.csv

         :header: building_category,building_code,purpose,behaviour_factor,start_year,end_year
            residential,default,default,1,2020,
            house,PRE_TEK49+TEK69+TEK87+TEK49+TEK97,default,0.9,2020,
            house,default,lighting,0.85,2020,
            non_residential,default,default,1.06,2020,
            retail,default,electrical_equipment,2,2020,


If you want ``terraced_house`` to have the same behaviour factor as ``house`` you can replace ``house`` with ``house+terraced_house`` in the building_category column of |energy_need_behaviour_factor_ref| in |user_case_bc|. The file should then look like the example below.

.. tabs::

   .. tab:: formatted table

      You should be able to paste the content of this table into |energy_need_behaviour_factor_ref| when using Excel

      .. csv-table:: Content energy_need_behaviour_factor.csv
          :file: ../_static/user_case/custom_building_category/energy_need_behaviour_factor.csv
          :header-rows: 1

   .. tab:: raw csv

      You can add the raw csv content at the end of |energy_need_behaviour_factor_ref| using notepad or a similar text editor.

        .. literalinclude:: ../_static/user_case/custom_building_category/energy_need_behaviour_factor.csv
           :language: csv

   .. tab:: Download

      Download `energy_need_behaviour_factor.csv <../_static/user_case/custom_building_category/energy_need_behaviour_factor.csv>`_.


Calibration files
-----------------

heating_rv
^^^^^^^^^^

The content of ``calibrate_heating_rv.csv`` is the same as the default value of ``1.0`` for all building categories and building codes. If you want to calibrate differently the new building categories, you can add them to the file in |user_case_bc|.

.. tabs::

   .. tab:: formatted table

      .. csv-table:: Content calibrate_heating_rv.csv
          :file: ../_static/user_case/custom_building_category/calibrate_heating_rv.csv
          :header-rows: 1


energy consumption
^^^^^^^^^^^^^^^^^^

If you want ``terraced_house`` to have the same calibration factor as ``house``, you can replace ``house`` with ``house+terraced_house`` in the building_category column of ``calibrate_energy_consumption.csv`` in |user_case_bc|. The file should then look like the example below.

.. tabs::

   .. tab:: Summmary

      .. csv-table:: Content calibrate_heating_rv.csv

         :header: building_category,to,from,factor
            house+terraced_house,Electric boiler,Electricity,1
            house+terraced_house,DH,Electricity - Bio,0.45
            house+terraced_house,Electricity,HP - Bio - Electricity,0.9
            house+terraced_house,Electricity,HP - Electricity,1
            house+terraced_house,Gas,HP - Electricity,1
            house+terraced_house,Electricity - Bio,Electricity,0.81
            house+terraced_house,Electricity - Bio,HP - Electricity,0.75
            house+terraced_house,HP - Bio - Electricity,Electricity - Bio,0.95
            house+terraced_house,DH - Bio,Electricity,1
            house+terraced_house,HP - Bio - Electricity,Electricity,0.98
            house+terraced_house,HP - Electricity,Electricity,1
            house+terraced_house,HP Central heating - Bio,Electric boiler,1
            house+terraced_house,HP Central heating - Electric boiler,Electric boiler,0.5
            house+terraced_house,HP Central heating - Gas,Electric boiler,1
            house+terraced_house,Electric boiler - Solar,Electric boiler,1
            apartment_block,Electric boiler,HP Central heating - Electric boiler,0.4
            …,…,…,…

   .. tab:: formatted table

      .. csv-table:: Content calibrate_energy_consumption.csv
          :file: ../_static/user_case/custom_building_category/calibrate_energy_consumption.csv
          :header-rows: 1

   .. tab:: Download

      Download `calibrate_energy_consumption.csv <../_static/user_case/custom_building_category/calibrate_energy_consumption.csv>`_.

Re-run the model
----------------

.. code-block:: powershell

   ebm --input=custom-building-categories --open


.. tip::
   EBM will open the result automatically when use use the option ``--open``



.. |date| date::

Last Updated on |date|

Version: |version|.
