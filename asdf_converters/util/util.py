
import dill
import json

import numpy as np
import obspy

from io import BytesIO


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, obspy.core.util.AttribDict):
            return dict(obj)
        elif isinstance(obj, obspy.UTCDateTime):
            return str(obj)
        # Numpy objects also require explicit handling.
        elif isinstance(obj, np.int64):
            return int(obj)
        elif isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.float64):
            return float(obj)
        elif isinstance(obj, np.float32):
            return float(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def load(buffer, **kwds):
    """Load an object that was stored as an ASDF auxiliary data file
    """
    value = getattr(buffer, 'value', buffer)
    return dill.load(BytesIO(value))


def dump(object, **kwds):
    """ Dumps an object to a dill virtual file
    """
    file = BytesIO()
    dill.dump(object, file)
    file.seek(0)
    return file


def loadjson(buffer, **kwds):
    """Load an object that was stored as an ASDF auxiliary data file
    """
    value = getattr(buffer, 'value', buffer)
    return json.load(BytesIO(value))


def dumpjson(object, **kwds):
    """ Dumps an object to a json virtual file
    """
    file = BytesIO()
    json.dump(object, file, cls=JSONEncoder)
    file.seek(0)
    return file


