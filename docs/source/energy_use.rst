Energy use
###########

Energy use is calculated by



Methods
=======

The formula for **Total energy use per year** in the EBM (Energibruksmodell) is designed to estimate how much
energy the building mass use annually. The calculation takes into account efficiency in the technology used and the type of energy carrier.

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


Explanation of Each Factor
++++++++++++++++++++++++++

 By default the model use an 60% improvement by the year 2030 for lighting. Electrical equipment has a yearly reduction of 1%. Lighting is expected to decrease by 0.5% yearly after 2030. These values are defined in :ref:`energy_need_improvements.csv <energy_need_improvements>`

 * **energy need kWh/m²**
   - Baseline energy use for the building type and purpose as defined by the building code.
 * **area m²**
   - area area area
 * **heating systems share**
   - heating systems share heating systems share heating systems share
 * **heating systems efficiency**
   - heating systems efficiency heating systems efficiency heating systems efficiency


Assumptions
===========

 - Flere❓


    Limitations
    ===========


.. |date| date::

Last Updated on |date|

Version: |version|.
