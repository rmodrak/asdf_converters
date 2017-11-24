
import glob
import os
import warnings

from os.path import basename, join

import numpy as np
import obspy
from obspy.core import Stream, Stats, Trace
from obspy.core.event import Event, Origin
from obspy.core.inventory import Inventory, Station


def read_sac_files(files):
    stream = obspy.core.Stream()
    for filename in files:
        try:
            _fromfile = obspy.read(filename, format='sac')
            trace = _fromfile[0]
        except:
            print("\nFailed to read '%s' as a SAC file." % filename)
            continue

        # keep track of original filename
        # (does not survive conversion to ASDF)
        trace.sac_filename = basename(filename)

        stream += _fromfile

    return stream


def get_event_coords(sac_headers):
    # location
    try:
        latitude = sac_headers.evla
        longitude = sac_headers.evlo
    except (TypeError, ValueError):
        warnings.warn("Could not determine event location from sac headers. "
                      "Setting location to nan...")
        latitude = np.nan
        longitudue = np.nan

    # depth
    try:
        depth = sac_headers.evdp
    except (TypeError, ValueError):
        warnings.warn("Could not determine event depth from sac headers. "
                      "Setting depth to nan...")
        depth = 0.

    # origin time
    try:
        origin_time = obspy.UTCDateTime(
            year=sac_headers.nzyear,
            julday=sac_headers.nzjday, 
            hour=sac_headers.nzhour, 
            minute=sac_headers.nzmin,
            second=sac_headers.nzsec) 
    except (TypeError, ValueError):
        warnings.warn("Could not determine origin time from sac headers. "
                      "Setting origin time to zero...")
        origin_time = obspy.UTCDateTime(0)

    return (
        latitude,
        longitude,
        depth,
        origin_time.timestamp,
        )

    #return Origin(
    #    time=origin_time,
    #    longitude=sac_headers.evlo,
    #    latitude=sac_headers.evla,
    #    depth=depth * 1000.0,
    #)


def get_station_coords(sac_headers):
    """ Creates station object based on sac metadata
    """
    # location
    try:
        latitude = sac_headers.stla
        longitude = sac_headers.stlo
    except:
        warnings.warn("Could not determine station location from sac headers. "
                      "Setting location to zero.")
        latitude = 0.
        longitude = 0.

    # elevation
    try:
        elevation = sac_headers.stel
        depth = 0.#depth = sac_headers.stdp
    except:
        warnings.warn("Could not determine station elevation from sac headers. "
                      "Setting elevation to zero.")
        elevation = 0.
        depth = 0.
    return (
       latitude,
       longitude,
       elevation,
       depth,
       )


def get_station_list(stream):
    """ Creates station list from sac metadata
    """
    stations = []
    for trace in stream:
        station_name = trace.station
        try:
            latitude = trace.stats.sac.stla
            longitude = trace.stats.sac.stlo
            elevation = 0.
        except:
            warnings.warn("Could not determine station location from sac headers.")
        stations += [Station(
           station_name,
           latitude,
           longitude,
           elevation)]
    return stations



