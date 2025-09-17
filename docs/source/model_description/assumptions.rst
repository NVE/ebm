Data assumptions NVE
=====================

Building category and building code
-----------------------------------
The tables below shows the different building categories and building codes (TEK) which are used in the model. The building category table shows what other types of buildings
are included under the main building category. The building
categories are the same as defined in the building code with the exception of "light industry and repairs". From this category the model
only uses the area attributed to storage and warehouses, and the category is then named "storage". 

.. csv-table:: Building categories and associated building types
  :file: ..\tables\building_category.csv
  :header-rows: 1
  :widths: 25 25
  :delim: ;

.. csv-table:: Building codes and their active years
  :file: ..\tables\building_code_parameters.csv
  :header-rows: 1
  :widths: 25 25 25 25
  :delim: ,

Key Assumptions
---------------

The key assumptions in this model are rates for new construction, renovation, small measures and demolition, as well as 
energy need per area (kWh/m²) for different building categories of different ages with different conditions.

Different assumptions are made for all rates for all building categories. Since the building category house accounts 
for 57 % of the total area in the building stock, it is reasonable to say that the rates concerning houses will have a 
greater impact on total energy use than the other rates.

The new construction rates for all building categories are directly linked to `SSB's population projections <https://www.ssb.no/befolkning/befolkningsframskrivinger/statistikk/nasjonale-befolkningsframskrivinger>`_,
and this has a significant impact on the result. It is assumed that the area distributed by the number of inhabitants in Norway (m²/person)
for each categories of non-residential buildings will remain constant throughout the period. For example, in 2024 
it is calculated that there are 5.8 m² of office area per person in Norway, and 1.3 m² of nursing home per person. These 
numbers are assumed to be constant during the forecast period, so the area will grow according to population change.

Thus, no account is taken of upcoming structural changes. We know that the aging population will impact us during the
forecast period. This might result in a different rate of new construction for nursing homes. However, since it is not
possible to say with certainty that this change will occur, when it will occur, and what the change will be, it is not
considered in this model. Other structural changes that can be imagined include urbanization and what it might entail
in terms of increased use of cafes, restaurants, theatres and so on. This is also not taken into account in the forecast.
The assumptions can easily be changed in the input files.

Regarding residences, urbanization is included in the assumption that the proportion of households living in houses will
decrease and the proportion living in apartments will increase. The assumed development in the number of people per
household is crucial. Until now, we have seen a decrease in the number of people per household, and this is assumed
to continue. However, we know that more and more families are choosing to have three or more children, and that divorce
rates are flattening out. Together with increased immigration from non-Western countries, where there is a stronger
tradition of having more children, this can impact household sizes going forward and help dampen the development.

The energy need per m² is a theoretical size that cannot be measured. The building has a certain energy need that
needs to be met for it to function properly. The energy needs used in this model are calculated using Simien. The
assumptions made in connection with these calculations are essential for the result the model calculates.

How much energy used to meet the energy requirement of a building is dependent on several factors. The composition of 
heating solutions is very important. It decides which energy product is used, and also how much of the energy product is used.
For instance, both air-to-air heat pumps and electrical panel heaters use electricity to heat the space, but heat pumps use
less electricity than the electric radiators the achieve the same indoor temperature. The assumptions about efficiency
are essential in the energy use forecast.
