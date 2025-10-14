Calibrating the model
=====================

To get a good starting point the model needs to be calibrated. The starting point is either energy use per energy product 
in a given year from temperature corrected statistics or a constructed year based on statistics. 

.. _Calibrating the model:

How to calibrate
----------------
Calibrating the model is done by changing up to three files.

- Kalibreringsark.xlsx
- energy_need_behaviour_factor.csv
- heating_system_efficiencies.csv

"Kalibreringsark.xlsx" can modify the heating system share where the given factor changes a percentage of one heating system for another. 
This excel file also makes it quick to see what the result of the calibration changes will be as the model directly modifies the cells
while having the excel file open. 

"energy_need_behaviour_factor.csv" contains a column called "behaviour_factor". The factor modifies the 
corresponding energy purpose in kWh/m\ :sup:`2` as given by a specific building code and building category. The start year and end
year can be specified, in addition to the mathematical function. 

The table below shows how the csv file is formatted. When "default" is input all valid
possibilites are affected. 

.. csv-table:: Energy need behaviour factor.
   :file: ../tables/energy_need_behaviour_factor.csv
   :header-rows: 1
   :widths: 10 10 10 10 10 10
   :delim: ,

It is also possible to modify the
factors given in "heating_system_efficiencies.csv" to fine tune the coverage of various heating technologies and their
efficiencies. 

Assumptions
------------
The calibration is based
on the `Norwegian energy balance <https://www.ssb.no/statbank/table/11561/>`_ published by Statistics Norway. The energy 
balance contains yearly consumption statistics per energy product on households and private and public services, 
including military. Heat production from heat pumps is calibrated on the basis of heat pump sale statistics from
the Norwegian Heat Pump Assosciation. 


.. |date| date::

Last Updated on |date|

Version: |version|.
