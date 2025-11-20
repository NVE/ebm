About EBM
=========

EBM is a model used by the Norwegian Water Resources and Energy Directorates (NVE) to forecast energy use in the building stock.
EBM is an open-source model developed and managed by NVE. 
The model allows the user to analyze how demographic trends and policy instruments impact the yearly energy use on a national and regional level. 
Energy use is estimated by a bottom- up approach, based on the building stock floor area, energy need and distribution of heating systems. 
The mathematical model is implemented in Python, with input and output files in excel or csv.



What is the purpose of EBM?
---------------------------

EBM is developed to meet the analytical needs of the Norwegian Ministry of Energy and NVE, 
in delivering high quality analyses to inform policy- making and the public. 
The model is an important tool in NVEs work to promote efficient energy use in Norway and alleviate pressure on the power system. 
The results from EBM are used in NVE’s reports on short-term power balance, 
long-term power market analysis and in various reports on the energy system and energy use in buildings. 

The model is targeted at high level national and regional analysis, delivering projections of the yearly energy use in buildings until 2050. 
EBM is not a tool for energy planning on a building level.


Why is NVE sharing EBM with the public?
---------------------------------------

NVE aims to be transparent about the data, assumptions, and methodologies we use in our analyses. 
We share detailed information about EBM to create a common knowledge base on energy use in the building sector. 
In addition, we hope to receive useful feedback on how to improve both data and functionality in the model. 

NVE is continuously working to improve the model and dataset, and welcomes feedback on email: ebm@nve.no. 

Which data is used in EBM?
--------------------------
The dataset provided with the model is developed and used by NVE. 
The input data in EBM is based on many different data sources and statistics. 
Where data is missing, estimates are used. 
Assumptions on future years in the model align with adopted policies in Norway, as of January 2025.  
A detailed description of the input data is provided in the documentation, by topic. 

The datasets and the model output is used in two recent analyses; `Langsiktig kraftmarkedsanalyse 2025 <https://www.nve.no/energi/analyser-og-statistikk/langsiktig-kraftmarkedsanalyse/langsiktig-kraftmarkedsanalyse-2025/>`_ 
and `Tilstanden i kraftsystemet 2025 <https://publikasjoner.nve.no/rapport/2025/rapport2025_10.pdf>`_. 

*NOTE! The current data used in EMB on demolition and building of new area differs from the available statistics. 
Our dataset indicates that more new buildings are being constructed, and more old ones are being demolished than the statistics show, 
resulting in lower energy consumption in the model.  
Results from the model on building stock area and energy consumption should therefore be used with caution. 
An updated and improved dataset will be published along with the next version of the model in 2026.* 

The dataset has been released by NVE under the `Creative Commons 4.0 license: Deed - Attribution 4.0 International - Creative Commons <https://creativecommons.org/licenses/by/4.0/>`_.
When using the dataset, you must credit NVE as described in the license. 

Disclaimer of use
-----------------
NVE does not take responsibility for how the EBM model or its data are used by others. 
Users are responsible for their own analyses based on the EBM model and data. 
NVE does not review or endorse third-party use and cannot guarantee the accuracy or relevance of external results.



.. |date| date::

Last Updated on |date|.

Version: |version|.
