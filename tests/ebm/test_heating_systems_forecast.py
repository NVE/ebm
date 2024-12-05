import pandas as pd
import pytest

from ebm.model.heating_systems import HeatingSystems
from ebm.heating_systems_forecast import (legge_til_alle_oppvarmingstyper,
                                          legge_til_ulike_oppvarmingslaster,
                                          aggregere_lik_oppvarming_fjern_0,
                                          ekspandere_input_oppvarming,
                                          framskrive_oppvarming,
                                          legge_til_resterende_aar_oppvarming,
                                          main)

# TODO: 
# add fixtures for the 3 input data files for one building category, 2 TEKS 
# add expected result dataframe and see that it runs ok. Refactor from there

if __name__ == "__main__":
    pytest.main()
    
