from setuptools import setup

if __name__ == "__main__":
    setup(
        name='zenodopy',         # How you named your package folder (MyLib)
        packages=[''],   # Chose the same as "name"
        version='0.1.0',      # Start with a small number and increase it with every change you make
        license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
        description='Manage Zenodo projects',   # Give a short description about your library
        author='Luke Gloege',                   # Type in your name
        author_email='ljg2157@columbia.edu',      # Type in your E-Mail
        url='https://github.com/lgloege/zenodopy',   # Provide either the link to your github or to your website
        keywords=['zenodo'],   # Keywords that define your package best
        install_requires=[            # I get to this in a second
            'requests',
            'types-requests',
            'wget',
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
            'Intended Audience :: Developers',      # Define that your audience are developers
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',   # Again, pick a license
            'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
    )
