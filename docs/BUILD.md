# Building EBM

## requirements
- build
    
```console
python -m pip install build  
```

## Configuration files

### pyproject.toml
Contains project meta data, dependencies and script configuration. Release version number is also defined in this file.

```toml
…
[project]
name = "energibruksmodell"
version = "x.y.z"
…
```

More information: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

### Manifest.in
Defines what files to be included in the package. 

More information: https://packaging.python.org/en/latest/guides/using-manifest-in/
## Building

To build a new package do the following while standing in the workspace root.
```shell
python -m build
```
By default, the resulting packages will be copied to the dists subdirectory. 
 - energibruksmodell-x.y.z-py3-none-any.whl
 - energibruksmodell-x.y.z-py3-none-any.tar.gz


