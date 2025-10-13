.. _energy_use_doc: 
Energy use
###########

The model calculates the energy use by combining energy need, area and heating systems. 
How much energy the building stock uses depends on it's energy need and which heating technologies are used to cover it. 
For instance, both air-to-air heat pumps and electrical panel heaters use electricity to heat a room, but heat pumps use
less electricity than electric panel heaters to achieve the same indoor temperature. 

Each heating technology (e.g. wood stove or electrical panel heater) uses one energy product (e.g. wood or electricity).
Knowing the composition of heating solutions, their efficiencies and which energy product they use,
means that the model can forecast the use of different energy products. 
The energy products included in the model are electricity, fuel wood, district heating and fossil fuel.


.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none


Model functionality
===================

The formula for **Total energy use per year** in EBM is designed to calculate the annual energy use in the Norwegian building stock. 
The calculation takes into account the type of energy product and efficiency in heating systems.

.. math::

   \text{energy use kWh}_{\text{year}} =
      \frac{
        \text{energy need kWh/m}^{\text{2}}_{\text{year}}
        \times
        \text{area m}^{\text{2}}_{\text{year}}
        \times \text{heating systems share}_{\text{year}}
      }{
        \text{heating systems efficiency kWh/kWh}
      }


where

 * :math:`\text{energy need kWh/m}^{\text{2}}`
   - :ref:`Energy need` for the building category, building condition and purpose.
 * :math:`\text{area m}^{\text{2}}`
   - :ref:`area` for building type and condition
 * :math:`\text{heating systems share}`
   - Distribution of :ref:`heating systems <Aggregating the heating systems>` across the building stock
 * :math:`\text{heating systems efficiency kWh/kWh}`
   - :ref:`Thermal efficiency of heating systems<heating_systems_efficiencies>`

Energy use per year can be broken down into energy use per purpose and energy product across building categories and building codes. 

Holiday homes
=============

Holiday homes are treated separately in EBM. 
We assume that the building code and condition of the buildings is not as important for energy use in holiday 
homes as it is for other building categories, as the use of holiday homes varies a lot. 
Some holiday comes are only used a few days per year, while others are used several months per year.  

Model functionality
-------------------

To calculate the energy use in holiday homes in Norway, 
we use the number of holiday homes and the average energy use per holiday home. 

First, we make a forecast of the number of holiday homes:

.. math::

   \text{Number of holiday homes}_{\text{year}} =
      \frac{
        \text{population}_{\text{year}}
      }{
        \text{average number of people per holiday home}_{\text{2021-2024}}
      }

where

 * :math:`\text{population}_{\text{year}}`
   - referst to the assumed population in the model year.
 * :math:`\text{average number of people per holiday home}`
   - refers to the ratio between population in Norway and the number of holiday homes, averaged over the years 2021 to 2024

The next step is to calculate the energy use, based on the use of electricity, wood fuel and fossil fuels per holiday home.
Assumptions in the model on the energy use of holiday homes is described under Data Assumptions NVE.

Energy use in holiday homes is calculated as follows: 

.. math::

   \text{Energy use in holiday homes}_{\text{year, energy product}} =
       \text{Number of holiday homes}_{\text{year}} \\
       \times
       \text{energy use per holiday home}_{\text{year, energy product}}

where

 * :math:`\text{Energy use in holiday homes}_{\text{year, energy product}}`
   - refers to the assumed average energy use per holiday home in the model year, for each energy product

Data assumptions NVE
--------------------

The assumptions concerning other building categories than holiday homes, are described in :ref:`Area`, :ref:`Energy need` and :ref:`Heating systems`. 

|holiday_home_stock_ref|. |br|
The historic number of holiday homes is based on statistics from Statistics Norway. 

|holiday_home_energy_consumption_ref|. |br|
The `historic energy consumption in holiday homes <https://www.ssb.no/en/statbank/table/13929>`_ is published by Statistics Norway. 
This energy use is divided by the `number of holiday homes <https://www.ssb.no/en/statbank/table/03174>`_, also published by Statistics Norway. 
This is done for the energy products electricity, wood fuel and fossil fuel. 

The development in use of the different energy products per holiday home is assumed based on the historic development. 
The electricity use per holiday home has increased over the last 20 years, and we expect this trend to continue. 
However, we assume that the increase will slow down over time and that the electricity use per holiday home never exceeds the level in 2021, 
when corona restrictions on travel caused people to use their holiday homes more. 

For fuelwood use, we assume that going forward, this will be the same as the average use in the years 2019 to 2023. 

There are still some use of fossil fuels in holiday homes. This is assumed to continue in the years ahead. 


.. |br| raw:: html

      <br>

.. |date| date::

Last Updated on |date|

Version: |version|.
