"""wxPython-specific data-as-code extensions to defaultgenerators"""
from resourcepackage import defaultgenerators
from wxPython.wx import *
from wxPython.tools import img2img
import tempfile, os

formats = [
	'.png', '.jpg', '.ico', '.tif', '.bmp',
	'.xpm', '.gif', '.pcx', '.pnm', '.iff',
	'.jpeg', '.tiff',
]

HEADER = '''
### wxPython specific functions
originalExtension = %(extension)r
from wxPython.wx import wxImageFromStream, wxBitmapFromImage, wxEmptyIcon
import cStringIO
def getData( ):
	"""Return the data from the resource as a simple string"""
	return data
def getImage( ):
	"""Return the data from the resource as a wxImage"""
	stream = cStringIO.StringIO(data)
	return wxImageFromStream(stream)
def getBitmap( ):
	"""Return the data from the resource as a wxBitmap"""
	return wxBitmapFromImage(getImage())
def getIcon( ):
	"""Return the data from the resource as a wxIcon"""
	icon = wxEmptyIcon()
	icon.CopyFromBitmap(getBitmap())
	return icon
'''
wxInitAllImageHandlers()
class wxImageGenerator( defaultgenerators.SimpleGenerator ):
	"""wxPython specific handling of Image formats"""
	def getHeader( self, source, destination, package=None ):
		"""Get the header, written before the data variable"""
		baseName, extension = os.path.splitext( source )
		source = baseName + '.png'
		base = defaultgenerators.SimpleGenerator.getHeader(
			self, source, destination, package
		)
		return base + (HEADER%locals())
		
	def getData( self, source, package=None ):
		"""Get the image as a .png-encoded string

		This is adapted directly from img2py.py
		"""
		tfname = tempfile.mktemp()
		ok, msg = img2img.convert(
			source,
			None, # don't support resetting the mask value
			None,
			tfname,
			wxBITMAP_TYPE_PNG,
			".png",
		)
		if not ok:
			raise ValueError ("""Unable to convert file %s to a png image for %s: %s"""%( source, package, msg))
		fh = open(tfname, "rb")
		try:
			data = fh.read()
		finally:
			fh.close()
			os.remove( tfname )
		return data
	

GENERATOR = wxImageGenerator()

generators = {
}
for format in formats:
	generators[ format ] = GENERATOR
