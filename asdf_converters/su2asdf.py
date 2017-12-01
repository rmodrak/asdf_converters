
import argparse
import collections
import io
import glob
import numpy as np
import obspy

from os.path import exists, join
from pyasdf import ASDFDataSet
from asdf_converters.util.su import get_source_coords, get_receiver_coords, unpack
from asdf_converters.util.util import dump




def getargs():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str,
        help='SU input filename')

    parser.add_argument('output', type=str,
        help='ASDF output filename')

    parser.add_argument('tag', type=str, 
        help='ASDF tag',
        nargs='?',
        default='converted_from_su')

    return parser.parse_args()


def get_source_id():
    return obspy.core.event.ResourceIdentifier()



# SU2ASDF
if __name__=='__main__':
    """
    Converts SeismicUnix (SU) to ASDF

     - SU trace headers are preserved in a dill auxiliary file
     - Attempts to write QuakeML from SU trace header metadata
     - Currently, no attempt is made to write StationXML
    """

    args = getargs()

    if not exists(args.input):
        raise Exception("File not found: %s" % args.input)

    if exists(args.output):
        raise Exception("File exists: %s" % args.output)

    try:
        stream = obspy.read(args.input, format='SU', byteorder='<')
    except:
        try:
            stream = obspy.read(args.input, format='SU', byteorder='>')
        except:
            raise Exception('Error reading SU file')

    ds = ASDFDataSet(args.output, mode='a')

    headers = []
    sources = {}
    receivers = {}

    for _i, trace in enumerate(stream):
        # keep track of headers
        su_header = trace.stats.su.trace_header
        headers += [unpack(su_header)]

        # keep track of sources
        coords = get_source_coords(trace)
        if coords in sources:
            source_id = sources[coords]
        else:
            source_id = get_source_id()
            sources[coords] = source_id

        # use trace index in place of network/station/channel
        trace.stats.station = _i

        # keep track of receivers
        coords = get_receiver_coords(trace)
        if coords in sources:
            source_id = sources[coords]
        else:
            source_id = get_source_id()
            sources[coords] = source_id

        ds.add_waveforms(trace, args.tag, source_id)

    # add events 
    # longitude = source_coord_x, latitude = source_coord_y
    catalog = obspy.core.event.Catalog()
    for source_coords, source_id in sources.items():
        latitude, longitude, depth  = source_coords
        origin = obspy.core.event.Origin(
            latitude=coords[0],
            longitude=coords[1],
            depth=coords[2])
        catalog.append(obspy.core.event.Event(
            resource_id=source_id,
            origins=[origin]))
    ds.add_quakeml(catalog)


    # add su_headers as auxiliary data
    ds.add_auxiliary_data_file(
        dump(headers),
        path='SUHeaders')
    del ds

