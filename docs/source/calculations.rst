Calculations
============

Heating systems parameters
--------------



Calibration
--------
To get a good starting point the model needs to be calibrated. The starting point is either energy use per energy carrier 
in a given year from temperature corrected statistics or a constructed year based on statistics. The calibration is based
on the `Norwegian energy balance https://www.ssb.no/statbank/table/11561/`_ published by Statistics Norway. The energy 
balance contains yearly consumption numbers per energy carrier on households and private and public services, 
including military. 

What is calibrated?
^^^^^^^^^^^^
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

