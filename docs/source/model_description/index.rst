Model Description
#############################

This is a bottom-up model that estimates how area, energy need, heating systems and energy use in the building stock changes over time. 
The annual energy use can be distributed geographically as defined by the user. In the model description you will find an explanation of how the model works and the assumptions the dataset in the model is based on. 
Methods and data assumptions are organized by the following themes: 

* Building category and building code
* Area
* Energy need
* Heating systems
* Energy use
* Geographical distribution 


.. toctree::
   :caption: Content
   :hidden:
   :maxdepth: 1

   architecture
   assumptions


Each building category is treated individually, and there are four steps in the calculations for each building category:

#. Determine rates for:
    a. Implementation of small energy efficiency measures (called small measures)
    b. Renovation
    c. Demolition
    d. New construction
#. Project area development, with area distributed by condition, i.e., whether the area is in original condition or has undergone small measures or renovation or both.
#. Link area to relevant energy requirement distributed by energy purpose.
#. Assign heating system to the area to determine the use of different energy products (electricity, district heating, wood, natural gas).




.. |date| date::

Last Updated on |date|.

Version: |version|.
