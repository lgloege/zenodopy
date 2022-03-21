# zenodopy

![Tests](https://github.com/lgloege/zenodopy/actions/workflows/tests.yaml/badge.svg)
[![codecov](https://codecov.io/gh/lgloege/zenodopy/branch/main/graph/badge.svg?token=FVCS71HPHC)](https://codecov.io/gh/lgloege/zenodopy)
[![pypi](https://badgen.net/pypi/v/zenodopy)](https://pypi.org/project/zenodopy)
[![License:MIT](https://img.shields.io/badge/License-MIT-lightgray.svg?style=flt-square)](https://opensource.org/licenses/MIT)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/lgloege/zenodopy/issues)

### Project under active deveopment, not production ready

A Python 3.6+ package to manage [Zenodo](https://zenodo.org/) repositories. 

### Functions Implemented
- `.create_project()`: create a new project
- `.upload_file()`: upload file to project
- `.download_file()`: download a file from a project
- `.delete_file()`: permanently removes a file from a project

Installing
----------

### PyPi
```sh
pip install zenodopy==0.2.0
```

### GitHub
```sh
pip install -e git+https://github.com/lgloege/zenodopy.git#egg=zenodopy
```

Using the Package
----------
1. **Create a Zenodo access token** by first logging into your account and clicking on your username in the top right corner. Navigate to "Applications" and then "+new token" under "Personal access tokens".  Keep this window open while you proceed to step 2 because **the token is only displayed once**.

2. **Store the token** in `~/.zenodo_token` using the folowing command
```sh
 { echo 'ACCESS_TOKEN: your_access_token_here' } > ~/.zenodo_token
```

3. **start using the `zenodopy` package**
```python
import zenodopy

# always start by creating a Client object
zeno = zenodopy.Client()

# list projects
zeno.list_projects

# list files 
zeno.list_files

# create a projects
zeno.create_project(title="test_project", upload_type="other")
# your zeno object now points to this newly created project

# create a file to upload
with open("~/test_file.txt", "w+") as f:
    f.write("Hello from zenodopy")

# upload file to zenodo
zeno.upload_file("~/test.file.txt")
```

Notes
----------
This project is under active development. Here is a list of things that needs improvement:
- **more tests**: need to test uploading and downloading files
- **documentation**: need to setup a readthedocs
- **download based on DOI**: right now you can only download from your own projects. Would be nice to download from 
- **asyncronous functions**: use `asyncio` and `aiohttp` to write async functions. This will speed up downloading multiple files. 
