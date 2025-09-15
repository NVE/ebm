About EBM
============


EBM is an open-source model used to forecast energy use in the building stock, developed by the Norwegian Water Resources and Energy Directorate (NVE). 
The model allows the user to analyze how policies and demographic trends impact yearly energy use on a national and regional level. 
Energy use is estimated by a bottom- up approach, based on the building stock area, energy need and distribution of heating systems. 
The mathematical model is implemented in Python, with input and output files in excel or csv.   

What is the purpose of EBM?
--------

EBM was developed to meet the analytical needs of NVE and to summarize important data and knowledge about the building stock in Norway. 
The model is targeted at high level national and regional analysis; it is not a tool for energy planning on a building level. 

Why is NVE sharing EBM with the public?
---------------

NVE aims to be transparent about the data, assumptions, and methodologies we use in our analyses. 
We share detailed information about EBM to create a common knowledge base on energy use in the building sector. 
In addition, we hope to receive useful feedback on how to improve both data and functionality in the model. 

Contact: ebm@nve.no

Which data is used in EBM?
---------------

The data provided with the model is the official NVE dataset. 
Recent analyses where the model and data is used are `Langsiktig kraftmarkedsanalyse 2025 <https://www.nve.no/energi/analyser-og-statistikk/langsiktig-kraftmarkedsanalyse/langsiktig-kraftmarkedsanalyse-2025/>`_ 
and `Tilstanden i kraftsystemet 2025 <https://publikasjoner.nve.no/rapport/2025/rapport2025_10.pdf>`_. 
The input data in EBM is based on many different data sources and statistics. Where data is missing, estimates are used. 
A detailed description of the input data is provided in “model functionality”, by topic. 

*NOTE! The current data on demolition and building of new area does not align with available statistics. 
Changes in building stock area and energy consumption should therefore be used with caution. 
An updated and improved dataset will be published along with the next version of the model.* 

Disclaimer of use
---------------
NVE does not take responsibility for how the EBM model, or its data are used by others. 
Users are responsible for their own analyses based on the EBM model and data. 
NVE does not review or endorse third-party use and cannot guarantee the accuracy or relevance of external results.



.. |date| date::

Last Updated on |date|.

Version: |version|.