Energy need
###########

Energy need per square metre is defined in the building code. Each building category has a specific energy need according to its building code and energy purpose.

The formula for **energy need per square metre per year** in the EBM (Energibruksmodell) is designed to estimate how much energy a building requires annually, adjusted for various factors. Here's a breakdown of each component:



Methods
=======


.. math::

   \begin{align}
   \text{energy need kWh/m}^{\text{2}}_{\text{year}} &= \text{energy need original condition}_{\text{building code}} \\
   &\times \text{improvement building upgrade}_{\text{building condition}} \\
   &\times \left(1.0 - \text{yearly reduction}\right)^{\text{year} - \text{start year}} \\
   &\times \text{improvement end year}_{\text{year}} \\
   &\times \text{behaviour factor} \\
   \end{align}


Explanation of Each Term
++++++++++++++++++++++++

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



Assumptions
===========

 - It is only heating need that is reduced during an upgrade of the buildings.
 - Upgrading to multiple standards have demishing returns.
 - Flere❓


Limitations
===========


.. |date| date::

Last Updated on |date|

Version: |version|.
