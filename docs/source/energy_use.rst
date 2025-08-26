Energy use
###########

Energy use is calculated by



Methods
=======

The formula for **Total energy use per year** in the EBM (Energibruksmodell) is designed to annual energy use of the building mass. The calculation takes into account the type of energy carrier and efficiency in heating systems.

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

 * **energy need kWh/m²**
   - :ref:`Energy need` for the building type, building condition and purpose.
 * **area m²**
   - :ref:`area` for building type and condition
 * **heating systems share**
   - :ref: Distribution of `heating systems <Aggregating the heating systems>` across the building stock
 * **heating systems efficiency**
   - Thermal efficiency of heating systems


Assumptions
===========

 - Flere❓


Limitations
===========


.. |date| date::

Last Updated on |date|

Version: |version|.
