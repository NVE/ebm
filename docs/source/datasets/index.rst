.. _datasets_doc:

Dataset description
#####################
There are two available datasets for EBM, a short forecast and a long forecast. The two datasets are updated at 
different times in the relation to the publication of NVEs short- and long term electricity market analysis. 
The most recent dataset was made for the short forecast
`Status and development in the power system 2025-2030 <https://www.nve.no/energi/analyser-og-statistikk/status-og-utvikling-i-kraftsystemet/status-og-utvikling-i-kraftsystemet-2025-2030/>`_.

The format of the name of the dataset is "short/long forecast *start year*". Where *start year* is the start year
used in EBM for the relevant forecast. 

.. contents:: Table of Contents
    :depth: 2
    :local:
    :backlinks: none

Common assumptions
==================
Alt her ned til Short forecast kan kanskje strykes, slik at vi bare omtaler datasettene kort i seg selv og changeloggen. 

The assumptions described in this chapter are the assumptions that are likely to change from one dataset revision to the next.
Other assumptioms used in the dataset are described under their respective chapters under Model Functionality in the sidebar. 

Demolition
----------
The core principle of controlling the demolition using s-curves or similar curves is not subject to change. The paramaters
creating the s-curves which are described under :ref:`area<_area_doc>` are likely to change between datasets. This is due to 
getting more information and better data on demolition.

Heating systems efficiency
----------------
The heating system effiency for various heating technologies are expected to change to better account for
distribution losses, and to have a common efficiency assumption among other analysis.  

Calibration
-----------
The model is calibrated each year and is based on historical energy use trends and statistics. 
Historical trends and statistics are used so the start year is not widely changed from year to year, based on the
most recent statstics. This means the calibration year is an "ideal model year", and it can differ from the actual statistical year.
How to calibrate the model is explained here :ref:`Calibrating the model<Calibrating the model>`. 



.. _short_forecast_doc:
Short forecast
==============
The short forecast is updated to deliver to NVEs short term electricity market analysis. The forecast period of the 
short forecast dataset is the given start year plus 5, as this is the period the analysis. 


Current short forecast
----------------------

The current short term dataset is:

* Short forecast 2025
* Related report: `Status and development in the power system 2025-2030 <https://www.nve.no/energi/analyser-og-statistikk/status-og-utvikling-i-kraftsystemet/status-og-utvikling-i-kraftsystemet-2025-2030/>`_
* Published: 28.05.2026

.. _long_forecast_doc:
Long forecast
=============
The long forecast is updated to deliver to NVEs long term electricity market analysis. The forecast period of the 
long forecast dataset is the given start year to 2050 as this is the period the analysis. 


Current long forecast
---------------------

The current long term dataset is:

* Long forecast 2024
* Related report: `Long electricity market analysis 2025 <https://www.nve.no/energi/analyser-og-statistikk/langsiktig-kraftmarkedsanalyse/langsiktig-kraftmarkedsanalyse-2025/>`_
* Published: 17.06.2025

.. _changelog_doc:
Changelog
=========
The most important changes to the assumptions and input files between the latest and the previous dataset is described
here. 

Demolition
----------
The demolition s-curve for houses and apartment blocks have been heavily modified to get down to a yearly
demolition level more in line with historical statistics. The demolition is still about 20 % higher than historical 
statistics to reflect that some buildings are empty, and others are renovating to TEK17 level.

The change in demolition incrases the energy use as less old area gets replaced by newer and more energy effective
TEK 17 area. 

LED lighting
-------------
The reduction curve on LED lighting has been changed from ending in 2030 to ending in 2025 for houses and apartment blocks.
This means that the electricity reduction potential has already happened and the electricity consumption reduction from 
2025 to 2030 will be less than previously assumed.

Heating systems efficiency
--------------------------
We have previously not taken distribution losses for waterborne heating systems into account. The efficiency of district
heating and electric boilers have been changed from 0,98 to 0,8. 

Distribution of new households
--------------------------------
Construction stemming from population growth can meet the demand either building houses or apartment blocks. The distrubution
has been updated using newer statistics. This resulted in very minor changes.

Calibration
-----------
The short term 2025 dataset has been re-calibrated using updated historical trends and statistics. 
Residential buildings:

* Electricty per person is changed to 6 900 kWh/person per year.
* Distrcit heating: assume a 2 TWh consumtion.
* Bio (fuel wood) use in households is increased from 3 800 kWh per household to 3 900 kWh per household per year.

Non-residential buildings:

* Electricty per person is changed to 4 300 kWh/person per year.
* District heating: increasing from 4 TWh to 4,2 TWh. 




.. |date| date::

Last Updated on |date|

Version: |version|.