Model Description
#############################

EBM is a bottom-up model that estimates how area, energy need and energy use in the building stock changes over time. 
The start year of the model consist of user input about the building stock area, 
it's condition and how it is divided between different building categories and building codes. 
Information about heating systems and efficiencies in the start year must also be provided. 
When forecasting how the building stock changes over time, the model consider changes in 

* population and demographics
* demolition and construction of buildings
* energy efficiency measures
* heating systems 

The main result of the model is annual energy use for each building category, building code, energy purpose and energy product. 
The annual energy use can be distributed geographically as defined by the user. 


.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none


The main steps of the model
===========================

For each building category and year in the model the calculations consist of four main steps:

#. Determine rates for implementation of:
    a. Small energy efficiency measures (called small measures)
    b. Renovation
    c. Demolition
    d. New construction
#. Forecast area development, with area distributed by condition, i.e., whether the area is in original condition or has undergone small measures or renovation or both.
#. Link area to relevant energy need allocated by energy purpose.
#. Assign heating system to the area to determine the use of electricity, district heating, wood and natural gas.

The detailed description of calculations in the model and NVE's data assumptions is organized by the following themes: 

* :ref:`Building category and building code<building_category_building_code_doc>`
* :ref:`Area<area_doc>`
* :ref:`Energy need<energy_need_doc>`
* :ref:`Heating systems<Heating systems>`
* :ref:`Energy use<energy_use_doc>`
* :ref:`Geographical distribution<geographical_distribution_doc>` 

Architecture
=============


EBM Container diagram
---------------------
Describes the model's overall architecture and inner workings. 

.. image:: ../_static/model_description/EBM-container-drawio.svg
   :alt: C4 EBM container diagram


EBM Pipeline Component diagram
------------------------------

Describes how the pipeline container interacts with components

.. image:: ../_static/model_description/EBM-pipeline.drawio.svg
   :alt: C4 pipeline component diagram




.. |date| date::

Last Updated on |date|.

Version: |version|.
