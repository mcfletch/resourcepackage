ResourcePackage for Python
=================

ResourcePackage is a mechanism for automatically managing `resources`
(i.e. non-Python files: small images, documentation files, binary data)
embedded in Python modules (as Python source code), particularly for
those wishing to create re-usable Python packages which require their
own resource-sets where you don't want to rely on run-time package 
registration support (i.e. pkg_resources).

Usage
-----

Install as a standard Python module (using setuptools). Note that 
ResourcePackage and setuptools are *not* required by the 
*generated* resource packages::

    pip install ResourcePackage

ResourcePackage allows you to set up resource-specific sub-packages
within your package. It creates a Python module for each resource
placed in the resource package's directory during development. You can
set up these packages simply by copying an __init__.py file and then
use the resources saved/updated in the package directory like so::

    from mypackage.resources import open_ico
    result = myStringLoadingFunction( open_ico.data )

ResourcePackage scans the package-directory on import to refresh
module contents, so simply saving an updated version of the file will
make it available the next time your application is run.

When you are ready to distribute your package, you need only replace
the copied __init__.py file with a dummy __init__.py to disable the
scanning support and eliminate all dependencies on resourcepackage
(that is, your users do not need to have resourcepackage installed 
once this is done).

Users of your packages do not need to do anything special when
creating their applications to give you access to your resources, as
they are simply Python packages/modules included in your package's
hierarchy. Your package's code (other than the mentioned __init__.py)
doesn't change. Similarly, automatic packaging systems will pick
up your resources as regular Python modules being imported by your
source-code.

There are two utility scripts, extract.py and scan.py which can be
used to manually extract or embed resources in a resourcepackage
package even if the package no longer has a resourcepackage-aware 
__init__.py file. See these scripts for usage details.

Status
------

ResourcePackage is ancient code at this point. It has been stable and 
working for so long it was still hosted on CVS in 2015. The only point 
in creating the new (2015 release) is to address packaging/pip-installation 
and python3 support.

Python 3 support is *definitely* not there yet. Python 3 doesn't allow 
extended characters in byte-strings (even with coding set), so we can't 
use the original approach to embedding, but the current approach wastes 
a lot of space.
