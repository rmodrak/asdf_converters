
import argparse
import collections
import io
import glob

import numpy as np
import obspy

from os.path import exists, join
from asdf_converters.util.sac import read_sac_files, get_event_coords, get_station_coords
from pyasdf import ASDFDataSet



def getargs():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str,
        help='SAC input directory')

    parser.add_argument('output', type=str,
        help='ASDF output filename')

    parser.add_argument('tag', type=str,
        help='ASDF tag')

    return parser.parse_args()


def get_event_id():
    return obspy.core.event.ResourceIdentifier()


def sort_by_station(channels):
    stations = collections.defaultdict(list)
    for trace_id, coords in channels.items():
        network, station, location_code, channel = trace_id.split('.')
        stations[(network, station)] += [(location_code, channel,) + coords]
    return stations.items()


def load(buffer, **kwds):
    """Load an object that was stored as an ASDF auxiliary data file
    """
    import dill
    from io import BytesIO
    value = getattr(buffer, 'value', buffer)
    return dill.load(BytesIO(value))


def dump(object, **kwds):
    """ Dumps an object to a dill virtual file
    """
    import dill
    from io import BytesIO
    file = BytesIO()
    dill.dump(object, file)
    file.seek(0)
    return file

    

# SAC2ASDF
if __name__=='__main__':
    args = getargs()

    if not exists(args.input):
        raise Exception("File not found:." % args.input)

    if exists(args.output):
        raise Exception("File exists: %s" % args.output)

    wildcard = '*.sac'
    files = glob.glob(join(args.input, wildcard))
    stream = read_sac_files(files)
    ds = ASDFDataSet(args.output, mode='a')

    headers = {}
    events = {}
    channels = {}

    starttime = np.inf
    endtime = -np.inf

    for trace in stream:
        print(trace.stats.sac_filename)

        # keep track of headers
        sac_header = trace.stats.sac
        sac_filename = trace.stats.sac_filename
        headers[sac_filename] = sac_header

        # keep track of events
        coords = get_event_coords(sac_header)
        if coords in events:
            event_id = events[coords]
        else:
            event_id = get_event_id()
            events[coords] = event_id

        # keep track of channels
        coords = get_station_coords(sac_header)
        name = trace.id
        channels[name] = coords

        # keep track of recording times
        s, e = trace.stats.starttime, trace.stats.endtime
        if s.timestamp < starttime:
            starttime = s
        if e.timestamp > endtime:
            endtime = e

        ds.add_waveforms(trace, args.tag, event_id)

    # add events
    catalog = obspy.core.event.Catalog()
    for event_coords, event_id in events.items():
        latitude, longitude, depth, origin_time = event_coords
        origin = obspy.core.event.Origin(
            time=origin_time,
            longitude=longitude,
            latitude=latitude,
            depth=depth)
        catalog.append(obspy.core.event.Event(
            resource_id=event_id,
            origins=[origin]))
    ds.add_quakeml(catalog)

    # add stations
    for group1, group2 in sort_by_station(channels):
        network, station = group1
        for location_code, channel, latitude, longitude, depth, elevation in group2:
            inventory = obspy.core.inventory.Inventory(
                networks=[obspy.core.inventory.Network(
                    code=network, 
                    stations=[obspy.core.inventory.Station(
                        code=station, 
                        latitude=group2[0][2],
                        longitude=group2[0][3],
                        elevation=group2[0][4],
                        start_date=starttime,
                        end_date=endtime,
                        creation_date=obspy.UTCDateTime(),
                        site=obspy.core.inventory.Site(name=""),
                        channels=[obspy.core.inventory.Channel(
                            code=channel,
                            location_code=location_code,
                            latitude=latitude,
                            longitude=longitude,
                            elevation=elevation,
                            depth=depth,
                            start_date=starttime,
                            end_date=endtime)])])],                 
                source="pyasdf sac2asdf converter")
            ds.add_stationxml(inventory)

    # add sac_headers as auxiliary data
    ds.add_auxiliary_data_file(
        dump(headers),
        path='SacHeaders')

    del ds

