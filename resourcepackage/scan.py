#!/usr/bin/env python
"""Script for scanning/updating resources into a resource package"""

usage = """scan.py [-f] packageName [filenames, ...]

packageName -- dotted Python package name for the package
    to be scanned.  If the Python package __init__.py
    includes a package instance named "package" it will
    be used for extraction.  If not, a new default
    package instance will be created for the given package.
    
filenames -- optional list of individual files to be
    updated, otherwise scans the package directory
    to determine the modules to create/update.

-f -- flag to signal that updates should be "forced",
    that is, that the relative dates of the resource file
    and any existing module should be ignored, and the
    embedding/encoding/updating should always occur.

Note:
    Because the scanning process needs to import the
    package, any automatic scanning done by your __init__.py
    may cause modules to be updated from their resources
    before scan.py starts working.

"""
import os, string

def main( packageName, filenames=(), force=0):
    """Perform the actual extraction"""
    packageModule = __import__(
        packageName, {}, {},
        string.split(packageName, '.')
    )
    if not hasattr( packageModule, 'package' ):
        # build the default package object...
        from resourcepackage import package
        packageObject = package.Package(
            packageModule.__name__,
            directory = os.path.dirname( os.path.abspath(packageModule.__file__) ),
        )
    else:
        packageObject = packageModule.package
    if filenames:
        for filename in filenames:
            packageObject.scanFile( source = filename, force=force )
    else:
        packageObject.scan( force=force )

if __name__ == "__main__":
    import sys
    arguments = sys.argv[1:]
    try:
        import logging
        # this is wrong, should be done at the app level :( 
        log = logging.getLogger( "resourcepackage" )
        log.setLevel( logging.INFO )
        logging.basicConfig()
    except ImportError:
        log = None
    if arguments:
        # do we have a force...
        force = arguments[0] == '-f'
        if force:
            del arguments[0]
        if arguments:
            packageName = arguments[0]
            modules = arguments[1:]
            main( packageName, modules, force=force )
        else:
            print(usage)
            print('ERR: arguments received', sys.argv[1:])
    else:
        print(usage)
            