import typing

import pandas as pd


def transform(heating_rv: pd.Series, heating_rv_factor=None) -> pd.Series:
    if heating_rv_factor is None:
        return heating_rv
    calibrated = heating_rv * heating_rv_factor
    calibrated.name = heating_rv.name
    return calibrated


def default_calibrate_heating_rv():
    df = pd.DataFrame({
        'building_category': ['non_residential', 'residential'],
        'heating_rv_factor': [1.0, 1.0]})
    return df


class EbmCalibration:
    energy_requirement_original_condition: pd.Series
    pass

class ComExcelCalibrationReader:
    """ Extract relevant cells from workbook and sheet and convert
        transform to EbmCalibration or pd.DataFrame?

    """

    com_excel_calibration: typing.Dict
    def extract(self) -> pd.DataFrame:
        """
            Trenger workbook, sheet ?, kan vel hardkode cells i starten
            returnerer dataframe som er 1 til 1 fra excel?

        """

        pass

    def transform(self, df) -> EbmCalibration:
        """ Konvertere dataframe til en som passer kalibrering
            "gruppe", building_category, heating_rv, faktor <--- building_category skal være pakket ut?

        """
        pass


class CalibrationReader:
    def extract(self) -> pd.Series:
        pass

    def transform(self) -> pd.Series:
        pass

    def load(self) -> None:
        pass


class CalibrationWriter:
    pass
