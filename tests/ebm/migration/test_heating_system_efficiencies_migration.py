from ebm.migrations import translate_heating_system_efficiencies, migrate_input_directory


def test_translate_heating_system_efficiencies():
    import pandas as pd
    df = pd.DataFrame({
        'Grunnlast energivare': [0.9],
        'Grunnlast': [1],
        'Spisslast': [2],
        'Ekstralast': [3],
        'Tappevann': [4]
    })
    result = translate_heating_system_efficiencies(df)
    assert 'base_load_energy_product' in result.columns
    assert 'Grunnlast' not in result.columns


def test_migrate_input_directory_rename_heating_systems_efficiencies(tmp_path):
    """Make sure migrate_input_directory rename
    heating_system->s<-_efficiencies.csv to heating_system-><-_efficiencies.csv"""

    target_file = tmp_path / 'heating_systems_efficiencies.csv'
    expected_file = tmp_path / 'heating_system_efficiencies.csv'

    file_contents = """
Grunnlast,heating_systems,base_load_energy_product,peak_load_energy_product,tertiary_load_energy_product,tertiary_load_coverage,base_load_coverage,peak_load_coverage,base_load_efficiency,peak_load_efficiency,tertiary_load_efficiency,domestic_hot_water_energy_product,domestic_hot_water_efficiency,Spesifikt elforbruk,cooling_efficiency
DELETEME,Electric boiler,Electricity,Ingen,Ingen,0.0,1.0,0.0,0.98,1.0,1,Electricity,0.98,1,4
    """.strip()
    target_file.write_text(file_contents)

    migrate_input_directory(tmp_path, translate_heating_system_efficiencies)

    assert not target_file.is_file()
    assert expected_file.is_file()

    actual = expected_file.read_text().strip()
    expected = file_contents.replace('Grunnlast,', '').replace('DELETEME,', '').strip()
    assert actual == expected


def test_migrate_input_directory_rename_ignore_heating_system_efficiencies_if_exists(tmp_path):
    """Make sure migrate_input_directory rename
    heating_system->s<-_efficiencies.csv to heating_system-><-_efficiencies.csv"""

    old_file = tmp_path / 'heating_systems_efficiencies.csv'
    existing_file = tmp_path / 'heating_system_efficiencies.csv'

    file_contents = """
Grunnlast,heating_systems,base_load_energy_product,peak_load_energy_product,tertiary_load_energy_product,tertiary_load_coverage,base_load_coverage,peak_load_coverage,base_load_efficiency,peak_load_efficiency,tertiary_load_efficiency,domestic_hot_water_energy_product,domestic_hot_water_efficiency,Spesifikt elforbruk,cooling_efficiency
DELETEME,Electric boiler,Electricity,Ingen,Ingen,0.0,1.0,0.0,0.98,1.0,1,Electricity,0.98,1,4
    """.strip()
    old_file.write_text('Invalid text')
    existing_file.write_text(file_contents)

    migrate_input_directory(tmp_path, translate_heating_system_efficiencies)

    assert existing_file.is_file()
    assert existing_file.read_text().strip() == file_contents.replace('Grunnlast,', '').replace('DELETEME,', '').strip()


def test_migrate_input_directory(tmp_path):
    target_file = tmp_path / 'heating_system_efficiencies.csv'
    target_file.write_text("""
Grunnlast,heating_systems,base_load_energy_product,peak_load_energy_product,tertiary_load_energy_product,tertiary_load_coverage,base_load_coverage,peak_load_coverage,base_load_efficiency,peak_load_efficiency,tertiary_load_efficiency,domestic_hot_water_energy_product,domestic_hot_water_efficiency,Spesifikt elforbruk,cooling_efficiency
DELETEME,Electric boiler,Electricity,Ingen,Ingen,0.0,1.0,0.0,0.98,1.0,1,Electricity,0.98,1,4
    """.strip())

    migrate_input_directory(tmp_path, translate_heating_system_efficiencies)
    assert target_file.is_file()

