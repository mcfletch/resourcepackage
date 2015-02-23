"""Objects for doing generic data-as-code encoding"""
import string, cStringIO, zlib, types, os
import resourcepackage

HEADER = '''# -*- coding: ISO-8859-1 -*-
"""Resource %(module)s (from file %(source)s)"""
# written by resourcepackage: %(resourcepackagev)r
source = %(source)r
package = %(packagen)r
'''
class SimpleGenerator:
    """Simplistic generator"""
    def __repr__( self ):
        return "%s (singleton)"%( self.__class__.__name__)
    def __call__( self, source, destination, package=None ):
        """Encode source in destination for package"""
        header = self.getHeader( source, destination, package )
        assert isinstance( header, types.StringType ), """Generator %s didn't return a String, returned %r"""%( self, header )
        data = self.getDataRepr( source, destination, package )
        assert isinstance( data, types.StringType ), """Generator %s didn't return a String, returned %r"""%( self, data )
        footer = self.getFooter( source, destination, package )
        assert isinstance( footer, types.StringType ), """Generator %s didn't return a String, returned %r"""%( self, footer )
        
        file = open(destination,'w')
        try:
            file.write( header )
            file.write( data )
            file.write( footer )
        finally:
            file.close()

    def getHeader( self, source, destination, package=None ):
        """Get the header, written before the data variable"""
        source = os.path.basename( source )
        module = os.path.splitext(os.path.basename( destination ))[0]
        resourcepackagev = resourcepackage.__version__
        packagen = package.packageName
        return HEADER % locals()
        
    def getDataRepr( self, source, destination, package=None ):
        """data as Python code assigning a value to variable "data" """
        return """data = %s\n"""%(
            crunch_data(
                self.getData(source)
            )
        )

    def getFooter( self, source, destination, package=None ):
        """Get the footer, written after the data variable"""
        return """### end\n"""
    
    def getData( self, source, package=None ):
        """Get the data to be encoded in the package"""
        return open(source,'rb').read()
        

class CompressedGenerator( SimpleGenerator ):
    """Adds Zlib compression and decompression to generator"""
    def getDataRepr( self, source, destination, package=None ):
        """data as Python code assigning a value to variable "data" """
        return """data = zlib.decompress(%s)\n"""%(
            crunch_data(
                self.getData(source)
            )
        )
    def getData( self, source, package=None ):
        """Get the data to be encoded in the package"""
        data = SimpleGenerator.getData( self, source, package )
        return zlib.compress( data, 9 )
    def getHeader( self, source, destination, package=None ):
        """Get the header, written before the data variable"""
        base = SimpleGenerator.getHeader( self, source, destination, package )
        return base + """\nimport zlib\n"""


_char_map = {
}
for c in range(32):
    
    _char_map[ chr(c)] = '\\%03o'%(c)
_char_map['"'] = '\\"'
_char_map['\\'] = '\\\\'

def crunch_data(source, chunkSize=60, charMap = _char_map ):
    """Try to get a minimal representation of a binary as Python code

    This is a re-implementation that tries to
    minimise the size of the data by embedding extended
    characters in the source code.
    """
    result = []
    lastIndex = 0
    for index in xrange(0, len(source), chunkSize):
        sresult = "".join([
            charMap.get( char, char)
            for char in source[index:index+chunkSize]
        ])
        result.append( sresult )
    return '"%s"'%( '\\\n'.join( result ))

SIMPLE = SimpleGenerator()
COMPRESSED = CompressedGenerator()

generators = {
    "": SIMPLE,
    ".txt": COMPRESSED,
    ".html": COMPRESSED,
    ".htm": COMPRESSED,
    ".pdf":COMPRESSED,
}
