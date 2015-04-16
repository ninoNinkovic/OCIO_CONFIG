#!/bin/bash

# 0.0000019180  -18.991965849
# 15.7761012587  3.97966881166

set -x

python SceneRefCreateShaper.py

sleep 3

python DisplayRefCreateShaper.py

ls -l *spi1d

cp -fv *spi1d ../luts

pushd .
cd $EDRHOME/ACES/HPD/python 
rm 1D.ctf
python  ./convertLUTtoCLF.py -i ../../../OCIO_CONFIG/luts/SceneRefPQ_Shaper.spi1d -o 1D.ctf
more 1D.ctf
popd

