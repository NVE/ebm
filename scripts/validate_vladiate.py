from vladiate import Vlad
from vladiate.inputs import LocalFile
from vladiate.validators import SetValidator

from ebm.model import BuildingCategory


class YourFirstValidator(Vlad):
    validators = {
        'building_category': [
            SetValidator([bc for bc in BuildingCategory])
        ]
    }


vlad = YourFirstValidator(source = LocalFile('input/building_categories.csv'))

validation = vlad.validate()

print('validated? ', validation)
