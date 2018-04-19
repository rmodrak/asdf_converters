#!/bin/bash -e

cd $(dirname ${BASH_SOURCE[0]})
export PYTHONPATH=$PYTHONPATH:$(dirname $PWD)

rm -rf $PWD/data/output.h5
../asdf_converters/sac2asdf.py data/20090407201255351 data/output.h5 && echo "SUCCESS"

