Energy need
###########

Energy need per square metre is defined in the building code. Each building category has a specific energy need according to its building code and energy purpose.

The formula for **energy need per square metre per year** in the EBM (Energibruksmodell) is designed to estimate how much energy a building requires annually, adjusted for various factors. Here's a breakdown of each component:

🔍 Explanation of Each Term
===========================

1. **Energy need original condition**
   - Baseline energy use for the building type and purpose before any improvements.
   - Baseline energy use for the building type and purpose as defined by the building code.

2. **Building code improvement**
   - Reflects changes in energy efficiency due to updated building regulations.

3. **Building upgrade condition**
   - Accounts for renovations or upgrades that improve energy performance.

4. **Yearly reduction**
   - Annual percentage reduction in energy use due to technological progress or behavioral changes.

5. **Year - Start year**
   - The number of years since the baseline year, used to apply the yearly reduction.

6. **Improvement end year factor**
   - A modifier that adjusts the reduction effect with improvements expected to be finalized after a certain year.

7. **Behaviour factor**
   - Captures changes in user behavior that affect energy consumption, like floor area utilization.



2. Building Code Improvement
++++++++++++++++++++++++++++
*Reflects changes in energy efficiency due to updated building regulations.*

This factor accounts for the impact of **government-mandated building codes** that set minimum energy performance standards for new constructions and major renovations. As regulations evolve to require better insulation, more efficient systems, and sustainable materials, buildings constructed or upgraded under these codes consume less energy.

It adjusts the energy need in the model to reflect:
- **Stricter energy requirements** in newer codes (e.g., TEK17 in Norway).
- **Compliance timelines** for existing buildings to meet updated standards.
- **Regional or national policy goals** for reducing building-related emissions.

This factor is especially important in long-term energy modeling, as it captures the effect of regulatory progress on the building stock’s overall efficiency.




3. Building Upgrade Condition
+++++++++++++++++++++++++++++

*Accounts for renovations or upgrades that improve energy performance.*

This factor reflects the impact of **physical improvements** made to a building that enhance its energy efficiency. These upgrades can include:

- **Insulation improvements**
- **Window replacements**
- **Heating, ventilation, and air conditioning (HVAC) upgrades**
- **Installation of energy-efficient lighting or appliances**
- **Roof or wall refurbishments**

The model uses this factor to adjust the baseline energy need, recognizing that upgraded buildings consume less energy than those in their original condition. It helps simulate the effect of renovation programs, private investments, or compliance with updated building codes.





4. Yearly Reduction
+++++++++++++++++++
*Annual percentage reduction in energy use due to technological progress or behavioral changes.*

This factor represents the expected **annual decrease in energy consumption per square metre** over time. It accounts for improvements that naturally occur year by year, such as:

- **Technological advancements**: More efficient heating systems, lighting, insulation, and appliances.
- **Behavioral changes**: Increased awareness and better habits in energy use (e.g., turning off lights, optimizing heating).
- **Market trends**: Adoption of smart energy management systems or low-energy building designs.

The reduction is applied **exponentially** in the formula:
$$
(1.0 - \text{Yearly reduction})^{\text{Year - Start year}}
$$
This means the effect compounds over time, leading to significant energy savings in the long term.

Would you like help estimating a realistic yearly reduction rate for a specific building type or scenario?



6. What improvement end year factor represents
++++++++++++++++++++++++++++++++++++++++++++++

This factor adjusts the impact of energy efficiency improvements after a certain year, typically when upgrades or renovations are considered complete. It helps the model reflect that:

Before the end year: Improvements are gradually implemented.
After the end year: No further upgrades are expected, so the reduction effect stabilizes or stops.
Governments often set deadlines or targets for energy efficiency improvements through:

6. Improvement End Year Factor
A modifier that adjusts the reduction effect with improvements expected to be finalized after a certain year.

This factor represents the point in time when planned or policy-driven energy efficiency improvements are considered complete. After this year, the model assumes that no further upgrades or efficiency gains will occur unless new initiatives are introduced. It prevents the model from overestimating long-term reductions by capping the impact of ongoing improvements.

The factor is especially useful when modeling the effects of:

Government regulations with fixed deadlines (e.g., all buildings must meet a certain standard by 2030).
Renovation programs with defined end dates.
Technological adoption curves that plateau after widespread implementation.
By applying this factor, the model reflects a more realistic trajectory of energy use, aligning with actual policy timelines and market behavior.


Building codes (e.g., TEK in Norway)
Energy performance regulations
Renovation mandates
Climate action plans
Once these policies are fully implemented — say, by 2030 — the model assumes no further improvements unless new policies are introduced. That’s where the Improvement End Year Factor comes in: it caps or adjusts the effect of ongoing reductions after that policy milestone.


7. What the Behaviour Factor Represents
+++++++++++++++++++++++++++++++++++++++

It adjusts the energy need based on how people use the building, which can vary even if the physical structure remains the same. Examples include:

Floor area utilization: If only part of a building is actively used, the energy demand per square metre may be lower.
Occupancy patterns: More people or longer hours of use can increase energy consumption.
User habits: Efficient use of heating, lighting, and appliances can reduce energy need.
Temperature preferences: Lower indoor temperature settings reduce heating demand.
This factor helps the model reflect real-world usage rather than just theoretical or regulated standards.



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


Assumptions
===========

 -


Limitations
===========


.. |date| date::

Last Updated on |date|

Version: |version|.
