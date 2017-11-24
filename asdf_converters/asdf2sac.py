
import argparse

import numpy as np
import obspy
import pyasdf

from os.path import exists, join


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


def load(buffer, **kwds):
    """Load an object that was stored as an ASDF auxiliary data file
    """
    import dill
    from io import BytesIO
    value = getattr(buffer, 'value', buffer)
    return dill.load(BytesIO(value))


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
        headers = load(ds.auxiliary_data.Files.SacHeaders.data)

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


