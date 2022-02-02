import json
import os
from pathlib import Path
import re
import requests
import warnings
import wget


def validate_url(url):
    """validates if URL is formatted correctly

    Returns:
        bool: True is URL is acceptable False if not acceptable
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


class Client(object):
    """Zenodo Client object

    Use this class to instantiate a zenodopy object
    to interact with your Zenodo account

        ```
        import zenodopy
        zeno = zenodopy.Client()
        zeno.help()
        ```

    Setup instructions:
        ```
        zeno.setup_instructions
        ```
    """

    def __init__(self, title=None, bucket=None, deposition_id=None, sandbox=None, ACCESS_TOKEN=None):
        self.title = title
        self.bucket = bucket
        self.deposition_id = deposition_id
        self.sandbox = sandbox
        self.ACCESS_TOKEN = ACCESS_TOKEN
        # 'metadata/prereservation_doi/doi'

    def __repr__(self):
        return f"zenodoapi('{self.title}','{self.bucket}','{self.deposition_id}')"

    def __str__(self):
        return f"{self.title} --- {self.deposition_id}"

    # ---------------------------------------------
    # hidden functions
    # ---------------------------------------------

    @staticmethod
    def _get_upload_types():
        """Acceptable upload types

        Returns:
            list: contains acceptable upload_types
        """
        return [
            "Publication",
            "Poster",
            "Presentation",
            "Dataset",
            "Image",
            "Video/Audio",
            "Software",
            "Lesson",
            "Physical object",
            "Other"
        ]

    @staticmethod
    def _read_config(path=None):
        """reads the configuration file

        Configuration file should be ~/.zenodo_token

        Args:
            path (str): location of the file with ACCESS_TOKEN

        Returns:
            dict: dictionary with API ACCESS_TOKEN
        """

        if path is None:
            print("You need to supply a path")

        full_path = os.path.expanduser(path)
        if not Path(full_path).exists():
            print(f"{path} does not exist. Please check you entered the correct path")

        config = {}
        with open(path) as file:
            for line in file.readlines():
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    if key in ("ACCESS_TOKEN", "ACCESS_TOKEN-sandbox"):
                        config[key] = value.strip()
        return config

    def _get_baseurl(self):
        """API URL

        This either returns the sandbox API URL
        or the actual Zenodo API URL.
        Sandbox is used for testing purposes
        and is not meant for projects you want to persist

        Returns:
            str: The API's URL
        """
        if self.sandbox:
            return "https://sandbox.zenodo.org/api"
        else:
            return "https://zenodo.org/api"

    def _get_key(self):
        """gets the ACCESS_TOKEN

        Returns:
            str: ACCESS_TOKEN to connect to zenodo
        """
        dotrc = os.environ.get("ACCESS_TOKEN", os.path.expanduser("~/.zenodo_token"))
        if os.path.exists(dotrc):
            config = self._read_config(dotrc)
            if self.sandbox is None:
                key = config.get("ACCESS_TOKEN")
                return key
            else:
                key = config.get("ACCESS_TOKEN-sandbox")
                return key
        else:
            print(' ** No ACCESS_TOKEN was found, check your ~/.zenodo_token file ** ')

        # initialize with key
        if self.ACCESS_TOKEN is not None:
            print(' ** Using ACCESS_TOKEN supplied at initialization ** ')
            return self.ACCESS_TOKEN

    def _get_headers(self):
        """gets the request headers

        Returns:
            dict: headers supplied to request calls
        """
        # gets the API key (tested)
        key = self._get_key()

        # header data attached to request
        if key is not None:
            return {"Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"}
        else:
            return None

    def _get_depositions(self):
        """gets the current project deposition

        this provides details on the project, including metadata

        Returns:
            dict: dictionary containing project details
        """
        # api baseurl (tested)
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        # get request, returns our response
        r = requests.get(f"{baseurl}/deposit/depositions",
                         headers=headers)
        if r.ok:
            return r.json()
        else:
            return None

    def _get_depositions_by_id(self, dep_id=None):
        """gets the deposition based on project id

        this provides details on the project, including metadata

        Args:
            dep_id (str): project deposition ID

        Returns:
            dict: dictionary containing project details
        """
        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        # get request, returns our response
        # if dep_id is not None:
        r = requests.get(f"{baseurl}/deposit/depositions/{dep_id}",
                         headers=headers)

        if r.ok:
            return r.json()
        else:
            return None

    def _get_depositions_files(self):
        """gets the file deposition

        ** not used, can safely be removed **

        Returns:
            dict: dictionary containing project details
        """
        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()
        dep_id = self.deposition_id

        # get request, returns our response
        r = requests.get(f"{baseurl}/deposit/depositions/{dep_id}/files",
                         headers=headers)

        if r.ok:
            return r.json()
        else:
            return None

    def _get_bucket_by_title(self, title=None):
        """gets the bucket URL by project title

        This URL is what you upload files to

        Args:
            title (str): project title

        Returns:
            str: the bucket URL to upload files to
        """
        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        dic = self.list_projects

        dep_id = dic[title] if dic is not None else None

        # get request, returns our response, this the records metadata
        r = requests.get(f"{baseurl}/deposit/depositions/{dep_id}",
                         headers=headers)

        if r.ok:
            return r.json()['links']['bucket']
        else:
            return None

    def _get_bucket_by_id(self, dep_id=None):
        """gets the bucket URL by project deposition ID

        This URL is what you upload files to

        Args:
            dep_id (str): project deposition ID

        Returns:
            str: the bucket URL to upload files to
        """
        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        # dic = get_projects()
        # dep_id = dic[title]

        # get request, returns our response
        r = requests.get(f"{baseurl}/deposit/depositions/{dep_id}",
                         headers=headers)

        if r.ok:
            return r.json()['links']['bucket']
        else:
            return None

    def _get_api(self):
        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        # get request, returns our response
        r = requests.get(f"{baseurl}", headers=headers)

        if r.ok:
            return r.json()
        else:
            return None

    # ---------------------------------------------
    # user facing functions/properties
    # ---------------------------------------------
    @property
    def setup_instructions(self):
        """instructions to setup zenodoPy
        """
        print(
            '''
            # ==============================================
            # Follow these steps to setup zenodopy
            # ==============================================
            1. Create a Zenodo account: https://zenodo.org/

            2. Create a personal access token
                2.1 Log into your Zenodo account: https://zenodo.org/
                2.2 Click on the drop down in the top right and navigate to "application"
                2.3 Click "new token" in "personal access token"
                2.4 Copy the token into ~/.zenodo_token using the following terminal command

                    { echo 'ACCESS_TOKEN: YOUR_KEY_GOES_HERE' } > ~/.zenodo_token

                2.5 Make sure this file was creates (tail ~/.zenodo_token)

            3. Now test you can access the token from Python

                import zenodopy
                zeno = zenodopy.Client()
                zeno._get_key() # this should display your ACCESS_TOKEN
            '''
        )

    @property
    def list_projects(self):
        """list projects connected to the supplied ACCESS_KEY

        prints to the screen the "Project Name" and "ID"
        """
        tmp = self._get_depositions()

        if isinstance(tmp, list):
            print('Project Name ---- ID')
            print('------------------------')
            for file in tmp:
                # dic[file['title']] = file['id']
                print(f"{file['title']} ----- {file['id']}")
        else:
            print(' ** need to setup ~/.zenodo_token file ** ')

        # print('Project Name ---- ID')
        # print('------------------------')
        # for key, val in dic.items():
        #    print(f"{key} ---- {val}")
        # return dic

    @property
    def list_files(self):
        """list files in current project

        prints filenames to screen
        """
        dep_id = self.deposition_id
        dep = self._get_depositions_by_id(dep_id)
        if dep is not None:
            print('Files')
            print('------------------------')
            for file in dep['files']:
                print(file['filename'])
        else:
            print(" ** the object is not pointing to a project. Use either .set_project() or .create_project() before listing files ** ")
            # except UserWarning:
            # warnings.warn("The object is not pointing to a project. Either create a project or explicity set the project'", UserWarning)

    def create_project(self, title=None, upload_type=None, description=None):
        """Creates a new project

        After a project is creates the zenodopy object
        willy point to the project

        title is required. If upload_type or description
        are not specified, then default values will be used

        Args:
            title (str): new title of project
            upload_type (str, optional): new upload type
            description (str, optional): new description
        """

        if upload_type is None:
            upload_types = self._get_upload_types()
            warnings.warn(f"upload_type not set, so defaulted to 'other', possible choices include {upload_types}",
                          UserWarning)
            upload_type = 'other'

        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        # get request, returns our response
        r = requests.post(f"{baseurl}/deposit/depositions",
                          headers=headers,
                          data=json.dumps({}))

        if r.ok:
            deposition_id = r.json()['id']

            self.change_metadata(dep_id=deposition_id,
                                 title=title,
                                 upload_type=upload_type,
                                 description=description,
                                 )

            self.deposition_id = r.json()['id']
            self.bucket = r.json()['links']['bucket']
            self.title = title
        else:
            print("** Project not created, something went wrong. Check that your ACCESS_TOKEN is in ~/.zenodo_token ")

    def set_project(self, dep_id=None):
        '''set the project by id'''
        projects = self._get_depositions()

        if projects is not None:
            project_list = [d for d in projects if d['id'] == int(dep_id)]
            if len(project_list) > 0:
                title = project_list[0]['title']
                self.title = title
                self.bucket = self._get_bucket_by_id(dep_id)
                self.deposition_id = dep_id
        else:
            print(f' ** Deposition ID: {dep_id} does not exist in your projects  ** ')

    def change_metadata(self, dep_id=None,
                        title=None,
                        upload_type=None,
                        description=None,
                        ):
        """change projects metadata

        ** warning **
        This changes everything. If nothing is supplied then
        uses default values are used.

        For example. If you do not supply an upload_type
        then it will default to "other"

        Args:
            dep_id (str): deposition to change
            title (str): new title of project
            upload_type (str): new upload type
            description (str): new description

        Returns:
            dict: dictionary with new metadata
        """

        baseurl = self._get_baseurl()

        headers = self._get_headers()

        if upload_type is None:
            upload_type = 'other'

        if description is None:
            description = "description goes here"

        data = {
            "metadata": {
                "title": f"{title}",
                "upload_type": f"{upload_type}",
                "description": f"{description}",
            }
        }

        r = requests.put(f"{baseurl}/deposit/depositions/{dep_id}",
                         headers=headers,
                         data=json.dumps(data))

        if r.ok:
            return r.json()
        else:
            return None

    def upload_file(self, file_path=None):
        """upload a file to a project

        Args:
            filename (str): name of the file to download
        """
        if file_path is None:
            print("You need to supply a path")

        if not Path(os.path.expanduser(file_path)).exists():
            print(f"{file_path} does not exist. Please check you entered the correct path")
        else:
            key = self._get_key()
            bucket_link = self.bucket

            # parameters
            params = {'access_token': key}

            with open(file_path, "rb") as fp:
                # text after last '/' is the filename
                filename = file_path.split('/')[-1]
                r = requests.put(f"{bucket_link}/{filename}",
                                 params=params,
                                 data=fp,)

                print(f"{file_path} successfully uploaded!") if r.ok else print("Oh no! something went wrong")

    def download_file(self, filename=None):
        """download a file from project

        Args:
            filename (str): name of the file to download
        """
        if filename is None:
            print(" ** filename not supplied ** ")

        key = self._get_key()

        # parameters
        params = {'access_token': key}

        bucket_link = self.bucket

        if bucket_link is not None:
            if validate_url(bucket_link):
                r = requests.get(f"{bucket_link}/{filename}",
                                 params=params,
                                 )
                wget.download(r.url) if r.ok else print(f" ** Something went wrong, check that {filename} is in your poject  ** ")
            else:
                print(f' ** {bucket_link}/{filename} is not a valid URL ** ')

    def delete_file(self, filename=None):
        """delete a file from a project

        Args:
            filename (str): the name of file to delete
        """
        key = self._get_key()

        # parameters
        params = {'access_token': key}

        bucket_link = self.bucket

        # with open(file_path, "rb") as fp:
        _ = requests.delete(f"{bucket_link}/{filename}",
                            params=params,)

    def _delete_project(self, dep_id=None):
        """delete a project from repository by ID

        Args:
            dep_id (str): The project deposition ID
        """
        # warnings.warn("This will permanently delete your project. Proceed with caution'", )
        # api baseurl
        baseurl = self._get_baseurl()

        # header data attached to request
        headers = self._get_headers()

        print('')
        # if input("are you sure you want to delete this project? (y/n)") == "y":
        # delete requests, we are deleting the resource at the specified URL
        r = requests.delete(f'{baseurl}/deposit/depositions/{dep_id}',
                            headers=headers)
        # response status
        print(r.status_code)

        # reset class variables to None
        self.title = None
        self.bucket = None
        self.deposition_id = None
        # else:
        #    print(f'Project title {self.title} is still available.')
