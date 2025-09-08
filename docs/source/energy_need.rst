Energy need
###########

The base line energy need per square metre is defined in the building code. Each :ref:`building category <building category and building code>` has a specific energy need according
to its building code, building condition and :ref:`energy purpose <energy purpose>`.


Methods
=======

The formula for **energy need per square metre per year** in the EBM (Energibruksmodell) is designed to estimate how much
energy a building requires annually, adjusted for various factors.

.. math::

   \begin{align}
   \text{energy need kWh/m}^{\text{2}}_{\text{year}} &= \text{energy need original condition}_{\text{building code}} \\
   &\times \text{improvement building upgrade}_{\text{building condition}} \\
   &\times \left(1.0 - \text{yearly reduction}\right)^{\text{year} - \text{start year}} \\
   &\times \text{improvement end year}_{\text{year}} \\
   &\times \text{behaviour factor} \\
   \end{align}


Explanation of Each Factor
++++++++++++++++++++++++++

 * **Energy need original condition**
   - Baseline energy use for the building type and purpose as defined by the building code.

 * **improvement building upgrade**
   - Accounts for renovations or upgrades that improve energy performance. By default this will be small measure, renovation or both.

 * **Yearly reduction**
   - Annual percentage reduction in energy use due to technological progress or behavioral changes.

 * **Improvement end year factor**
   - A modifier that adjusts the reduction effect with improvements expected to be finalized after a certain year. EU Commission’s RoHS directive, banning fluorescent lamps, is an example of policy that can be modelled using this factor.

 * **Behaviour factor**
   - Captures changes in user behavior that affect energy consumption, like floor area utilization.

By default the model use an 60% improvement by the year 2030 for lighting. Electrical equipment has a yearly reduction of 1%. Lighting is expected to decrease by 0.5% yearly after 2030. These values are defined in :ref:`energy_need_improvements.csv <energy_need_improvements>`



Energy purpose
++++++++++++++

Energy purpose is used to define level of energy, its source, and assess whether any energy-saving measures are applied.

There are six energy purposes defined in EBM.


Heating Room Ventilation (heating_rv)
    Energy used for space heating in rooms, typically through radiators, underfloor heating, or air systems. This includes the energy required to maintain indoor temperatures at comfortable levels during colder periods.

Heating Domestic Hot Water (heating_dhw)
    Energy used to heat water for domestic purposes such as bathing, cooking, and cleaning. This is separate from space heating and is often supplied by boilers, heat pumps, or electric water heaters.

Fans and pumps
    Electricity consumed by mechanical systems that circulate air or fluids within a building. This includes HVAC fans, circulation pumps for heating and cooling systems, and booster pumps for water supply.

Lighting
    Electricity used for indoor and outdoor lighting, including general illumination, task lighting, and emergency lighting systems. This category often includes both traditional and energy-efficient lighting technologies.

Electrical equipment
    Energy consumed by plug-in devices and fixed electrical systems not covered by other categories. This includes computers, kitchen appliances, office equipment, elevators, and other miscellaneous electrical loads.

Cooling
    Energy used for air conditioning and refrigeration systems to maintain comfortable indoor temperatures and preserve perishable goods. This includes chillers, split systems, and centralized cooling systems.


Below is an excerpt showing the kilowatt hours per square metre for retail buildings, categorized by energy purpose according to the TEK07 building code:

.. csv-table:: Energy need original condition retail TEK07
    :header: building_category, building_code, purpose, kwh_m2

    …,…,…,…
    retail,TEK07,lighting,50.2
    retail,TEK07,cooling,36.5
    retail,TEK07,electrical_equipment,3.7
    retail,TEK07,fans_and_pumps,45.8
    retail,TEK07,heating_dhw,10.5
    retail,TEK07,heating_rv,82.7
    …,…,…,…


Assumptions
===========

The energy need in a buldings original condition is based on the energy requirement given by the building code. This energy requirement is one common value in in kWh per square. 
To get the energy need per energy purpose in the original condition, representative buildings per building category and building code
have been simulated in Simien. This work was originally done by Multiconsult in 2014 to simulate the energy purpose for buildings built built after different building codes to calculate a 
new building performance energy scale. There have been changes in the energy purpose since then, especially in lighting, due to new legislation from ecodesign. 
For more information on energy purpose in buildings see this summary report published in 2016 `Analyse av energibruk i yrkesbygg <https://publikasjoner.nve.no/rapport/2016/rapport2016_24.pdf>`_. 

In EBM 1.0 we assume that buildings undergo small measures and renovation over time. This reduces the energy need for the energy purpose space heating.


Limitations
===========

.. |date| date::

Last Updated on |date|

Version: |version|.
