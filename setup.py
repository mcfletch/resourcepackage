#!/usr/bin/env python
"""Installs ResourcePackage using distutils

Run:
	python setup.py install
to install the package from the source archive.
"""

if __name__ == "__main__":
	import sys,os, string
	from distutils.sysconfig import *
	from distutils.core import setup,Extension
	from distutils.command.build_ext import build_ext
	from distutils.command.install import install
	from distutils.command.install_data import install_data
	##from my_install_data import *

	##############
	## Following is from Pete Shinners,
	## apparently it will work around the reported bug on
	## some unix machines where the data files are copied
	## to weird locations if the user's configuration options
	## were entered during the wrong phase of the moon :) .
	from distutils.command.install_data import install_data
	class smart_install_data(install_data):
		def run(self):
			#need to change self.install_dir to the library dir
			install_cmd = self.get_finalized_command('install')
			self.install_dir = getattr(install_cmd, 'install_lib')
			# should create the directory if it doesn't exist!!!
			return install_data.run(self)
	##############
	### The following automates the inclusion of files while avoiding problems with UNIX
	### where case sensitivity matters.
	dataFiles = []
	excludedTypes = ('.py','.pyc','.pyo', '.db', '.max','.gz','.bat')
	def nonPythonFile( file ):
		if string.lower( file ) == 'cvs':
			return 0
		else:
			return (os.path.splitext( file )[1]).lower() not in excludedTypes
	dataDirectories = [
		'.',
		'testres',
	]
	for directory in dataDirectories:
		finalFiles = []
		for file in os.listdir( directory):
			fullFile = os.path.join( directory, file )
			if os.path.isfile(fullFile) and nonPythonFile(fullFile):
				finalFiles.append (os.path.join(directory, file))
		if finalFiles:
			dataFiles.append (
				(os.path.join('resourcepackage',directory),finalFiles)
			)
	from sys import hexversion
	if hexversion >= 0x2030000:
		# work around distutils complaints under Python 2.2.x
		extraArguments = {
			'classifiers': [
				"""License :: OSI Approved :: BSD License""",
				"""Programming Language :: Python""",
				"""Topic :: Software Development :: Libraries :: Python Modules""",
				"""Intended Audience :: Developers""",
			],
			'download_url': "https://sourceforge.net/project/showfiles.php?group_id=71287",
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
	else:
		extraArguments = {
		}

	### Now the actual set up call
	setup (
		name = "ResourcePackage",
		version = "1.0.0",
		description = "Automated resource-as-package embedding mechanism",
		author = "Mike C. Fletcher",
		author_email = "mcfletch@users.sourceforge.net",
		url = "http://resourcepackage.sourceforge.net",
		license = "BSD-style, see license.txt for details",

		package_dir = {
			'resourcepackage':'.',
		},

		packages = [
			'resourcepackage', 
			'resourcepackage.testres',
			'resourcepackage.testwx',
		],
		# non python files of examples      
		data_files = dataFiles,
		cmdclass = {'install_data':smart_install_data},
		**extraArguments
	)
	
