import sys

import pandas as pd
import pytest

from ebm.model.energy_purpose import EnergyPurpose


@pytest.mark.skipif(sys.platform != "win32", reason="Test only runs on Windows")
def test_transform_convert_column_names_and_values():
    from ebm.services.calibration_writer import ComCalibrationReader
    ccr = ComCalibrationReader()
    values = (('Bygg', 'Gruppe', 'Endringsvariabel', 'Faktor', 'Endringsparameter'),
              ('Yrksebygg', 'Heating system', 'Electric boiler', 1.0, 'HP - Electricity'),
              ('Bolig', 'Energibehov', 'Heating dhw', 1.0, '-'),
              ('Skole', 'Energibehov', 'Elspesifikt', 0.1, '-'),
              ('Yrksebygg', 'Energibehov', 'heating rv', 0.5, '-'))
    r = ccr.transform(values)

    expected = pd.DataFrame([
        ['residential', 'energy_requirement', EnergyPurpose.HEATING_DHW, 1.0, None],
        ['school', 'energy_requirement', EnergyPurpose.ELECTRICAL_EQUIPMENT, 0.1, None],
        ['non_residential', 'energy_requirement', EnergyPurpose.HEATING_RV, 0.5, None]],
        columns=['building_category', 'group', 'purpose', 'heating_rv_factor', 'extra'])

    pd.testing.assert_frame_equal(r, expected)


def test_transform_unpack_purpose_when_on_and():
    from ebm.services.calibration_writer import ComCalibrationReader
    ccr = ComCalibrationReader()
    values = (('Bygg', 'Gruppe', 'Endringsvariabel', 'Faktor', 'Endringsparameter'),
              ('yrkesbygg', 'Energibehov', 'Heating rv and heating dhw', 0.8, '-'))
    r = ccr.transform(values)

    expected = pd.DataFrame([
        ['non_residential', 'energy_requirement', EnergyPurpose.HEATING_RV, 0.8, None],
        ['non_residential', 'energy_requirement', EnergyPurpose.HEATING_DHW, 0.8, None]],
        columns=['building_category', 'group', 'purpose', 'heating_rv_factor', 'extra'])

    pd.testing.assert_frame_equal(r, expected)
