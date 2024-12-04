import zenodopy as zen
"""
This module contains tests for the zenodopy library using pytest.
Functions:
    test_client: Tests the initialization of the zen.Client object with and without a token.
    test_read_config: Tests the _read_config method of the zen.Client object to ensure it raises a TypeError.
    test_get_baseurl: Tests the _endpoint attribute of the zen.Client object for both sandbox and production environments.
    test_get_depositions: Tests the _get_depositions, _get_depositions_by_id, and _get_depositions_files methods of the zen.Client object.
    test_get_bucket: Tests the _get_bucket_by_id method of the zen.Client object.
    test_get_projects_and_files: Tests the list_projects and list_files properties of the zen.Client object.
Note:
    The update and change_metadata functions have been updated to add new versions to existing depositions. 
    This functionality is being tested in test_version. We will bring back individual tests once these changes 
    have been merged upstream to keep the changes incremental.
"""
import pytest

# use this when using pytest
import os
ACCESS_TOKEN = os.getenv('ZENODO_TOKEN')
DEPOSITION_ID = os.getenv('DEPOSITION_ID')

# can also hardcode sandbox token using tox locally
# ACCESS_TOKEN = ''


def test_client():
    _ = zen.Client()
    _ = zen.Client(token=ACCESS_TOKEN, sandbox=True)
    # zeno.list_projects


def test_read_config():
    zeno = zen.Client()
    with pytest.raises(TypeError):
        zeno._read_config()


def test_get_baseurl():
    zeno = zen.Client(sandbox=True)
    assert zeno._endpoint == 'https://sandbox.zenodo.org/api'

    zeno = zen.Client()
    assert zeno._endpoint == 'https://zenodo.org/api'


# def test_get_key():
#     zeno = zen.Client(token=ACCESS_TOKEN, sandbox=True)
#     zeno._get_key()
#     zeno.title
#     zeno.bucket
#     zeno.deposition_id
#     zeno.sandbox

#     zobj = zen.Client()
#     if zobj._get_key() is None:
#         pass


# def test_get_headers():
#     zeno = zen.Client(token=ACCESS_TOKEN, sandbox=True)
#     zeno._get_headers()

#     zeno = zen.Client()
#     if zeno._get_headers() is None:
#         pass


def test_get_depositions():
    zeno = zen.Client(sandbox=True,token=ACCESS_TOKEN)
    dep_id=DEPOSITION_ID
    zeno.set_project(dep_id=dep_id)
    depositions = zeno._get_depositions()
    deposition_by_id = zeno._get_depositions_by_id()
    deposition_files = zeno._get_depositions_files()
    if len(depositions) > 0:
        pass
    elif int(deposition_by_id['id']) == dep_id or int(deposition_by_id['conceptrecid']) == dep_id:
        pass
    elif len(deposition_files) >0:
        pass
    else:
        raise ValueError('Depositions not found')

def test_get_bucket():
    zeno = zen.Client(sandbox=True,token=ACCESS_TOKEN)
    dep_id=DEPOSITION_ID
    zeno.set_project(dep_id=dep_id)
    bucket_link = zeno._get_bucket_by_id()
    assert bucket_link.startswith('https://sandbox.zenodo.org/api/files/')
    # if zeno._get_bucket_by_title(title='fake title') is None:
        # pass


def test_get_projects_and_files():
    zeno = zen.Client(sandbox=True,token=ACCESS_TOKEN)
    dep_id=DEPOSITION_ID
    zeno.set_project(dep_id=dep_id)
    _ = zeno.list_projects
    _ = zeno.list_files


# @pytest.mark.filterwarnings('ignore::UserWarning')
# def test_create_project():
#     zeno = zen.Client(sandbox=True)
#     zeno.create_project(title='test', upload_type='other')
#     zeno.create_project(title='test')


# def test_set_project():
#     zeno = zen.Client()
#     zeno.set_project(dep_id='123')


# # don't know how to mock inputs
# def test_delete_project():
#     pass


# def test_change_metadata():
#     zeno = zen.Client(sandbox=True)
#     zeno.change_metadata(dep_id='fake_ID', title='fake_title')


# def test_upload_file():
#     zeno = zen.Client(sandbox=True)
#     zeno.upload_file(file_path='path')


# def test_download_file():
#     zeno = zen.Client(sandbox=True)
#     zeno.download_file(filename='test')
#     zeno.bucket = 'invalid_url'
#     zeno.download_file(filename='test')


# def test_tutorial():
#     zeno = zen.Client(ACCESS_TOKEN=ACCESS_TOKEN, sandbox=True)
#     zeno.list_projects
#     zeno.list_files
#     zeno.title
#     zeno.bucket
#     zeno.deposition_id
#     zeno.sandbox

#     params = {'title': 'test_set', 'upload_type': 'other'}
#     zeno.create_project(**params)

#     # params = {'title': 'test', 'upload_type': 'other'}
#     # zeno.create_project(**params)
#     zeno.list_projects

#     # with open("/home/test_file.txt", "w+") as f:
#     #     f.write("test")

#     # zeno.upload_file("/home/test_file.txt")
#     zeno.list_files
#     zeno.list_projects
#     _ = zeno.change_metadata(zeno.deposition_id, title='test_new')
#     zeno.list_projects
#     # zeno.download_file('test_file.txt')
#     # zeno.delete_file('test_file.txt')
#     zeno.list_files
#     # zeno._delete_project(zeno.deposition_id)
#     zeno.list_projects
#     zeno._delete_project(zeno.deposition_id)
#     zeno.list_projects
