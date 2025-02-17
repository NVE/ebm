=================
Model Description
=================

This is a bottom-up model that estimates area, energy demand and energy use in the Norwegian building stock towards 2050. The model calculates area, energy demand and energy use for the building categories used in the Norwegian building codes (TEK) . Each building category is treated individually, and there are four steps in the calculations for each building type:

#. Determine rates for:
    a. Implementation of small energy efficiency measures
    b. Rehabilitation
    c. Demolition
    d. New construction
#. Project area development, with area distributed by condition, i.e., whether the area is untouched or has undergone energy efficiency measures or rehabilitation or both.
#. Link area to relevant energy demand distributed by energy purpose.
#. Assign heating solutions to the area to determine the use of different energy carriers (electricity, district heating, wood, natural gas).

------------------
1. Determine Rates
------------------

The rates for implementing small energy efficiency measures, rehabilitation, and demolition of buildings are
determined. The rates are set in relation to the area’s age, and a development comparable to an S-curve is expected.
The rates are set individually for each building type, but the principle is the same for all.

As an example, we can look at the energy efficiency rate for office buildings. In the first few years after the
buildings are constructed, no energy efficiency measures are implemented. When the buildings are three years old,
small energy efficiency measures will be implemented on some of the buildings. Small energy efficiency measures will be
implemented in 1.4 % of the relevant office area each year until the buildings are ten years old. At ten years of age,
the pace of implementing small energy efficiency measures increases, and 4 % of the area undergoes small energy
efficiency measures each year. This high rate continues until the building stock is 30 years old. From then on,
only 0.5 % of the building stock will undergo energy efficiency measures annually. It is assumed that 1 % of the area
will never have small energy efficiency measures implemented, and that the buildings that are to have energy efficiency
measures implemented will have had them done within 50 years.

Similarly, rates are set for the rehabilitation and demolition of buildings. The proportion of a building type that is
demolished, rehabilitated, and undergoes energy efficiency measures each year will therefore depend on the age
distribution of the building stock for that building type.

It is not uncommon for buildings that have reached a certain age to have undergone both small energy efficiency measures
and rehabilitation. This is accounted for in the model. However, the model does not allow small energy efficiency
measures and rehabilitation to be done several times on the same building.

----------------------------
2. Forecast Area Development
----------------------------

Data on the building area used in this model is prepared by Prognsesenteret in 2022. This data describes the building
stock in 2020 in Norway, distributed by building categories and age. The area is grouped into age groups that correspond
to the periods during which the various building codes have been in effect. The age is suitable for use with the
age-specific rates for small energy efficiency measures, rehabilitation, and demolition.

Based on the established rates for small energy efficiency measures, rehabilitation, and demolition, as well as an
assumed rate for new construction, the area within each building category is projected, distributed by the area's
condition, i.e., whether the area is untouched, has undergone small energy efficiency measures, or is rehabilitated.

For commercial buildings, it is assumed that the area of a building type (e.g., office buildings) distributed by the
number of inhabitants in the country (m²/person) will remain constant going forward. This assumption, along with the
calculated demolition, leads to new construction that will vary from year to year and between building categories.


-------------------------
3. Forecast Energy Demand
-------------------------

The different "types" of area (variations in building category, age and condition) will have different energy demands. The model therefore assigns each area group (same building category, age and condition) an energy demand. The energy demand is distributed by these energy purposes: heating the building, heating domestic hot water, lighting, appliances, fans and pumps and cooling.

It is assumed that only the heating demand is reduced during an upgrade of the buildings. The heating demand is reduced by 7% in a building that undergoes small energy efficiency measures, by 15% in a building that is rehabilitated, and by 20% in a building that undergoes both improvement measures.

As an example, we can look at office buildings built according to TEK 97. The calculations show that in 2024, 26% of this area was untouched. This area is assigned the energy demand that TEK 97 implies. The energy demand is distributed by energy purpose by Multiconsult.  It is calculated that 62 % of the office area built according to TEK 97 has undergone small energy efficiency measures. This area is assigned energy demand that corresponds to a 7 % reduction in the heating demand compared to the requirements in TEK97. Similarly, the model shows that 12 % of the office area built according to TEK 97 was rehabilitated by 2024 and therefore is assigned energy demand with a 15 % reduction in heating demand compared to the energy demand of an untouched building.


Key Assumptions
^^^^^^^^^^^^^^^

The key assumptions in this work are rates for new construction, rehabilitation, small energy efficiency measures and
demolition, as well as energy demand per area for different types of buildings of different ages with different
conditions.

Different assumptions are made for all rates for all building types. Since the building type house accounts for 57 % of
the total area in the building stock, it is reasonable to say that the rates concerning houses will have a greater
impact on total energy use than the other rates.

The new construction rates for all building types are directly linked to SSB's population projections, and this has a
significant impact on the result. It is assumed that the amount of area per inhabitant in Norway for the different types
of commercial buildings will remain constant throughout the period. For example, in 2024 it is calculated that there are
5.8 m² of office area per person in Norway, and 1.3 m² of nursing home per person. These numbers are assumed to be constant
during the forecast period, so the area will grow according to population change.

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

The energy demand per m² is a theoretical size that cannot be measured. The building has a certain energy demand that
needs to be met for it to function properly. The energy demands used in this model are calculated using Simien. The
assumptions made in connection with these calculations are essential for the result the model calculates.

How much energy used to meet the energy demand of a building is dependent on several factors. The choice of heating
technology is very important. It decides which energy carrier is used, and also how much of the energy carrier is used.
For instance, both air to air heat pumps and electric panel heaters use electricity to heat the space. But heat pumps use
less electricity than the electric panel heaters the achieve the same indoor temperature. The assumptions about efficiency
are very essential in the energy use forecast.
