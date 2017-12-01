
import argparse
import warnings

import numpy as np
import obspy
import pyasdf

from os.path import exists, join

from asdf_converters.util.util import load


def getargs():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str,
        help='SAC input filename')

    parser.add_argument('output', type=str,
        help='ASDF output filename')

    parser.add_argument('tag', type=str,
        help='ASDF tag',
        nargs='?',
        default='converted_from_su')

    return parser.parse_args()


# ASDF2SAC
if __name__=='__main__':
    args = getargs()

    if not exists(args.input):
        raise Exception("File not found: %s" % args.input)

    if exists(args.output):
        raise Exception("File already exists: %s" % args.output)

    ds = pyasdf.ASDFDataSet(args.input)

    # retrieve SAC headers from ASDF auxiliary data
    headers = []
    if hasattr(ds.auxiliary_data.Files, 'SUHeaders'):
        headers = load(ds.auxiliary_data.Files.SUHeaders.data)

    stream = obspy.core.stream.Stream()
    for _i, waveforms in enumerate(ds.waveforms):
        trace = waveforms[args.tag][0]
        trace.stats.su = headers[_i]
        stream += trace

    # write data
    stream.write(args.output, format='SU')


