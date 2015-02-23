"""Package object, manages package-related operations
"""
import os, string, stat, traceback, types
from resourcepackage import defaultgenerators
try:
	import logging
	log = logging.getLogger( "resourcepackage" )
except ImportError:
	log = None

class Package:
	"""Represents an individual ResourcePackage at design-time

	Includes facilities for scanning (embedding) and extracting
	the package.
	"""
	directory = ""
	def __init__(
		self,
		packageName,
		directory,
		generators = defaultgenerators.generators,
	):
		"""Initialse the Repository

		directory -- the package's directory, in which we will
			do all of our work.
		"""
		self.packageName = packageName
		self.directory = directory
		self.generators = generators
	def __repr__( self ):
		return """%s (%s)"""%( self.__class__.__name__, self.packageName)

	# all-lowercased extensions and files to ignore
	ignoreExtensions = [ '.pyc','.pyo',]
	ignoreFiles = [ '__init__.py', ]

	def fileToName( self, filename ):
		"""Get Python module name and extension from filename

		This is a primary customisation point, as it allows you
		to choose the module-names in the package as generated
		by the system.  The default implementation does the
		following to the name:

			replaces all '.' with '_'
			replaces all ' ' with '_'

		So, obviously, there are cases where two different
		filenames will produce the same module name.  Those
		cases will be caught by the processing code and raise
		ValueErrors.

		Note that for case-in-sensitive file-systems, there
		will potentially be silent overwrites as files which
		differ only in case will not raise a ValueError.

		returns (base, extension)

			base -- processed filename
			extension -- lowercase-only version of the file
				extension, or "" if no extension was found.
		"""
		try:
			base, ext = os.path.splitext(filename)
		except ValueError:
			# there is no extension on the file...
			base, ext = filename, ''
		ext = string.lower(ext)
		# Alpha 3 changes, makes the module names less
		# consistent, but allows for more file-names to map
		# to unique module names
		#   Upper/lower-case is a tricky one,
		#   although I think they should be unified
		#   I'm guessing other's will want them unique
		#   base = string.lower( base )
		base = string.replace( filename, ".", "_" )
		base = string.replace( base, " ", "_" )
		return base, ext
		

	def isResource( self, file, ext ):
		"""Determine whether we consider this file a resource"""
		if not os.path.isfile( os.path.join( self.directory, file )):
			return 0
		file = string.lower( file )
		if (
			( ext not in self.ignoreExtensions ) and
			( file not in self.ignoreFiles ) and
			( ext != '.py' )
		):
			return 1
		return 0
			
	def scan( self, force=0 ):
		"""Scan the directory, looking for updated/added resources"""
		if log:
			log.info("""scan(force=%r) %s""", force, self )
		fileList = os.listdir( self.directory )
		nonPython = {}
		python = {}
		testFileNames = {}
		if log:
			log.debug("""filtering filename-list""" )
		for file in fileList:
			base, ext = self.fileToName( file )
			fullName = os.path.join( self.directory, file )
			if log:
				log.debug("""file=%r, base=%r, ext=%r""", file, base, ext )
			if self.isResource( file, ext ):
				if testFileNames.has_key( base ):
					raise ValueError(
						"""%s has two data files %s and %s which would generate the same Python module %s"""%(
							self, file, testFileNames[base]
						)
					)
				testFileNames[base] = file
				if log:
					log.debug("""will process""" )
				nonPython[file] = base, ext, fullName
			elif ext == '.py':
				python[base] = file, ext, fullName
		if log:
			log.debug("""starting updates, %s files""", len(nonPython) )
		for file,(base,ext,fullName) in nonPython.items():
			self.scanFile(
				file,
				base,
				extension=ext,
				force=force
			)
		if log:
			log.debug("""finished updates""")
	def scanFile( self, source, base=None, extension=None, force=0):
		"""Encode/update/scan a single file

		source -- full path name of the source-file
		base -- (optional) calculated base module name
		extension -- (optional) calculated lower-cased extension
		force -- whether to force update even if dates suggest
			the module is already up-to-date.

		Note: this does _not_ check to see if there is a filename
		conflict between resources, so potentially it could
		overwrite another source-file's destination module.
		"""
		if log:
			log.debug("""scanFile %r""", source )
		# since this can be called from scripts, not just
		# the scan method, we do a lot of redundant name-
		# mangling :(

		# This forced truncation makes some things possible,
		# and others not, for instance, you can't update into a
		# different directory from where the files are, but you
		# can specify the filenames as p:\whatever\whenever.gif
		# which in the imagined approach will be more common.
		source = os.path.basename( source )
		fullName = os.path.join( self.directory, source )
		if base is None or extension is None:
			base, extension = self.fileToName( source )
		moduleName = base + '.py'
		fullModuleName = os.path.join(self.directory, moduleName)
		
		# date-only check, is actually a redundant check for
		# calls from scan
		if (not force) and os.path.exists( fullModuleName ):
			if self.compareDates( fullName, fullModuleName ):
				if log:
					log.info("""file %r up to date""", moduleName )
				return 0
			else:
				if log:
					log.info("""refresh %r -> %r""", source, moduleName)
		elif force:
			if log:
				log.info("""force %r -> %r""", source, moduleName)
		else:
			if log:
				log.info("""new %r -> %r""", source, moduleName)
		# okay, one way or another we want to generate our
		# little Python file for this resource.  By default,
		# we're going to just dump the contents to a string.
		# a child can handle image-specific mechanisms...
		generator = self.getGenerator( extension )
		if log:
			log.debug("""generator %r""", generator )
		generator( fullName, fullModuleName, self )
		if log:
			log.debug("""scanFile %r finished""", source )
		return 1

	def getGenerator( self, extension="" ):
		"""Get a file-type-specific generator, or the default"""
		for ext in [ extension, "" ]:
			obj = self.generators.get( ext )
			if obj:
				return obj
		raise KeyError( """%s class has no default "generate" object (key "")!!!"""%(self.__class__))
	
				
	def compareDates( self, first, second ):
		"""Compare dates for two filenames

		This is it's own function so that a better
		comparison mechanism could be included easily.

		Returns boolean saying whether the first date is
		before-or-equal to the second
		"""
		try:
			firstTime = os.stat(first)[stat.ST_MTIME]
		except OSError:
			# first doesn't exist, so it's staler than
			# second for us...
			return 1
		try:
			secondTime = os.stat(second)[stat.ST_MTIME]
		except OSError:
			# second doesn't exist, so it's staler than
			# first for us...
			return 0
		return firstTime <= secondTime
	### Extracting back to disk files
	def isEncodedResource (self, file, ext ):
		"""Determine whether we consider this file an encoded resource module
		"""
		if not os.path.isfile( os.path.join( self.directory, file )):
			return 0
		if ext != '.py' or file == "__init__.py":
			return 0
		## OK, so it is definitely a python file...
		## for now, we will consider that sufficient...
		return 1
	def extract( self, force=0 ):
		"""Extract encoded files to disk files

		for each python source file other than __init__.py, we
		attempt to write:
			module.data to module.source

		if module.source doesn't exist, or is older,
		or force is true, then we write the file, otherwise
		we skip the file.
		"""
		if log:
			log.info("""scan(force=%r) %s""", force, self )
		fileList = filter ( self.isEncodedResource, os.listdir( self.directory ))
		for file in fileList:
			self.extractFile (module, force)

	def extractFile( self, module, force = 0 ):
		"""Extract a single file from source (python module) to destination"""
		# first question, should we do anything
		fullModule = os.path.join( self.directory, module)
		### Need to import the module to do anything...
		base, ext = self.fileToName( module )
		try:
			moduleObject = self.importModule(base)
		except Exception, err:
			if log:
				log.error( """Exception while attempting to extract module %s, %s""", module, err)
			return
		if hasattr( moduleObject, "data") and hasattr( moduleObject, "source"):
			fullDestination = os.path.join( self.directory, moduleObject.source)
			if force or not self.compareDates( fullModule, fullDestination):
				# okay, should write to the resource file...
				if log:
					log.info( """extract %s -> %s""", module, moduleObject.source)
				if isinstance( moduleObject.data, types.StringType ):
					fileHandle = open( fullDestination, 'wb')
					try:
						fileHandle.write( moduleObject.data )
					finally:
						fileHandle.close ()
					return 1
				else:
					if log:
						log.error( """module %s data attribute is not a string, is a %s""", module,type(moduleObject.data))
			else:
				if log:
					log.info( """resource file %s up-to-date""", fullDestination)
				
		else:
			if log:
				log.error( """Resource module %s does not define "data" and "source" attributes, cannot extract""", module)
			
	def importModule(self, baseName):
		"""Import the given module from our package and return the module object"""
		moduleName = string.split( self.packageName,'.')+[baseName]
		return __import__( string.join( moduleName, '.'), {}, {}, moduleName)

##
##if log:
##	log.setLevel( logging.WARN )
	