# GDAL exercise
# Read and plot a BAG file
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo import osr


sys.path.append(os.getcwd())
np.set_printoptions(precision=2, floatmode='fixed')

# open BAG file
bag_path = os.path.join(os.getcwd(), "H11560_LI_3m_MLLW_1of1.bag")  # the 'H11560_LI_3m_MLLW_1of1.bag' file is located under the `data` folder

dataset = gdal.Open(bag_path, gdal.GA_ReadOnly)
if not dataset:
    raise RuntimeError("Issue in opening the BAG file: %s" % bag_path)

print("BAG file was successfully opened: %s" % (bag_path,))

# retrieve corner coordinates of the extent
gt = dataset.GetGeoTransform()
if not gt:
    raise RuntimeError("Issue in retrieving the geotransfrom")
print("")
print("Geo-Transform: [%.2f, %.2f, %.2f, %.2f, %.2f, %.2f]" % gt)

print("x coordinate of the top-left corner : %.3f " %gt[0])
print("y coordinate of the top-left corner : %.3f " %gt[3])

print("Top-left Corner = (%.2f, %.2f)" % (gt[0], gt[3]))
print("Grid Resolution = (%.2f, %.2f)" % (gt[1], gt[5]))

#read raster layers
elev_band = dataset.GetRasterBand(1)
print("")
print("Elevation band -> data type: %s" % (gdal.GetDataTypeName(elev_band.DataType)))
print("Elevation band -> min/max values in meters: %.3f/%.3f" % (elev_band.GetMinimum(), elev_band.GetMaximum()))
elev_nodata = elev_band.GetNoDataValue()
print("Elevation band -> nodata value: %s" % (elev_nodata))

unc_band = dataset.GetRasterBand(2)
print("Uncertainty band -> data type: %s" % (gdal.GetDataTypeName(unc_band.DataType)))
print("Uncertainty band -> min/max values in meters: %.3f/%.3f" % (unc_band.GetMinimum(), unc_band.GetMaximum()))
unc_nodata = elev_band.GetNoDataValue()
print("Uncertainty band -> nodata value: %s" % (unc_nodata))

print("")
print("Projection:")
projection = dataset.GetProjection()
print("- WKT:\n%s" % projection)

srs = osr.SpatialReference(wkt=projection)
projection_name = srs.GetAttrValue('projcs')
print("- name: %s" % projection_name)

#read raster layers as numpy arrays
elev = elev_band.ReadAsArray()
elev[elev==elev_nodata] = np.nan
elev = -elev

print("minimum depth: %.3f" % np.nanmin(elev))
print("maximum depth: %.3f" % np.nanmax(elev))

plt.imshow(elev)
plt.show()

#calculate extent of the area
bag_extent = [gt[0], gt[0] + elev.shape[1] * gt[1], gt[3] + elev.shape[0] * gt[5], gt[3]]
print("BAG extent: %s" % (bag_extent, ))


#create final plot
plt.figure(figsize=(15, 10))
ax = plt.axes()
plt.ticklabel_format(useOffset=False)  # to avoid the display of an offset for the labels
ax.xaxis.set_major_locator(ticker.MultipleLocator(5000.0))  # to set the distance between labels (x axis)
ax.yaxis.set_major_locator(ticker.MultipleLocator(5000.0))  # to set the distance between labels (y axis)
img = ax.imshow(elev, origin='upper', extent=bag_extent, cmap='viridis_r')  # display the array using the passed data extent
ax.set_aspect('equal')  # avoid deformations for the displayed data
title = "%s\nProjection: %s" % (os.path.basename(bag_path), projection_name)
plt.title(title)  # put the filename and the projection as part of the title
plt.xlabel("Easting")
plt.ylabel("Northing")
cb = plt.colorbar(img)  # pass the 'img' object used to create the colorbar
cb.set_label('Bathymetry [meter]')
plt.grid()
#plt.savefig('bag.png')
plt.show()