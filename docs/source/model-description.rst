=================
Model Description
=================

This is a bottom-up model that estimates area, energy requirement and energy use in the Norwegian building stock towards 2050. 
The model calculates area, energy requirement and energy use for the building categories used in the Norwegian building codes (TEK). 



The Four Steps of the Model
===========================

Each building category is treated individually, and there are four steps in the calculations for each building category:

#. Determine rates for:
    a. Implementation of small energy efficiency measures (called small measures)
    b. Renovation
    c. Demolition
    d. New construction
#. Project area development, with area distributed by condition, i.e., whether the area is in origial condition or has undergone small measures or renovation or both.
#. Link area to relevant energy requirement distributed by energy purpose.
#. Assign heating system to the area to determine the use of different energy carriers (electricity, district heating, wood, natural gas).


------------------
1. Determine Rates
------------------

The rates for implementing small energy, renovation, and demolition of buildings are determined. The rates are
set in relation to the area’s age, and a development comparable to an S-curve is expected. The rates are set 
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


----------------------------
2. Forecast Area Development
----------------------------

Data for the building area used in this model is prepared by Prognsesenteret in 2022. This data describes the building
stock in 2020 in Norway, distributed by building categories and age. The area is grouped into age groups that correspond
to the periods during which the various building codes (TEK) have been in effect. The age is suitable for use with the
age-specific rates for small measures, renovation, and demolition.

Based on the established rates for small measures, renovation, and demolition, as well as an assumed rate for new construction, 
the area within each building category is projected, distributed by the area's condition, i.e., whether the area is in original 
condition, has undergone small measures or renovation or both.

For non-residential buildings, it is assumed that the area of a building type (e.g. office buildings) distributed by the
number of inhabitants in Norway (m²/person) will remain constant going forward. This assumption, along with the
calculated demolition, leads to new construction that will vary from year to year and between building categories.


------------------------------
3. Forecast Energy Requirement
------------------------------

The different "types" of area (variations in building category, age and condition) will have different energy requirements. 
The model therefore assigns each area group (same building category, age and condition) an energy requirement. The energy 
requirement is distributed by these energy purposes: heating the building, heating domestic hot water, lighting, appliances, 
fans and pumps and cooling.

It is assumed that only the heating requirement is reduced during an upgrade of the buildings. The heating requirement is reduced 
by 7 % in a building that undergoes small measures, by 15 % in a building that is renovated, and by 20 % in a building that undergoes 
both improvement measures.

As an example, we can look at office buildings built according to TEK 97. The calculations show that in 2024, 26 % of this 
area was in its original condition. This area is assigned the energy requirement that TEK 97 implies. The energy requirement is 
distributed by energy purpose by Multiconsult.  It is calculated that 62 % of the office area built according to TEK 97 has 
undergone small measures. This area is assigned energy requirement that corresponds to a 7 % reduction in the heating requirement 
compared to the requirements in TEK97. Similarly, the model shows that 12 % of the office area built according to TEK 97 was
renovated by 2024 and therefore is assigned energy requirement with a 15 % reduction in heating requirement compared to the energy 
requirement of building in its original condition.


----------------------
4. Forecast Energy Use
----------------------

Finally, heating systems are allocated to the area. This can be done for each building category and each age group, or it can be done on 
an aggregated level, like treating all non-residental area the same way. We allocate a composition of different heating solutions 
to the area. For instance, X % of the house area use only electric radiator to heat the home, while Y % of the house area 
use both electric radiator, an air-to-air heat pump and a wood burner, and so on. The composition of heating solutions can change 
over time in the forecast period. 

Each heating technology (e.g. wood burner stove or electric radiator) use one energy carrier (e.g. wood or electricity). Knowing the 
composition of heating solutions, their efficiencies and which energy carrier they use, means that the model can forecast the use of 
different energy carriers. The energy carriers included in the model are electricity, wood, district heating and fossil fuel.  


Key Assumptions
===============

The key assumptions in this model are rates for new construction, renovation, small measures and demolition, as well as 
energy requirement per area (kWh/m²) for different building categories of different ages with different conditions.

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

The energy requirement per m² is a theoretical size that cannot be measured. The building has a certain energy requirement that
needs to be met for it to function properly. The energy requirements used in this model are calculated using Simien. The
assumptions made in connection with these calculations are essential for the result the model calculates.

How much energy used to meet the energy requirement of a building is dependent on several factors. The composition of 
heating solutions is very important. It decides which energy carrier is used, and also how much of the energy carrier is used.
For instance, both air-to-air heat pumps and electric radiators use electricity to heat the space. But heat pumps use
less electricity than the electric radiators the achieve the same indoor temperature. The assumptions about efficiency
are essential in the energy use forecast.

