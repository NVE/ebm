limitations
===========


The geographical distribution module has the following limitations:

- Currently, the module distributes annual EBM energy use projection results only at the municipality level. However, future versions are intended to support
  additional levels of geographical distribution, such as price areas and grid zones.

- Distribution keys for electricity can only be generated via the Elhub API for years from 2022 onwards, since Elhub data is available only 
  from that year.

- The module does not currently account for demographic changes, such as population growth or decline, which may affect electricity consumption patterns.
  However, it is intended to implement a method that adjusts the electricity distribution keys based on projected demographic changes in future versions 
  of the module.
  