.. _heating_systems Heating systems:
Heating systems
#################

Heating systems is the link from the computed *energy need* to *energy use*. *Energy need* states what the building requires in 
terms of space heating, non-substitutable electrical use and hot tap water. Heating systems assigns specific heating technologies to meet the energy
demand of space heating and hot tap water. Various heating technologies have different efficiencies and energy carriers which then gives an *energy use*.
The energy useage per carrier and building category is compared with the national energy balance to fine tune the distribution of the various 
heating technologies. 

.. image:: images/Heating_systems_flowchart.png
  :width: 600
  :alt: Flowchart of heating systems

Methods
=======

Initial shares
------------
The initial heating system shares are based on the Norwegian energy building performance database. The database contains information on the energy class
of certified buildings. There are 1,2 million certificates in total spread out among the 13 building categories, however for some categories, especially 
non-residental buildings, the number of certificates are low. Some cleaning is done on the dataset to filter out misleading certificates and duplicates.

* Removed certificates missing building category, heated floor area or energy performance label
* Removed certificates where calculated delivered energy is above 1000 kWh/m:sup:'2'.
* If a certificate has been issued to the same address more than once, the most recent certificate is kept. This is done for all building categories
except for apartment blocks or hospitals as one address can contain multiple buildings or apartments. For apartments the house number is often missing.

After these three steps there are about 1 million certificates remaining. The associated building code classification is added to the certificates based on the supplied 
building year. 

The certificates has a column for "heating system". This column can vary from one or more energy products or a combination of various technologies. 
About 130 000 certificates do not have this information. For certificates missing this information an estimate is done based on the combination of 
"delivered energy". For example if the certificate has values in the "bio" and "electricity" delivered energy columns the heating system is set to
"Electricity - Bio". This results in 190 different heating systems which is then aggregated to 12 categories shown in the table below, together with the
corresponding technology for the different loads and hot tap water. 

.. csv-table:: Heating systems overview
  :file: tables\heating_systems_table.csv
  :widths: 15, 15, 15, 15, 15
  :header-rows: 1

The share of each heating system is the useful area summed up per heating system, building category and building code and then divided by the total useful
area of the given building category and building code. The useful area is part of the energy certificates.  

Manual tuning
-------
The described process gives a good starting point on the distribution of heating systems, but manual fine tuning is needed, especially on
heat pumps and wood stoves. The share of heat pumps is adjusted up, and the share of wood stoves is adjusted down. The manual tuning on heating systems is done 
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
The energy balance is reported on "residential" and "non-residential" buildings without any other details such as building code or 
specific building type. To get a good point of comparison we aggregate the heating systems to three categories:
* House
* Apartment block
* Non-residential buildings

First the initial heating system shares are assigned to the useful area given in the start year. This is done for each building category and
condition. It is assumed that the four different building conditions have the same heating systems under a given building code. The share of each 
heating system is the useful area summed up per heating system, aggregated building category and building code and then divided by the total useful
area of the given building category and building code. The new aggregated heating systems are then set for all the building codes in the three building categories.
Meaning that a TEK69 house has the same share heating systems as a TEK17 house, and a TEK69 kindergarten has the same share of heating systems as a TEK10 office.
The resulting heating systems are then used as an input to the model. An example on the aggreagted heating systems is given below for houses.

.. csv-table:: Aggregated heating systems - house
  :file: tables\shares_house_pretek49.csv
  :widths: 15, 15, 15, 15, 15
  :header-rows: 1

A final tuning of the heating systems are done in the calibration step of the model which is documented here.


Heating systems efficiencies
----------------------------
Each heating technology is either a base load, peak load, tertiary load or hot water, making up the combined heating system. The
different heating technologies have an assosicated efficency factor, load share factor and energy product.
The efficiency factor, together with the related energy product, is used to get *energy use* per energy product
from *energy need*. For example, given that the energy need is only covered by the specific technology:

* Air-air heat pumps have an efficiency factor of 2,5 with electricity as an energy product. 
  If the energy need for space heating is 1000 kWh, then the energy use is 400 kWh of electricity.      
* Wood fired stoves have an efficency factor of 0,65 with bio as an energy product. 
  If the energy need for space heating is 1000 kWh, then the energy use is 1538 kWh of bio.       

The load share factor decides how much of the heating need is covered by a specific technology. A single air-air heat
pump can not provide heating to the whole building, and in addtion needs supplementation from another heating technology at 
extreme temperatures. 

All the combinations can be found in the table chapter. 

Forecasting of heating systems
-------------------------------
Forecasting of heating systems are necessary to go from *energy need* to *energy use*. 
The forecasting defines the rate of change in one heating system to another towards 2050. The change is done on a percentage basis compared with the start 
year and can be specified on building category and building code. The percentage changes are given in the input file "heating_systems_projection". 
An example of the input is given in the table below. In the input file there are percentages for every year and not just the few years given as an example. 
The rate of change is a way to look at the heating systems of the whole building mass as it includes both 
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


Assumptions
===========

Initial shares
------------
During calculation of the intial shares about 130 000 certificates from the building energy performance database do not have information about the
buildings heating system. The certificates have information on "delivered energy" for various energy products. All the delivered energy coulumns are 
put together and an aggregation is made to create the most common combinations. Oil based heating was banned in 2020, but the database contains a lot of 
certificates issued before this ban. For the intiial shares we assume that half of the buildings who used oil-based heating switch to electric boilers and
the other half to a water-borne heatpump.  

The building energy performance database gives us information on heating systems across the various building codes. However for some building categories,
especially for newer building codes, the amount of certificates are too few to give a good representation of that particular building code and category. 
We therefore assume that the distribution of heating systems are the same across all non-residential buildings and building codes. The same assumption
is made for residential buildings, but are different for houses and for apartments.

Forecasting
-----------
The current implementation and numbers of forecasting heating systems is based on various assumptions. The first assumption is that natural gas is phased out as a heating
system for buildings by 2030. The second assumption is the continued growth of air-air heat pumps in houses. The final assumption is an increase in water-borne 
heating in new apartment blocks and non-residential buildings from building code requirements. The last assumption is causes an increase in electric boilers and 
central heating heat pumps. The final assumption is that the share of distrcit heating will increase in both non-residental buildings and in apartment blocks.  

Limitations
===========
The current implementation of forecasting for energy
systems is simplified, meaning it is not based on an economic optimization model such as `TIMES <https://iea-etsap.org/index.php/etsap-tools/model-generators/times>`_.



Heating systems glossary
========================
.. csv-table:: Glossary of terms used in heating systems
  :file: tables\heating_systems_glossary_csv.csv
  :header-rows: 1
  :widths: 10 10 30 30
  :delim: ;

Tables
======
The tables below show the various combinations of heating systems and heating technologies.

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


.. |br| raw:: html

      <br>

.. |date| date::

Last Updated on |date|.

Version: |version|.