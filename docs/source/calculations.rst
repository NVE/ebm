Calculations/methods
====================

Heating systems efficiencies
----------------------------
A heating system in the model is made up of one or more heating technologies providing the heating 
need for space heating and domestic hot water. The various
combinations can be found under :ref:`heating_systems Heating systems`. Each heating technology is either a
base load, peak load, tertiary load or hot water, making up the combined heating system. The
different heating technologies have an assosicated efficency factor, coverage factor and energy carrier.
The efficiency factor, together with the related energy carrier, is used to get *energy use* per energy carrier
from *energy need*. For example without taking the coverage factor into account:

* Air-air heat pumps have an efficiency factor of 2,5 with electricity as an energy product. 
  If the energy need for space heating is 1000 kWh, then the energy use is 400 kWh of electricity.      
* Wood fired stoves have an efficency factor of 0,65 with bio as an energy product. 
  If the energy need for space heating is 1000 kWh, then the energy use is 1538 kWh of bio.       

The coverage/utilization factor decides how much of the heating need is covered by a specific technology. A single air-air heat
pump can not provide heating to the whole building, and in addtion needs supplementation from another heating technology at 
extreme temperatures. 

The efficiency and load share for the different combinations of heating systems are shown in a tables below.

.. csv-table:: Heating systems efficiency
  :file: tables\heating_systems_efficiencies.csv
  :widths: 15 15 15 15 5 5 5
  :header-rows: 1
  :delim: ;


.. csv-table:: Heating systems coverage
  :file: tables\heating_systems_coverage.csv
  :widths: 15 15 15 15 5 5 5
  :header-rows: 1
  :delim: ;


.. csv-table:: Heating systems hot tap water
  :file: tables\heating_systems_dhw.csv
  :widths: 15 15 15
  :header-rows: 1
  :delim: ;

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

    \text{New construction} (\text{year } x) = &\text{ area/person} * \text{population} (\text{year } x) \\
                          &-\text{area/person}*\text{population} (\text{year } x-1) \\
                          &+ \text{ demolished}(\text{year }x-1)

The area per person is different for each of the non-residental building categories. It can also change from year to year, but currently it is a constant.

.. csv-table:: Area per person per non-residential building category
  :file: tables\area_per_person.csv
  :widths: 40, 20
  :header-rows: 1

Residential area
^^^^^^^^^^^^^^^^
New construction in residential area are also based on population, but with some key differences compared to the non-residential area.


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
factors given in "heating_systems_efficiencies" to fine tune the coverage of various heating technologies and their
efficiencies. 
In the excel file "Kalibreringsark.xlsx" you can adjust various factors which can modify the following:

* Change one heating system for another.
* Energy need for space heating and hot tap water.
* Energy need for lighting and other electrical equipment.

When the model is run the excel file updates without having to close the file. 

.. |br| raw:: html

      <br>

Version: |version|.