import os
import shutil
import sys


def split_and_break_path(path):
    delimiter = ''
    if ';' in path:
        delimiter = ';'
    elif ':' in path:
        delimiter = ':'
    if delimiter:
        path = '\n' + '\n'.join([f'                {p}' for p in path.split(delimiter)])
    return path


python_version = sys.version_info.major, sys.version_info.minor
conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'No conda')
exe_path = shutil.which('python.exe')
conda_path = shutil.which('conda.exe')
venv_path = os.environ.get('VIRTUAL_ENV', 'No venv 🙅')
env_python_path = os.environ.get('PYTHONPATH', 'No PYTHONPATH 🙅')
env_path = os.environ.get('PATH', 'No PATH 🙅')

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

env_python_path = split_and_break_path(env_python_path)
env_path = split_and_break_path(env_path)

print('          PATH?', env_path)
print('           CWD?', os.getcwd())
print('    PYTHONPATH?', env_python_path)
print('    python.exe?', exe_path)
print(f'Python version? {sys.version_info.major}.{sys.version_info.minor} {version_reaction}')
print('     What venv?', venv_path)
print('     conda.exe?', conda_path if conda_path else 'No conda.exe 🙅')
print('What conda env?', conda_env, conda_reaction)
