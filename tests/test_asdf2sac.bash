#!/bin/bash -e

cd $(dirname ${BASH_SOURCE[0]})
export PYTHONPATH=$PYTHONPATH:$(dirname $PWD)
OUTPUT="$PWD/data/output"

rm -rf $OUTPUT
mkdir -p $OUTPUT
../asdf_converters/asdf2sac.py data/20090407201255351.h5 $OUTPUT && echo "SUCCESS"

