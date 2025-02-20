Heating systems
===============
Overview
--------
Heating systems is the link from the computed *energy demand* to *energy use*. *Energy demand* states what the building requires in 
terms of space heating, non-substitutable electrical use and hot tap water. Heating systems assigns specific heating technologies to meet the energy
demand of space heating and hot tap water. Various heating technologies have different efficiencies and energy carriers which then gives an *energy use*.
The energy useage per carrier and building category is compared with the national energy balance to fine tune the distribution of the various 
heating technologies. 


Initial shares
------------
The initial heating system shares are based on the Norwegian energy building performance database. The database contains information on the energy class
of certified buildings. There are 1,2 million certificates in total spread out among the 13 building categories, however for some categories, especially 
non-residental buildings, the number of certificates are low. Some cleaning is done on the dataset to filter out misleading certificates and duplicates.

* Removed certificates missing building category, heated floor area or energy performance label
* Removed certificates where calculated delivered energy is above 1000 kWh/m:sup:'2'.
* If a certificate has been issued to the same address more than once, the most recent certificate is kept. This is done for all building categories
except for apartment blocks or hospitals as one address can contain multiple buildings or apartments. For apartments the house number is often missing.

After these three steps there are about 1 million certificates remaining. The associated TEK class is added to the certificates based on the supplied 
building year. 

The certificates has a column for "heating system". This column can vary from one or more energy carriers or to a combination of various technologies. 
About 130 000 certificates do not have this information. For certificates missing this information an estimate is done based on the combination of 
"delivered energy". For example if the certificate has values in the "bio" and "electricity" delivered energy columns the heating system is set to
"Electricity - Bio". This results in 190 different heating systems which is then aggregated to 12 categories shown in the table below, together with the
corresponding technology for the different loads and hot tap water. 

.. csv-table:: Heating systems overview
  :file: tables\heating_systems_efficiencies_table.csv
  :widths: 15, 15, 15, 15, 15
  :header-rows: 1


After calibration the resulting heating systems shares are:

.. raw:: html
  :file: images\Hus.html

Forecasting
----------
