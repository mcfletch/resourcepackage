#!/usr/bin/env python
"""Script for extracting resources from a resource package"""

usage = """extract.py [-f] packageName [modules, ...]

packageName -- dotted python package name for the package
	which holds the resource to be extracted.  The package
	__init__.py file should include a Package instance named
	"package".  If not, a new default package instance will
	be created for the given package.
	
modules -- optional list of individual modules to be
	extracted, otherwise scans the package directory
	to determine the modules to extract.

-f -- flag to signal that extraction should be "forced",
	that is, that the relative dates of the module and any
	existing resource file should be ignored, and the
	extraction should always occur.

Note:
	Because the extraction process needs to import the
	package, any automatic scanning done by your __init__.py
	may cause modules to be updated from their resources.
	
	As a result, if there is a newer resource file which
	would generate the module you are seeking to extract,
	the module will be overwritten before the extraction
	and you'll get a copy of the already-present resource
	file.  To avoid this, delete all copies of the resource
	files you would like to extract before running extract.py

"""
import os, string

def main( packageName, modules=(), force=0):
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
	if modules:
		for module in modules:
			packageObject.extractFile( module, force )
	else:
		packageObject.extract( force )

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
			print usage
			print 'ERR: arguments received', sys.argv[1:]
	else:
		print usage
			
	

		