import os
import shutil
import sys
try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import version
    PackageNotFoundError = ImportError

# Legacy consoles (e.g. cp1252) cannot encode the emoji below.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, OSError, ValueError):
    pass

def split_and_break_path(path):
    if os.pathsep in path:
        path = '\n' + '\n'.join([f'                {p}' for p in path.split(os.pathsep)])
    return path


current_shell = os.environ.get('SHELL', 'Not detected 🙅')
if "PSModulePath" in os.environ:
    current_shell = "Probably PowerShell 😒"
elif os.environ.get("ComSpec", "").strip().endswith("cmd.exe"):
    current_shell = "Possibly cmd.exe 😞"
elif os.environ.get("SHELL"):
    current_shell = f"Unix shell: {os.environ['SHELL']} 😊"

try:
    pandas_version = version('pandas')
except PackageNotFoundError:
    pandas_version = 'No pandas 🙅'
try:
    numpy_version = version("numpy")
except PackageNotFoundError:
    numpy_version = 'No numpy 🙅'
try:
    pandera_version = version("pandera")
except PackageNotFoundError:
    pandera_version = "no pandera 🙅"
try:
    pywin32_version = version("pywin32")
except PackageNotFoundError:
    pywin32_version = "no pywin32 🙅"
try:
    ebm_version = version("ebm")
except PackageNotFoundError:
    ebm_version = "no ebm 🙅"

conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'No conda')
exe_path = shutil.which('python')
exe_path_reaction = '😒' if exe_path and 'Microsoft\\WindowsApps' in exe_path else ''
conda_path = shutil.which('conda')
venv_path = os.environ.get('VIRTUAL_ENV', 'No venv')
venv_reaction = '😊' if venv_path != 'No venv' else '😞'
env_python_path = os.environ.get('PYTHONPATH', 'No PYTHONPATH 🙅')
env_path = os.environ.get('PATH', 'No PATH 🙅')

conda_reaction = '😊'
if conda_env.upper() == 'BASE':
    conda_reaction = '😖'
elif 'No conda' in conda_env:
    conda_reaction = '😊'

version_reaction = '😊'
if sys.version_info.minor < 11:
    version_reaction = '😞'
elif sys.version_info.minor > 12:
    version_reaction = '😒'

env_python_path = split_and_break_path(env_python_path)
env_path = split_and_break_path(env_path)

print('           PATH?', env_path)
print('     PYTHONPATH?', env_python_path)
print('   cw directory?', os.getcwd())
print('  Current shell?', current_shell)
print('     python.exe?', exe_path, exe_path_reaction)
print(f'Python version? {sys.version_info.major}.{sys.version_info.minor} {version_reaction}')
print('      What venv?', venv_path, venv_reaction)
print('      conda.exe?', conda_path if conda_path else 'No conda.exe 🙅')
print(' What conda env?', conda_env, conda_reaction)
print(' Pandas version?', pandas_version)
print('  Numpy version?', numpy_version)
print('Pandera version?', pandera_version)
print('pywin32 version?', pywin32_version)
print('    ebm version?', ebm_version)

