Energy need
###########

:ref:`Energy need <various_terms_glossary>` in the model is determined by many factors, building category, the area's age and if the area has been upgraded.
The baseline energy need per square meter is defined in the building code. Each :ref:`building category <building category and building code>` has a specific energy need according
to its building code, building condition and :ref:`energy purpose <energy purpose>`.
The energy condition of the area in the model changes between the model years due to implementation of renovation, small measures and other
energy efficiency measures (e.g. LED lighting). User defined S-curves determines how often and how much of the 
area undergoes renovation and small measures. 

.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none

Definitions
===========

The area in the model can have one of the following conditions: 

* Original condition
* Small measure
* Renovation
* Renovation and small measure

The energy need is distributed for different energy purposes. 
The model uses the following energy purposes:

**Heating Room Ventilation (heating_rv)** |br|
Energy used for space heating in rooms, typically through radiators, underfloor heating, or air systems. 
This is the energy required to maintain indoor temperatures at comfortable levels during colder periods. 

**Heating Domestic Hot Water (heating_dhw)** |br|
Energy used to heat water for domestic purposes such as bathing, cooking, and cleaning. 
This is separate from space heating and is often supplied by boilers, heat pumps, or electric water heaters.

**Fans and pumps** |br|
Electricity consumed by mechanical systems that circulate air or fluids within a building. This includes HVAC fans, 
circulation pumps for heating and cooling systems, and booster pumps for water supply.

**Lighting** |br|
Electricity used for indoor and outdoor lighting, including general illumination, task lighting, and emergency lighting systems. 
This category often includes both traditional and energy-efficient lighting technologies.

**Electrical equipment** |br|
Energy consumed by plug-in devices and fixed electrical systems not covered by other categories. This 
includes computers, kitchen appliances, office equipment, elevators, and other miscellaneous electrical loads.

**Cooling** |br|
Energy used for air conditioning and refrigeration systems to maintain comfortable indoor temperatures and preserve perishable goods. 
This includes chillers, split systems, and centralized cooling systems.


Model functionality
===================
The model calculates the energy need for every combination of building category, 
building code and condition for each year. The calculations are done separately for every energy purpose.

Heating Room Ventilation (heating_rv)
--------------------------------------

.. math::

   \text{energy need heating_rv} = & \text{ energy need heating_rv original condition}_\text{buidling code} \\
                                  &-\text{area upgrade}_\text{condition} \\
                                  &+\text{behaviour factor} 

Where

* :math:`\text{energy need heating_rv original condition}_\text{buidling code}` refers to the energy need for heating rooms and ventilation as determined by the building code.
* :math:`\text{area upgrade}_\text{condition}` refers to the reduction in energy need for heating rooms and ventilation as a result of the area being upgraded (the condition of the area).
* :math:`\text{behaviour factor}` factor refers to the inhabitant’s behavior. E.g. some people do not heat their whole house but keep some rooms cold and closed of during the winter. This would give a behavior factor smaller than 1, which coordinates with the portion of the house that is heated. 

Heating Domestic Hot Water (heating_dhw)
----------------------------------------

.. math::

   \text{energy need heating_dhw} = & \text{ energy need heating_dhw original condition}_\text{buidling code} \\
                                  & * \text{1-yearly reduction heating_dhw}^\text{year-start year} \\
                                  & * \text{improvment heating_dhw end year}_\text{year}

Where

* :math:`\text{energy need heating_dhw original condition}_\text{buidling code}` code refers to the energy need for heating_dhw as determined by the building code.
* :math:`\text{yearly reduction heating_dhw}` refers to a yearly reduction in energy need for heating_dhw as a result of energy measures e.g. transition to LED bulbs.

   * :math:`^\text{year}` refers to the year of the calculated energy need.
   * :math:`^\text{start year}` refers to the start of the energy measure.

* :math:`\text{improvment heating_dhw end year}_\text{year}` refers to an assumed reduction in energy need by a specific end year and how much of this is achieved in the year of the calculated energy need.

   * :math:`_\text{year}` refers to the year of the calculated enery need.

Fans and pumps
--------------

.. math::

   \text{energy need fans_and_pumps} = & \text{ energy need fans_and_pumps original condition}_\text{buidling code} \\
                                  & * \text{1-yearly reduction fans_and_pumps}^\text{year-start year} \\
                                  & * \text{improvment fans_and_pumps end year}_\text{year}

Where

* :math:`\text{energy need fans_and_pumps original condition}_\text{buidling code}` code refers to the energy need for fans_and_pumps as determined by the building code.
* :math:`\text{yearly reduction fans_and_pumps}` refers to a yearly reduction in energy need for fans_and_pumps as a result of energy measures e.g. transition to LED bulbs.

   * :math:`^\text{year}` refers to the year of the calculated energy need.
   * :math:`^\text{start year}` refers to the start of the energy measure e.g. improved ventilation.

* :math:`\text{improvment fans_and_pumps end year}_\text{year}` refers to an assumed reduction in energy need by a specific end year and how much of this is achieved in the year of the calculated energy need.

   * :math:`_\text{year}` refers to the year of the calculated enery need.
   
Lighting
---------

.. math::

   \text{energy need lighting} = & \text{ energy need lighting original condition}_\text{buidling code} \\
                                  & * \text{1-yearly reduction lighting}^\text{year-start year} \\
                                  & * \text{improvment lighting end year}_\text{year}

Where

* :math:`\text{energy need lighting original condition}_\text{buidling code}` code refers to the energy need for lighting as determined by the building code.
* :math:`\text{yearly reduction lighting}` refers to a yearly reduction in energy need for lighting as a result of energy measures e.g. transition to LED bulbs.

   * :math:`^\text{year}` refers to the year of the calculated energy need.
   * :math:`^\text{start year}` refers to the start of the energy measure e.g. transition to LED bulbs.

* :math:`\text{improvment lighting end year}_\text{year}` refers to an assumed reduction in energy need by a specific end year and how much of this is achieved in the year of the calculated energy need.

   * :math:`_\text{year}` refers to the year of the calculated enery need.

Cooling
-------

.. math::

   \text{energy need cooling} = & \text{ energy need cooling original condition}_\text{buidling code} \\
                                  & * \text{1-yearly reduction cooling}^\text{year-start year} \\
                                  & * \text{improvment cooling end year}_\text{year}

Where

* :math:`\text{energy need cooling original condition}_\text{buidling code}` code refers to the energy need for cooling as determined by the building code.
* :math:`\text{yearly reduction cooling}` refers to a yearly reduction in energy need for cooling as a result of energy measures e.g. transition to LED bulbs.

   * :math:`^\text{year}` refers to the year of the calculated energy need.
   * :math:`^\text{start year}` refers to the start of the energy measure.

* :math:`\text{improvment cooling end year}_\text{year}` refers to an assumed reduction in energy need by a specific end year and how much of this is achieved in the year of the calculated energy need.

   * :math:`_\text{year}` refers to the year of the calculated enery need.

Summarised
----------

This can be summarised in the following formula:

.. math::

   \begin{align}
   \text{energy need kWh/m}^{\text{2}}_{\text{year}} &= \text{energy need original condition}_{\text{building code}} \\
   &\times \text{improvement building upgrade}_{\text{building condition}} \\
   &\times \left(1.0 - \text{yearly reduction}\right)^{\text{year} - \text{start year}} \\
   &\times \text{improvement end year}_{\text{year}} \\
   &\times \text{behaviour factor} \\
   \end{align}

Where

 * :math:`\text{Energy need original condition}`
   - refers to the baseline energy use for the building type and purpose as defined by the building code.

 * :math:`\text{improvement building upgrade}`
   - accounts for renovations or upgrades that improve energy performance. By default this will be small measure, renovation or both.

 * :math:`\text{yearly reduction}`
   - refers to the annual percentage reduction in energy use due to technological progress or behavioral changes.

 * :math:`\text{improvement end year factor}`
   - is a modifier that adjusts the reduction effect with improvements expected to be finalized after a certain year. EU Commission’s RoHS directive, banning fluorescent lamps, is an example of policy that can be modelled using this factor.

 * :math:`\text{behaviour factor}`
   - captures changes in user behavior that affect energy consumption, like floor area utilization.

The factors described above affects the energy need in different ways and their usage depends on the intent of the user and what the user wants to achieve.

Data assumptions NVE
=====================

The original energy need of the area
------------------------------------
|energy_need_original_condition_ref|

In the NVE dataset, the original condition of the area has an energy need given by the building code. 
This energy need is in kWh per square meter. To calculate the original condition energy need per energy purpose, 
representative buildings per building category and building code have been simulated in 
Simien (a Norway-based software tool used by professionals for detailed energy calculations). This work was originally done 
by Multiconsult in 2014 to simulate the energy purpose for buildings built according to different building codes 
to calculate a new building performance energy scale. There have been changes in the energy purpose since then, 
especially in lighting, due to new eco design regulations. For more information on energy purpose in buildings see this 
summary report published in 2016 (in Norwegian) `Analyse av energibruk i yrkesbygg <https://publikasjoner.nve.no/rapport/2016/rapport2016_24.pdf>`_. 

Improving the energy need
--------------------------
|s_curve_ref|

Determines the rates for demolition and the implementing small measures and renovation. The rates are 
based on the area’s age, and a development comparable to an S-curve is expected. The rates can be 
defined individually for each building category. The proportion of a building type that is demolished, renovated, 
and undergoes small measures each year will therefore depend on the age distribution of the building stock for that building type.

It is not uncommon for buildings that have reached a certain age to have undergone both small measures 
and renovation. This is accounted for in the model. However, this version of 
the model does not allow small measures and renovation to be done several times on the same building. This is something 
that we plan to improve in coming versions of the model.

|improvement_building_upgrade_ref|

In EBM we assume that buildings undergo small measures and renovation over time. This 
reduces the energy need for heating rooms and ventilation by a certain percentage, as defined in this input file.

|energy_need_improvements_ref|

Specifies energy efficiency measures other than small measures and renovation. In this file, 
you can define any energy efficiency measure, by specifying the energy purpose, start year 
and end year of the measure and the energy improvement by the end year. By default, the model uses a 60 % improvement by 
the year 2030 for lighting. Lighting is expected to decrease by 0.5 % yearly after 2030. Electrical equipment has a yearly reduction of 1 %. 


.. |br| raw:: html

      <br>


.. |date| date::

Last Updated on |date|

Version: |version|.
