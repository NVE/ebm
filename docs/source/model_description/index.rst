Model Description
#############################

This is a bottom-up model that estimates area, energy requirement and energy use in the Norwegian building stock towards 2050. 
The model calculates area, energy requirement and energy use for the building categories used in the Norwegian building codes (TEK). 


.. toctree::
   :caption: Content
   :maxdepth: 1

   architecture
   assumptions



The Four Steps of the Model
---------------------------

Each building category is treated individually, and there are four steps in the calculations for each building category:

#. Determine rates for:
    a. Implementation of small energy efficiency measures (called small measures)
    b. Renovation
    c. Demolition
    d. New construction
#. Project area development, with area distributed by condition, i.e., whether the area is in origial condition or has undergone small measures or renovation or both.
#. Link area to relevant energy requirement distributed by energy purpose.
#. Assign heating system to the area to determine the use of different energy products (electricity, district heating, wood, natural gas).


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


----------------------------
2. Forecast Area Development
----------------------------

Data for the building area used in this model was prepared by Prognsesenteret in 2022. This data describes the building
stock in 2020 in Norway, distributed by building categories and age. The area is grouped into age groups that correspond
to the periods during which the various building codes (TEK) have been in effect. The age is suitable for use with the
age-specific rates for small measures, renovation, and demolition.

Based on the established rates for small measures, renovation, and demolition, as well as an assumed rate for new construction, 
the area within each building category is projected, distributed by the condition of the area, i.e., whether the area is in original 
condition, has undergone small measures or renovation or both.

For non-residential buildings, it is assumed that the area of a building type (e.g. office buildings) distributed by the
number of inhabitants in Norway (m²/person) will remain constant going forward. This assumption, along with the
calculated demolition, leads to new construction that will vary from year to year and between building categories.


------------------------------
3. Forecast Energy Need
------------------------------

The different "types" of area (variations in building category, age and condition) will have different energy needs. 
The model therefore assigns each area group (same building category, age and condition) an energy need. The energy 
need is distributed by these energy purposes: heating the building, heating domestic hot water, lighting, appliances, 
fans and pumps and cooling.

It is assumed that only the heating need is reduced during an upgrade of the buildings. The heating need is reduced 
by 7 % in a building that undergoes small measures, by 15 % in a building that is renovated, and by 20 % in a building that undergoes 
both improvement measures.

As an example, we can look at office buildings built according to TEK 97. The calculations show that in 2024, 26 % of this 
area was in its original condition. This area is assigned the energy need that TEK 97 implies. The energy need is 
distributed by energy purpose by Multiconsult.  It is calculated that 62 % of the office area built according to TEK 97 has 
undergone small measures. This area is assigned energy need that corresponds to a 7 % reduction in the heating requirement 
compared to the requirements in TEK97. Similarly, the model shows that 12 % of the office area built according to TEK 97 was
renovated by 2024 and therefore is assigned energy need with a 15 % reduction in heating requirement compared to the energy 
need of building in its original condition.


----------------------
4. Forecast Energy Use
----------------------

Finally, heating systems are allocated to the area. This can be done for each building category and each age group, or it can be done on 
an aggregated level, like treating all non-residental area the same way. We allocate a composition of different heating solutions 
to the area. For instance, X % of the house area use only direct resistance heating to heat the home, while Y % of the house area 
use both direct resistance heating, an air-to-air heat pump and a wood stove, and so on. The composition of heating solutions can change 
over time in the forecast period. 

Each heating technology (e.g. wood stove or electrical panel heater) use one energy carrier (e.g. wood or electricity). Knowing the 
composition of heating solutions, their efficiencies and which energy product they use, means that the model can forecast the use of 
different energy products. The energy products included in the model are electricity, fuel wood, district heating and fossil fuel.  







.. |date| date::

Last Updated on |date|.

Version: |version|.
