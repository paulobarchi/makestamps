#!env python
import os
import sys
import h5py as h5
import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np


def fal(filename, skip_comments=True):
    with open(filename, "r") as f:
        lines = f.readlines()
    if skip_comments:
        return [l.strip() for l in lines if not l.startswith("#")]
    else:
        return [l.strip() for l in lines]


def progbar(current, to, width=40, show=True, message=None, stderr=False):
    percent = float(current) / float(to)
    length = int(width * percent)
    if show:
        count = " (%d/%d)    " % (current, to)
    else:
        count = ""
    if message:
        count += message
    outstream = sys.stderr if stderr else sys.stdout
    outstream.write(("\r[" + ("#" * length) + " " * (width - length) +
                     "] %0d" % (percent * 100)) + "%" + count)
    outstream.flush()

def saveImgFromFitsData(fileName, imageData):
    # if we were supposed to cut...
    # maxX, maxY = len(imageData[0]), len(imageData)
    # img2plt = imageData[int(0.2*maxX):int(0.8*maxX),int(0.2*maxY):int(0.8*maxY)]

    plt.imshow(imageData, cmap='gray',
        # norm=colors.LogNorm(vmin=np.median(imageData),vmax=np.median(imageData)+100))
        norm=colors.LogNorm(vmin=np.median(imageData),vmax=np.percentile(imageData,98)))
    plt.box(False)
    plt.tick_params(
            axis='both', 
            which='both', 
            bottom=False, 
            top=False, 
            labelbottom=False, 
            right=False, 
            left=False, 
            labelleft=False)
    plt.savefig(fileName, bbox_inches='tight')#, transparent=True, pad_inches=0)
    plt.clf()

def extract_objects(datastore, objids, outdir, band):
    if objids is None:
        extract_all(datastore, outdir, band)
        return
    else:
        extract_some(objids, datastore, outdir, band)


def extract_some(ids, datastore, outdir, band):
    todo = len(ids)
    done = 0
    # ct.progbar(done, todo)
    with h5.File(datastore, "r") as f:
        ds = f['/stamps/']
        for tile in ds:
            data = ds[tile + "/data"]
            headers = ds[tile + "/header"]
            objids = ds[tile + "/catalog"]
            N = data.shape[0]
            for i in range(N):
                objid = objids[i].strip()
                if objid in ids:
                    done += 1
                    # ct.progbar(done, todo)
                    heads = headers[i]
                    # for b in range(len(bands)):
                        # band_name = bands[b]
                    d = data[i, :, :, 1]
                    # head = pyfits.Header.fromstring(heads[b].strip())
                    fileName = "%s/%s_%s.png" % (outdir, objid, band)
                    # saving to png
                    saveImgFromFitsData(fileName, d)
                    # if we were saving in fits...
                    # outfits = pyfits.PrimaryHDU(data=d)
                    # outfits.writeto(filename, overwrite=True)


def make_rgb(datastore, outdir):
    pass


def extract_all(datastore, outdir, band):
    with h5.File(datastore, "r") as f:
        ds = f['/stamps/']
        for tile in ds:
            data = ds[tile + "/data"]
            headers = ds[tile + "/header"]
            objids = ds[tile + "/catalog"]
            N = data.shape[0]
            for i in range(N):
                objid = objids[i].strip()
                heads = headers[i]
                # for b in range(len(bands)):
                # band_name = bands[b]
                d = data[i, :, :, 1]+1000
                # head = pyfits.Header.fromstring(heads[b].strip())
                fileName = "%s/%s_%s.png" % (outdir, objid, band)
                
                # if you need to check matrix values, uncomment block below
                # np.set_printoptions(suppress=True, threshold=sys.maxsize)
                # print(d)
                # exit()

                # saving to png
                saveImgFromFitsData(fileName, d)
                # if we were saving in fits...
                # outfits = pyfits.PrimaryHDU(data=d)
                # outfits.writeto(filename, overwrite=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("image_extract <datastore> <dest_dir> <bands> [objids]")
        sys.exit(0)

    datastore = sys.argv[1]
    outdir = sys.argv[2]

    # if len(sys.argv) > 3 (script+2args), bands should be there
    band = "r" # "my" default
    # bands = "grizY" # old default
    if len(sys.argv) > 3:
        inputs = sys.argv[3]

    # only check for inputs if len(sys.argv) == 5 
    inputs = None
    if len(sys.argv) == 5:
        inputs = sys.argv[4]

    if not os.path.exists(outdir):
        print("Output directory doesn't exist.")
        sys.exit(0)

    if inputs is not None:
        objids = inputs.split(",")
    else:
        objids = None

    extract_objects(datastore, objids, outdir, band)
