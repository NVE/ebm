Methods
=======

The total area in the model changes due to demolition and building of new area. New area in the model is added in two ways: 

* New area replaces demolished area 
* New area is built due to changes in population


New area replaces demolished area
---------------------------------

When new area is replacing demolished area the total amount of area does not change. However, the new area is given the newest building code standard, which impacts the energy need.  
Demolition is controlled by an user defined s-curve, that decides how much area is demolished each year. The demolition rates are
set in relation to the area's age, and a development comparable to an S-curve is expected. The rates can be defined individually for each building category.

New area from population growth
-------------------------------

When new area is added due to changes in population, the total amount of area grows. The model has two different methods for forecasting newly built area due to changes in population. 
One method for residental area and another one for non-residental area.


Non-residental area
^^^^^^^^^^^^^^^^^^^

Population growth is the driver for new area in non-residential buildings. How the population develops is defined in the input file "population_forecast".
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
  :file: ../tables/area_per_person.csv
  :widths: 40, 20
  :header-rows: 1

Residential area
^^^^^^^^^^^^^^^^

New construction in residential area is based on population, but with some key differences compared to the non-residential area. Instead of forecasting square-meters per person
as is done in non-residential area, we first have to calculate the required number of new dwellings. Number of new dwellings is calculated from the "population_forecast" input file which contains 
both the popluation forecast and average household size. The new dwellings can be either apartments or houses and the ratio between them, and the area per dwelling, is given 
in the input file "new_buildings_residential".  

HVA ER FORMELEN VI BRUKER FOR Å BEREGNE ANTALL BYGG SOM MÅ BYGGES NYTT?? 



