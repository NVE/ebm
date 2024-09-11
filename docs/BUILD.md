# Building EBM

Building is used to create distribution packages for a Python project. It generates a source distribution (sdist), 
which includes the project’s source code and metadata. By default, the output is placed in the dist directory within your project. 
This makes it easier to distribute and share your project with others, or to upload it to package repositories like PyPi. 
In EBM there a build is automatically executed every time the main branch is changed. The built package will published as
an artifact when the version number has changed.

## Using build

### requirements
- build
    
```console
python -m pip install build  
```

### Configuration files

#### pyproject.toml
Contains project metadata, dependencies and script configuration. Release version number is also defined in this file.

```toml
# …
[project]
name = "energibruksmodell"
version = "x.y.z"
# …
```

More information: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

#### Manifest.in
Defines what files to be included in the package. 

More information: https://packaging.python.org/en/latest/guides/using-manifest-in/
### Building

To build a new package do the following while standing in the workspace root.
```shell
python -m build
```
By default, the resulting packages will be copied to the dists subdirectory. 
 - `energibruksmodell-x.y.z-py3-none-any.whl`
 - `energibruksmodell-x.y.z-py3-none-any.tar.gz`


## Using PyInstaller

### Documentation
https://pyinstaller.org/en/stable/index.html


### Requirements
Install PyInstaller from pypi.

`python -m pip install pyinstaller`

### Configuration

Make sure `datas` has default input directory in [calculate-area-forecast.spec](../calculate-area-forecast.spec)

```
…
datas=[(ebm/input)],
… 
```
[calculate-area-forecast.spec](../calculate-area-forecast.spec) is currently in .gitignore. The file will be created by running the PyInstaller build command below.


### Build

`python -m PyInstaller --name calculate-area-forecast --onefile -w -F -c ebm/__main__.py`


