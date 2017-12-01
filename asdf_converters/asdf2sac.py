
import argparse
import warnings

import numpy as np
import obspy
import pyasdf

from os.path import exists, join

from asdf_converters.util.util import loadjson


def getargs():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str,
        help='SAC input filename')

    parser.add_argument('output', type=str,
        help='ASDF output filename')

    parser.add_argument('tag', type=str,
        help='ASDF tag',
        nargs='?',
        default='converted_from_sac')

    return parser.parse_args()


# ASDF2SAC
if __name__=='__main__':
    args = getargs()

    if not exists(args.input):
        raise Exception("File not found:." % args.input)

    if not exists(args.output):
        raise Exception("Directory not found: %s" % args.output)

    ds = pyasdf.ASDFDataSet(args.input)

    # retrieve SAC headers from ASDF auxiliary data
    headers = {}
    if hasattr(ds.auxiliary_data.Files, 'SacHeaders'):
        headers = loadjson(ds.auxiliary_data.Files.SacHeaders.data)

    for station in ds.waveforms:
        for trace in station[args.tag]:

            # retrieve SAC filename
            try:
                filename = trace.stats.asdf.labels[0]
            except:
                filename = "%s.SAC" % trace.id
                warnings.warn(
                    "Original SAC filename not stored in asdf.labels. "
                    "Using trace.id instead:\n%s\n" % filename)

            # attach SAC header
            if filename in headers:
                trace.stats.sac = headers[filename]

            # write data
            fullname = join(args.output, filename)
            trace.write(fullname, format='sac')


