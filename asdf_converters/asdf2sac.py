

def getargs():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str,
        help='SAC input filename')

    parser.add_argument('output', type=str,
        help='ASDF output filename')

    return parser.parse_args()


def read_bytesio():
    raise NotImplementedError

def get_data():
    raise NotImplementedError

def get_sac_headers():
    raise NotImplementedError


# ASDF2SAC
if __name__=='__main__':
    args = getargs()

    if not exists(args.input):
        raise Exception("File not found:." % args.input)

    if exists(args.output):
        raise Exception("File exists: %s" % args.output)

    ds = ASDFDataSet(args.input)

    # get data from ASDF files
    stream = get_data(ds)
    sac_headers = get_sac_headers(s)
    del ds

    for _i, trace in enumerate(stream):
        # work around obspy data type conversion
        trace.data = stream.data.astype(np.float32)

        # attach SAC header
        trace.stats.sac = sac_headers[_i]

        # write data
        fullname = join(args.output, trace.sac_filename)
        data.write(fullname, format='sac')

