#!/usr/bin/env python
"""Installs ResourcePackage"""
from setuptools import setup

if __name__ == "__main__":
    extraArguments = {
            'classifiers': [
                """License :: OSI Approved :: BSD License""",
                """Programming Language :: Python""",
                """Topic :: Software Development :: Libraries :: Python Modules""",
                """Intended Audience :: Developers""",
            ],
            'keywords': 'resource,package,automation,wxPython,image,embed,encode,find,data',
            'long_description' : """Automated resource-as-package embedding mechanism

ResourcePackage creates an automatically updating
package directory where resource files are embedded in
automatically-named Python modules.  This allows the
application to find the resources even after being
stored via py2exe or the McMillan Installer.

Includes specialised support for embedding wxPython
images as well.
""",
            'platforms': ['Any'],
        }
    ### Now the actual set up call
    setup (
        name = "ResourcePackage",
        version = "1.0.1",
        description = "Automated resource-as-package embedding mechanism",
        author = "Mike C. Fletcher",
        author_email = "mcfletch@users.sourceforge.net",
        url = "http://resourcepackage.sourceforge.net",
        license = "BSD-style, see license.txt for details",

        package_dir = {
            'resourcepackage':'resourcepackage',
        },

        packages = [
            'resourcepackage', 
            'resourcepackage.testres',
            'resourcepackage.testwx',
        ],
        # non python files of examples      
        include_package_data=True,
        **extraArguments
    )
    
