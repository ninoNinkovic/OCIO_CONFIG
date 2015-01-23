'''


99.9% of code repurposed from an early verion of hpd's LUT code. Please
go here to review his latest:
https://github.com/hpd/OpenColorIO-Configs/tree/master/aces_1.0.0/python/aces_ocio


This is very rudimentary just enough to proces out this single 1D LUT 
needed for shaping. Look at bottom of file for hard coded paths 
and parameters.

This file used to make a 1D shaper for some Display Referred
exr images that Technicolor provided to MPEG where exe 1.0 
is 1 nit and that have exterme dynamic range thats why 
scaled to goto past 2^13


usage from command line, from the same directory as this file
python DisplayRefCreateShaper.py  



'''

import sys
import os
import array
import shutil
import string

import OpenImageIO as oiio
import PyOpenColorIO as OCIO

import process

#
# Functions used to generate LUTs using CTL transforms
#
def convertBitDepth(inputImage, outputImage, depth):
    args = [inputImage, "-d", depth, "-o", outputImage]
    convert = process.Process(description="convert image bit depth", cmd="oiiotool", args=args)
    convert.execute()  

def generate1dLUTFromCTL(lutPath, 
    ctlPaths, 
    lutResolution=1024, 
    identityLutBitDepth='half', 
    inputScale=1.0, 
    outputScale=1.0,
    globalParams={},
    cleanup=True,
    acesCTLReleaseDir=None,
    minValue=0.0,
    maxValue=1.0):
    #print( lutPath )
    #print( ctlPaths )

    lutPathBase = os.path.splitext(lutPath)[0]

    identityLUTImageFloat = lutPathBase + ".float.tiff"
    generate1dLUTImage(identityLUTImageFloat, lutResolution, minValue, maxValue)

    if identityLutBitDepth != 'half':
        identityLUTImage = lutPathBase + ".uint16.tiff"
        convertBitDepth(identityLUTImageFloat, identityLUTImage, identityLutBitDepth)
    else:
        identityLUTImage = identityLUTImageFloat

    transformedLUTImage = lutPathBase + ".transformed.exr"
    applyCTLToImage(identityLUTImage, transformedLUTImage, ctlPaths, inputScale, outputScale, globalParams, acesCTLReleaseDir)

    generate1dLUTFromImage(transformedLUTImage, lutPath, minValue, maxValue)

    if cleanup:
        os.remove(identityLUTImage)
        if identityLUTImage != identityLUTImageFloat:
            os.remove(identityLUTImageFloat)
        os.remove(transformedLUTImage)
        
        
def applyCTLToImage(inputImage, 
    outputImage, 
    ctlPaths=[], 
    inputScale=1.0, 
    outputScale=1.0, 
    globalParams={},
    acesCTLReleaseDir=None):
    if len(ctlPaths) > 0:
        ctlenv = os.environ
        if acesCTLReleaseDir != None:
            ctlModulePath = "%s/utilities" % acesCTLReleaseDir
            ctlenv['CTL_MODULE_PATH'] = ctlModulePath

        args = []
        for ctl in ctlPaths:
            args += ['-ctl', ctl]
        args += ["-force"]
        #args += ["-verbose"]
        args += ["-input_scale", str(inputScale)]
        args += ["-output_scale", str(outputScale)]
        args += ["-global_param1", "aIn", "1.0"]
        for key, value in globalParams.iteritems():
            args += ["-global_param1", key, str(value)]
        args += [inputImage]
        args += [outputImage]

        #print( "args : %s" % args )

        ctlp = process.Process(description="a ctlrender process", cmd="ctlrender", args=args, env=ctlenv )

        ctlp.execute()        


def generate1dLUTImage(ramp1dPath, resolution=1024, minValue=0.0, maxValue=1.0):
    print( "Generate 1d LUT image - %s" % ramp1dPath)

    # open image
    format = os.path.splitext(ramp1dPath)[1]
    ramp = oiio.ImageOutput.create(ramp1dPath)

    # set image specs
    spec = oiio.ImageSpec()
    spec.set_format( oiio.FLOAT )
    #spec.format.basetype = oiio.FLOAT
    spec.width = resolution
    spec.height = 1
    spec.nchannels = 3

    ramp.open (ramp1dPath, spec, oiio.Create)

    data = array.array("f", "\0" * spec.width * spec.height * spec.nchannels * 4)
    for i in range(resolution):
        value = float(i)/(resolution-1) * (maxValue - minValue) + minValue
        data[i*spec.nchannels +0] = value
        data[i*spec.nchannels +1] = value
        data[i*spec.nchannels +2] = value

    ramp.write_image(spec.format, data)
    
    #print(spec.nchannels)
    #print(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8])    
    
    ramp.close()

# Credit to Alex Fry for the original single channel version of the spi1d writer
def WriteSPI1D(filename, fromMin, fromMax, data, entries, channels):
    f = file(filename,'w')
    f.write("Version 1\n")
    f.write("From %f %f\n" % (fromMin, fromMax))
    f.write("Length %d\n" % entries)
    f.write("Components %d\n" % (min(3, channels)) )
    f.write("{\n")
    for i in range(0, entries):
#    for i in range(0, 5):
        entry = ""
        for j in range(0, min(3, channels)):
            entry = "%s %f" % (entry, data[i*channels + j])
        f.write("        %s\n" % entry)
    f.write("}\n")
    f.close()

    print(entry)

def generate1dLUTFromImage(ramp1dPath, outputPath=None, minValue=0.0, maxValue=1.0):
    if outputPath == None:
        outputPath = ramp1dPath + ".spi1d"

    # open image
    ramp = oiio.ImageInput.open( ramp1dPath )

    # get image specs
    spec = ramp.spec()
    type = spec.format.basetype
    width = spec.width
    height = spec.height
    channels = spec.nchannels


    # get data
    # Force data to be read as float. The Python API doesn't handle half-floats well yet.
    type = oiio.FLOAT
    data = ramp.read_image(type)

    WriteSPI1D(outputPath, minValue, maxValue, data, width, channels)

#
# Main
#
def main():
    import optparse

    p = optparse.OptionParser(description='An 1D shaper LUT generation script',
                                prog='createShaper',
                                version=' 0.1',
                                usage='%prog [options]')
    p.add_option('--lutResolution1d', default=10000)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    lutResolution1d  = int(options.lutResolution1d)
    cleanupTempImages  = False

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []


 
    #
    # Generate the shaper
    #
    shaperInputScale = 1.0
    outputScale=1.0
    cleanup=False
    acesCTLReleaseDir=None
    
#"/home/qbit/Documents/EDR/ACES/HP/acesOCIOConfigGeneration_v005/ctl/logShaper/aces_to_logShaper16i_param.ctl",     

    generate1dLUTFromCTL( "DisplayRefPQShaper.spi1d", 
		["DisplayRefPQ_Shaper.ctl"], 
		lutResolution1d, 
		'half', 
		1.0/shaperInputScale,
		outputScale, 
		{},
		cleanup, 
		acesCTLReleaseDir,
		2.0**-7.64,
		2.0**13.3)    

# main

if __name__ == '__main__':
    main()
