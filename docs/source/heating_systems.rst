.. _heating_systems Heating systems:
Heating systems
===============
Overview
--------
Heating systems is the link from the computed *energy demand* to *energy use*. *Energy demand* states what the building requires in 
terms of space heating, non-substitutable electrical use and hot tap water. Heating systems assigns specific heating technologies to meet the energy
demand of space heating and hot tap water. Various heating technologies have different efficiencies and energy carriers which then gives an *energy use*.
The energy useage per carrier and building category is compared with the national energy balance to fine tune the distribution of the various 
heating technologies. 

.. image:: images/Heating_systems_flowchart.png
  :width: 600
  :alt: Flowchart of heating systems

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
  :file: tables\heating_systems_table.csv
  :widths: 15, 15, 15, 15, 15
  :header-rows: 1

The share of each heating system is the useful area summed up per heating system, building category and TEK and then divided by the total useful
area of the given building category and TEK. The useful area is part of the energy certificates.  

Manual tuning
-------
The described process gives a good starting point on the distribution of heating systems, but manual fine tuning is needed, especially on
heat pumps and bio. The share of heat pumps is adjusted up, and the share of bio is adjusted down. The manual tuning on heating systems is done 
to roughly hit the energy use from statistics before calibration for a given year is completed. Manual tuning is done by shifting a percentage
of a heating system to another on a per building and TEK basis. An example is given below which shifts 45 % of the district heating technology share
into Heat pump central heating and electric boilers for apartment blocks in TEK07, TEK10 and TEK17. 

.. code-block:: python
  
  {
    "current_heating_system": "DH",
    "new_heating_system": "HP Central heating - Electric boiler",
    "share": 0.45,
    "list_buildings": ["Apartment block"],
    "list_TEK": ["TEK07", "TEK10", "TEK17"]
  }

Aggregating the heating systems
-------
The energy balance is reported on "residential" and "non-residential" buildings without any other details such as TEK class or 
specific building type. To get a good point of comparison we aggregate the heating systems to three categories:
* House
* Apartment block
* Non-residential buildings

First the initial heating system shares are assigned to the useful area given in the start year. This is done for each building category and
condition. It is assumed that the four different building conditions have the same heating systems under a given TEK. The share of each 
heating system is the useful area summed up per heating system, aggregated building category and TEK and then divided by the total useful
area of the given building category and TEK. The new aggregated heating systems are then set for all the TEK in the three building categories.
Meaning that a TEK69 house has the same heating systems as a TEK17 house, and a TEK69 kindergarten has the same heating systems as a TEK10 office.
The resulting heating systems are then used as an input to the model. An example on the aggreagted heating systems is given below for houses.

.. csv-table:: Aggregated heating systems - house
  :file: tables\shares_house_pretek49.csv
  :widths: 15, 15, 15, 15, 15
  :header-rows: 1

A final tuning of the heating systems are done in the calibration step of the model which is documented here.

Forecasting of heating systems
-----------
Forecasting of heating systems are necessary to go from *energy need* to *energy use*. The current implementation of forecasting for energy
systems is simplified, meaning it is not based on an economic optimization model such as `TIMES <https://iea-etsap.org/index.php/etsap-tools/model-generators/times>`_.
The forecasting defines the rate of change in one heating system to another towards 2050. The change is done on a percentage basis compared with the start 
year and can be specified on building category or TEK. The percentage changes are given in the input file "heating_systems_projection". 
An example of the input is given in the table below. In the input file there are percentages for every year and not just the few years given as an example. 
The rate of change is a way to look at the heating systems of the whole building mass as includes both 
retrofits and new construction. I.e it is not feasible for an exisiting apartment block to switch over 
to distrcit heating, but a house retrofitting an air-air heat pump is possible. 


.. csv-table:: Heating systems forecasting example.
  :file: tables\heating_systems_projection.csv
  :widths: 10, 10, 15, 15, 5, 5 ,5, 5, 5
  :header-rows: 1

From the first row it states that in 2024 10 % of the heating system "Gas" in non-residental buidlings changes to
the heating system "HP Central heating - Electric boiler". If the heating system share of "Gas" was 5 % in 2023 and
"HP Central heating - Electric boiler" was 10 % for non-residental buildings, then the shares in 
2024 are 4,5 % "Gas" and 10,5 % "HP Central heating - Electric boiler". As 10 % of 5 % has changed from one heating system 
to another, as per the table.

After calibration and forecasting the resulting heating system fractions for houses are shown in the figure below. 

.. raw:: html
  :file: images\Hus.html

Heating systems glossary
------------------------
.. csv-table:: Glossary of terms used in heating systems
  :file: tables\heating_systems_glossary_csv.csv
  :header-rows: 1
  :widths: 10 10 30 30
  :delim: ;


Version: |version|.