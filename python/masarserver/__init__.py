"""
MASAR server package.  The live service is the pure-Python p4p/PVXS
implementation in masarServer_p4p.py, which uses the pymasarsqlite backend
directly.  The legacy dslPY backend-selector layer has been removed.
"""

__version__ = '1.0.0'

__all__ = ['version']
