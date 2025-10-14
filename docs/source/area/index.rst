.. _area_doc:

Area
#############################

Based on the assumed rates for small measures, renovation, and demolition, as well as an assumed rate for new construction, the area within each building category 
is forecasted. The model forecast area within each building code and determines the condition of the area, 
i.e., whether the area is in original condition, has undergone small measures or renovation or both.

.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none

Model functionality
===================

The total area in the model changes over time because some of the area is demolished and new area is constructed. In the model, newly built area is added in two ways:

* Newly built area replaces demolished area.
* New area is built due to population growth.

When new area replaces demolished area the total amount of area does not change. 
However, the new area is constructed according to the newest building code, which has an impact on the energy need. 
Demolition is determined by a user defined S-curve, which decides how much area is demolished each year. 
The demolition rates are set in relation to the area’s age, and a development comparable to an S-curve is expected. The 
rates can be defined individually for each building category.

When new area is added due to population growth, the total amount of area increases. The model has two
different methods for forecasting newly built area due to population growth. One method for residential area
and another for non-residential area.

Residential area
----------------
New construction in residential area is based on the population forecast and other key assumptions. 

First, we calculate the required increase in dwellings. This is calculated from |population_forecast_ref|
which contains both the population forecast and average household size.

.. math::

   \text{Increase in num. dwellings} (\text{year } x) = \frac{\text{population} (\text{year } x)}{\text{household size} (\text{year } x)} - \frac{\text{population} (\text{year } x-1)}{\text{household size} (\text{year } x-1)}     


The new dwellings can be either apartments or houses. The ratio between them, and the area per dwelling, 
is given in |new_buildings_residential_ref|. The increase in dwellings is divided into houses and apartments:

.. math::

   \text{Increase in num. houses} (\text{year } x) = &\text{ Increase in num. dwellings} (\text{year } x) \\  
                                                     &*\text{New house share} (\text{year } x)

.. math::

   \text{Increase in num. apartments} (\text{year } x) = &\text{ Increase in num. dwellings} (\text{year } x) \\
                                                         &*\text{New apartment share} (\text{year } x)

The new construction area for houses is calculated as follows:

.. math::

   \text{New construction house} (\text{year } x) = &\text{ Increase in num. houses} (\text{year } x) \\  
                                                     &*\text{Floor area new house} \\
                                                     &+\text{demolished area houses} (\text{year } x-1)

The construction area for new apartments is calculated as follows:

.. math::

   \text{New construction house} (\text{year } x) = &\text{ Increase in num. apartments} (\text{year } x) \\  
                                                     &*\text{Floor area new apartments} \\
                                                     &+\text{demolished area apartments} (\text{year } x-1)

Any residential floor area listed in |area_new_residential_buildings_ref| is considered a 
statistical fact and will override the model's calculated values for new construction.

Non-residential area
---------------------
Population growth is the driver for increasing non-residential area. The population forecast is defined in 
|population_forecast_ref|. The area per person for each building category is defined in |area_per_person_ref|.

The total area in a given year for each building category is the area per person times the population. 

.. math::

    \text{Total area} (\text{year } x) = \text{area\person} * \text{population} (\text{year } x)

The total area in a given year for each building cateogry can also be described as the area in the
previous year minus the demolished area the previous year plus new construction.

.. math::

    \text{Total area} (\text{year } x) = &\text{ total area} (\text{year } x-1) \\
                          &- \text{demolished area} (\text{year } x-1) \\
                          &+ \text{new construction} (\text{year } x)

Combining the two formulas and rearranging them gives us the method for calculating new construction:

.. math::

    \text{New construction} (\text{year } x) = &\text{ area/person} \times \text{population} (\text{year } x) \\
                          &-\text{area/person} \times \text{population} (\text{year } x-1) \\
                          &+ \text{ demolished}(\text{year }x-1)

The area per person is different for each of the non-residential building categories. It can also change from year to year.
In |area_per_person_ref|, we have assumed that the area per person for each building category is constant thorughout the forecast period. 

Data assumptions NVE
====================

Area in the starting year of the model
---------------------------------------
|area_ref|

Data for the building area used in this model was prepared by Prognosesenteret in 2022. . This data describes the building stock in 2020 in Norway, 
distributed by building categories and age. The area is grouped into age groups that correspond to the periods during which the 
various building codes (TEK) have been in effect. The age is suitable for use with the 
age-specific rates for small measures, renovation, and demolition.

Demolition of area
-------------------
|s_curve_ref|

The assumed rates for demolition in the model are made to resemble S-curves. This means that the demolition of a 
specific building category of a specific age varies over time in the model. The S-curves are specific to 
each building category but are the same across building code. 

The assumed demolition S-curves are based on limited data of average lifetime before demolition of the different building categories.

*NOTE! The current data on demolition and building of new area differs from available statistics. Changes in building stock area and 
energy consumption should therefore be used with caution. An updated and improved dataset will be published along with the next version of the model.*

Population forecast
-------------------
|population_forecast_ref|

The population forecast in the dataset is sourced from Statistics Norway. We use their main forecast, called 
`MMM <https://www.ssb.no/befolkning/befolkningsframskrivinger/statistikk/nasjonale-befolkningsframskrivinger>`_.

Dwellings
----------
|new_buildings_residential_ref|

The forecast for average household size in the dataset is made to be a continuation of historic household size
in Norway going back to the 1960s. `The historic household size is published by Statistics Norway <https://www.ssb.no/statbank/table/06076/>`_. We have assumed
a continued decrease in average household size, and that the decline will continue to decrease over time. We also assume
that the average houseohld size never dips below 2 persons per household. Until now, we have seen a decrease in the number of people per household, 
and this is assumed to continue. However, we know that more and more families are choosing to have three or more children, 
and that divorce rates are flattening out. Together with increased immigration from non-Western countries, where 
there is a stronger tradition of having more children, this can impact household sizes going forward and help dampen the decrease.

The forecasted allocation of new dwellings distributed into houses and apartments is made to be a continuation of the historic development in number of newly built
houses versus number of newly built apartments. This `statistic is published by Statistics Norway <https://www.ssb.no/statbank/table/05940/>`_. 
Urbanization is included in the assumption that the proportion of households living in houses will decrease and the 
proportion living in apartments will increase. 

The assumed average area for newly built houses and apartments is based on the historic development in average area of newly built dwellings. This is calculated 
based on information about `newly built dwellings published by Statistics Norway <https://www.ssb.no/statbank/table/05940/>`_.

Area per person in non-residential buidlings
-------------------------------------------
For non-residential buildings, NVE has assumed that the area of a building category (e.g. office buildings) distributed 
by the number of inhabitants in Norway (m²/person) will remain constant going forward. This assumption, 
along with the calculated demolition, leads to new construction that will vary from year to year and between building categories.

.. csv-table:: Area per person per non-residential building category
  :file: ../tables/area_per_person.csv
  :widths: 40, 20
  :header-rows: 1

The new construction rates for all building categories are directly linked to `SSB’s population forecast <https://www.ssb.no/befolkning/befolkningsframskrivinger/statistikk/nasjonale-befolkningsframskrivinger>`_, 
and this has a significant impact on the result. 


Thus, no account is taken of upcoming structural changes. We know that the average lifespan of the Norwegian 
population will increase during the forecast period. This might result in a different rate of new 
construction for nursing homes. However, since it is not possible to say for sure that this change will occur, 
when it will occur, and what the change will be, it is not considered in this model. Other structural changes 
might include urbanization and what it might entail in terms of increased use of cafes, restaurants, 
theatres and so on. This is also not taken into account in the forecast. The assumptions can easily be changed in the input files.




.. |date| date::

Last Updated on |date|

Version: |version|.
