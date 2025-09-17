.. _heating_systems Heating systems:

Heating systems
#################

Heating systems is the link from the computed *energy need* to *energy use*. *Energy need* states what the building requires in 
terms of space heating, non-substitutable electrical use and hot tap water. Heating systems assigns specific heating technologies to meet the energy
demand of space heating and hot tap water. Various heating technologies have different efficiencies and energy carriers which then gives an *energy use*.

<<<<<<< HEAD
The input to EBM is aggregated heating system shares for houses, apartment blocks and non-residental buildings. The source of the intial shares is the 
Norwegian energy performance building database which has been processed outside of EBM. As part of the processing the energy useage per product and building category is compared with the 
national energy balance to fine tune the distribution of the various heating technologies. The process is described under "methods" and "assumptions" and an overview 
is shown in the flowchart below. 

The method for forecasting is also described in the subpages. 
=======
A combination of different heating systems can be assigned to each building category and each age group. It is also possible to do it on  
an aggregated level, like treating all non-residental area the same way. For instance, X % of the house area use only direct resistance heating to heat the home, while Y % of the house area 
use both direct resistance heating, an air-to-air heat pump and a wood stove, and so on. The composition of heating solutions can be changed 
over time in the forecast period. 


The current implementation of forecasting for energy
systems is simplified, meaning it is not based on an economic optimization model such as `TIMES <https://iea-etsap.org/index.php/etsap-tools/model-generators/times>`_.
>>>>>>> 353d7d81f33f08fd8038ee6a681ddf8b9d67ec1b

.. toctree::
   :caption: Content
   :maxdepth: 1

   methods
   assumptions
   tables_glossary


.. image:: ../images/Heating_systems_flowchart.png
  :width: 600
  :alt: Flowchart of heating systems

.. |date| date::

Last Updated on |date|.

Version: |version|.
