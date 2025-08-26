Energy need
###########

Energy need per square metre is defined in the building code. Each building category has a specific energy need according to its building code and energy purpose.




Methods
=======

The formula for **energy need per square metre per year** in the EBM (Energibruksmodell) is designed to estimate how much
energy a building requires annually, adjusted for various factors.

.. math::

   \begin{align}
   \text{energy need kWh/m}^{\text{2}}_{\text{year}} &= \text{energy need original condition}_{\text{building code}} \\
   &\times \text{improvement building upgrade}_{\text{building condition}} \\
   &\times \left(1.0 - \text{yearly reduction}\right)^{\text{year} - \text{start year}} \\
   &\times \text{improvement end year}_{\text{year}} \\
   &\times \text{behaviour factor} \\
   \end{align}


Explanation of Each Factor
++++++++++++++++++++++++++

 * **Energy need original condition**
   - Baseline energy use for the building type and purpose as defined by the building code.

 * **improvement building upgrade**
   - Accounts for renovations or upgrades that improve energy performance. By default this will be small measure, renovation or both.

 * **Yearly reduction**
   - Annual percentage reduction in energy use due to technological progress or behavioral changes.

 * **Improvement end year factor**
   - A modifier that adjusts the reduction effect with improvements expected to be finalized after a certain year. EU Commission’s RoHS directive, banning fluorescent lamps, is an example of policy that can be modelled using this factor.

 * **Behaviour factor**
   - Captures changes in user behavior that affect energy consumption, like floor area utilization.

By default the model use an 60% improvement by the year 2030 for lighting. Electrical equipment has a yearly reduction of 1%. Lighting is expected to decrease by 0.5% yearly after 2030. These values are defined in :ref:`energy_need_improvements.csv <energy_need_improvements>`



Assumptions
===========

 - Energy need for heating (heating_rv) is reduced during an upgrade of the buildings.
 - Upgrading to multiple standards have diminishing returns.
 - Flere❓


Limitations
===========

.. |date| date::

Last Updated on |date|

Version: |version|.
