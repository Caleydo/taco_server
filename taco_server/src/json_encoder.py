"""
Serializer to avoid default usage of numpy integer/float/bytes/etc.
"""
import json
import numpy


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.int64):
            return int(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        elif isinstance(obj, numpy.bytes_):
            return obj.decode('utf-8')
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(JsonEncoder, self).default(obj)
