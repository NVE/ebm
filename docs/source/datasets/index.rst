.. _datasets_doc:

Dataset description
===================

The dataset can be downloaded following the method described in :ref:`Getting started <getting_started_doc>`. 

EBM is a bottom up model that calculates the energy need and energy usage of the Norwegian building stock. The
foundation of the model and the datasets is the data on area and builidng age. The current datasets have the building area
stock from 2020, and all area after this is modelled. The available datasets are considered a base scenario, meaning 
the analysis and assumptions are based on current and adopted policy. 

There are two available datasets for EBM, a short analysis and a long analysis. The two datasets are updated at 
different times in the relation to the publication of NVEs short- and long term electricity market analysis. 
The most recent dataset was made for the short analysis
`Status and development in the power system 2025-2030 <https://www.nve.no/energi/analyser-og-statistikk/status-og-utvikling-i-kraftsystemet/status-og-utvikling-i-kraftsystemet-2025-2030/>`_.
The report for the long analysis can be found here  `Long electricity market analysis 2025 <https://www.nve.no/energi/analyser-og-statistikk/langsiktig-kraftmarkedsanalyse/langsiktig-kraftmarkedsanalyse-2025/>`_.

An imporant part of updating the datasets is the calibration step. The model is calibrated each year and is based on historical energy use trends and statistics. 
Historical trends and statistics are used so the start year is not widely changed from year to year, based on the
most recent statstics. This means the calibration year is an "ideal model year", and it can differ from the actual statistical year.
How to calibrate the model is explained here :ref:`Calibrating the model<Calibrating the model>`. 

**Limitations**

The current version of the two datasets and their respective forecasts have the following imitations
and data assumptions:

- "Norgespris" has not been taken into account in the current version.
- The impact of the ageing populations is not accounted for.
- Rebound effects of energy efficiency measures are not included.
- Public and private buildings are not defined.

**Dataset format**

The format of the name of the dataset is "short/long analysis *start year*". Where *start year* is the start year
used in EBM for the relevant analysis. 

Changelong
----------

Version 2.1 Short analysis 2025 - 2026-04-26
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* rush_period_years is changed from 75 to 76 in demolition s-curve paramters for house and apartment block.

    * Small changes to rush_share and never_share to account for the change in rush_period_years. 

Version 2.0 Short analysis 2025 - 2025-12-06
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Demoliton s-curves have been modified for houses and apartment blocks to be more in line with historical statistics.
* The reduction curve on LED lighting has been changed from ending in 2030 to ending in 2025 for houses and apartment blocks. 
  This means that the electricity reduction potential has already happened resulting in lower electricty reduction from LED.

* The heating system efficiency for district heating and electric boilers are changed from 0,98 to 0,8 to better take distribution losses into account.
* Updated the distribution of houses and apartment blocks when constructing new households. Resulting in minor changes.
* Calibration households:

    * Electricty per person is changed to 6 900 kWh/person per year.
    * Distrcit heating: assume a 2 TWh consumtion.
    * Bio (fuel wood) use in households is increased from 3 800 kWh per household to 3 900 kWh per household per year.

* Calibration non-residental buildings:

    * Electricty per person is changed to 4 300 kWh/person per year.
    * District heating: increasing from 4 TWh to 4,2 TWh. 

Version 1.0 Long analysis 2024 - 2025-01-20
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* First dataset version. Must be considered a work in progress. 


.. |date| date::

Last Updated on |date|

Version: |version|.