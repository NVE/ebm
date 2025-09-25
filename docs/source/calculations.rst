:orphan:

Calculations/methods
====================


Forecasting of area
-------------------
New area in the model is added in two ways. Either by replacing demolished area or by building new area. When area is replaced by demolishion
the total amount of area does not change, but it gets updated to the newest building code standard. Demolishion is controlled by the s-curve. 
When constructing new area the total amount of area grows.The model has two different methods for forecasting area newly built area. 
One method for residental area and another for non-residental area. 

Non-residental area
^^^^^^^^^^^^^^^^^^^
Population growth is the driver for new area in non-residential buildings. If the population growth is 0 then the total area is held constant.
We assume that each person requires a specific amount of area from the various non-residental building categories. This is a constant factor calculated
by taking the total non-residental building area per category and dividing it by the population. 
The total area in a given year is the sum of the area in the previous year minus the demolished amount the previous year plus new construction. 

.. math::

    \text{Total area} (\text{year } x) = &\text{ total area} (\text{year } x-1) \\
                          &- \text{demolished area} (\text{year } x-1) \\
                          &+ \text{new construction} (\text{year } x)

Where new construction is calculated the following way:

.. math::

    \text{New construction} (\text{year } x) = &\text{ total area} (\text{year } x) \\ 
                          &- \text{total area} (\text{year } x-1) \\
                          &+ \text{new construction} (\text{year } x-1)

Combining the two:

.. math::

    \text{New construction} (\text{year } x) = &\text{ area/person} \times \text{population} (\text{year } x) \\
                          &-\text{area/person} \times \text{population} (\text{year } x-1) \\
                          &+ \text{ demolished}(\text{year }x-1)

The area per person is different for each of the non-residental building categories. It can also change from year to year, but currently it is a constant. 

.. csv-table:: Area per person per non-residential building category
  :file: tables\area_per_person.csv
  :widths: 40, 20
  :header-rows: 1

Residential area
^^^^^^^^^^^^^^^^
New construction in residential area is based on population, but with some key differences compared to the non-residential area. Instead of forecasting square-meters per person 
as is done in non-residential area, we first have to calculate the required number of new dwellings. Number of new new dwellings is calculated from the "population_forecast" input file which contains 
both the popluation forecast and average household size. The new dwellings can be either apartments or houses and the ratio between them, and the area per dwelling, is given 
in the input file "new_buildings_residential".  


Calibration
------------
To get a good starting point the model needs to be calibrated. The starting point is either energy use per energy carrier 
in a given year from temperature corrected statistics or a constructed year based on statistics. The calibration is based
on the `Norwegian energy balance <https://www.ssb.no/statbank/table/11561/>`_ published by Statistics Norway. The energy 
balance contains yearly consumption numbers per energy carrier on households and private and public services, 
including military. 

What is calibrated?
^^^^^^^^^^^^^^^^^^^^
Calibration is done through an input file called "Kalibreringsark.xlsx" and "energy_requirement_original_condition". 
"energy_requirement_original_condition" contains a column called "behaviour_factor". The factor modifies the 
corresponding energy requirement as given by a specific TEK and building category. It is also possible to modify the
factors given in "heating_system_efficiencies" to fine tune the coverage of various heating technologies and their
efficiencies. 
In the excel file "Kalibreringsark.xlsx" you can adjust various factors which can modify the following:

* Change one heating system for another.
* Energy need for space heating and hot tap water.
* Energy need for lighting and other electrical equipment.

When the model is run the excel file updates without having to close the file. 


Energy need
-----------




.. |br| raw:: html

      <br>

.. |date| date::

Last Updated on |date|.

Version: |version|.
