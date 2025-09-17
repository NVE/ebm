Methods
=======

Forecasting of area
-------------------
New area in the model is added in two ways. Either by replacing demolished area or by building new area. When area is replaced by demolishion
the total amount of area does not change, but it gets updated to the newest building code standard. Demolishion is controlled by the s-curve. 
When constructing new area the total amount of area grows. The model has two different methods for forecasting newly built area. 
One method for residental area and another for non-residental area.

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

------------------
1. Determine Rates
------------------

The rates for implementing small measures, renovation, and demolition of buildings are determined. The rates are
set in relation to the area's age, and a development comparable to an S-curve is expected. The rates are set 
individually for each building category, but the principle is the same for all.

As an example, we can look at the small measures rate for office buildings. In the first few years after the
buildings are constructed, no small measures are implemented. When the buildings are three years old, small measures will 
be implemented on some of the buildings. Small measures will be implemented in 1.4 % of the relevant office area each year 
until the buildings are ten years old. At ten years of age, the pace of implementing small measures increases, and 4 % of the 
area undergoes small measures each year. This high rate continues until the building stock is 30 years old. From then on,
only 0.5 % of the building stock will undergo small measures annually. It is assumed that 1 % of the area
will never have small measures implemented, and that the buildings that are to have small measures implemented will have had 
them done within 50 years.

Similarly, rates are set for the renovation and demolition of buildings. The proportion of a building type that is
demolished, renovated, and undergoes small measures each year will therefore depend on the age distribution of the building stock
for that building type.

It is not uncommon for buildings that have reached a certain age to have undergone both small measures and renovation. This is
accounted for in the model. However, the model does not allow small measures and renovation to be done several times on the same building.
