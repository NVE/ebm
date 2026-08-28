from importlib.resources import files


def test_dataset_readme_md_use_uppercase():
    """Ensure that each dataset in ebm/data has a README.md file and that the filename uses the correct case.

The filename must use an uppercase stem ('README') and a lowercase extension ('.md').
    """
    data_path = files('ebm.data')
    assert data_path.is_dir(), 'No ebm/data directory found'

    datasets = [
        dataset for dataset in data_path.iterdir()
        if dataset.is_dir() and dataset.joinpath('population_forecast.csv').is_file()
    ]
    for dataset in datasets:

        readmes = [f for f in dataset.iterdir() if f.name.lower() == 'readme.md']
        assert len(readmes) == 1, f'Expected exactly 1 README.md in {dataset}. Got {len(readmes)} {readmes}'

        readme = readmes[0]
        assert readme.is_file(), f'dataset {dataset.name} is missing README.md'
        assert readme.name == 'README.md', f'README.md in dataset `{dataset.name}`  has the wrong case. Expected: README.md GOT: {readme.name}'
