import os
import shutil
import sys


python_version = sys.version_info.major, sys.version_info.minor
conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'No conda')
exe_path = shutil.which('python.exe')
venv_path = os.environ.get('VIRTUAL_ENV', 'No venv 🙅')

conda_reaction = '😊'
if conda_env.upper() == 'base':
    conda_reaction = '😖'
elif 'No conda' in conda_env:
    conda_reaction = '🙅'

version_reaction = '😊'
if sys.version_info.minor < 11:
    version_reaction = '😞'
elif sys.version_info.minor > 12:
    version_reaction = '😒'

print('Current path', os.getcwd())
print('Where is python.exe?', exe_path)
print(f'Python is version {sys.version_info.major}.{sys.version_info.minor} {version_reaction}')
print('What venv?', venv_path)
print('What conda?', conda_env, conda_reaction)