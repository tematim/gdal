#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test default implementation of GDALRasterBand::IRasterIO
# Author:   Even Rouault <even dot rouault at mines dash paris dot org>
#
###############################################################################
# Copyright (c) 2008-2013, Even Rouault <even dot rouault at mines-paris dot org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

import struct
import sys

sys.path.append('../pymod')

import gdaltest
from osgeo import gdal

###############################################################################
# Test writing a 1x1 buffer to a 10x6 raster and read it back


def rasterio_1():
    data = 'A'.encode('ascii')

    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create('tmp/rasterio1.tif', 10, 6, 1)

    ds.GetRasterBand(1).Fill(65)
    checksum = ds.GetRasterBand(1).Checksum()

    ds.GetRasterBand(1).Fill(0)

    ds.WriteRaster(0, 0, ds.RasterXSize, ds.RasterYSize, data, buf_type=gdal.GDT_Byte, buf_xsize=1, buf_ysize=1)
    if checksum != ds.GetRasterBand(1).Checksum():
        gdaltest.post_reason('Didnt get expected checksum ')
        return 'fail'

    data2 = ds.ReadRaster(0, 0, ds.RasterXSize, ds.RasterYSize, 1, 1)
    if data2 != data:
        gdaltest.post_reason('Didnt get expected buffer ')
        return 'fail'

    ds = None
    drv.Delete('tmp/rasterio1.tif')

    return 'success'

###############################################################################
# Test writing a 5x4 buffer to a 10x6 raster and read it back


def rasterio_2():
    data = 'AAAAAAAAAAAAAAAAAAAA'.encode('ascii')

    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create('tmp/rasterio2.tif', 10, 6, 1)

    ds.GetRasterBand(1).Fill(65)
    checksum = ds.GetRasterBand(1).Checksum()

    ds.GetRasterBand(1).Fill(0)

    ds.WriteRaster(0, 0, ds.RasterXSize, ds.RasterYSize, data, buf_type=gdal.GDT_Byte, buf_xsize=5, buf_ysize=4)
    if checksum != ds.GetRasterBand(1).Checksum():
        gdaltest.post_reason('Didnt get expected checksum ')
        return 'fail'

    data2 = ds.ReadRaster(0, 0, ds.RasterXSize, ds.RasterYSize, 5, 4)
    if data2 != data:
        gdaltest.post_reason('Didnt get expected buffer ')
        return 'fail'

    ds = None
    drv.Delete('tmp/rasterio2.tif')

    return 'success'

###############################################################################
# Test extensive read & writes into a non tiled raster


def rasterio_3():

    data = [['' for i in range(4)] for i in range(5)]
    for xsize in range(5):
        for ysize in range(4):
            for m in range((xsize + 1) * (ysize + 1)):
                data[xsize][ysize] = data[xsize][ysize] + 'A'
            data[xsize][ysize] = data[xsize][ysize].encode('ascii')

    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create('tmp/rasterio3.tif', 10, 6, 1)

    i = 0
    while i < ds.RasterXSize:
        j = 0
        while j < ds.RasterYSize:
            k = 0
            while k < ds.RasterXSize - i:
                m = 0
                while m < ds.RasterYSize - j:
                    for xsize in range(5):
                        for ysize in range(4):
                            ds.GetRasterBand(1).Fill(0)
                            ds.WriteRaster(i, j, k + 1, m + 1, data[xsize][ysize],
                                           buf_type=gdal.GDT_Byte,
                                           buf_xsize=xsize + 1, buf_ysize=ysize + 1)
                            data2 = ds.ReadRaster(i, j, k + 1, m + 1, xsize + 1, ysize + 1, gdal.GDT_Byte)
                            if data2 != data[xsize][ysize]:
                                gdaltest.post_reason('Didnt get expected buffer ')
                                return 'fail'
                    m = m + 1
                k = k + 1
            j = j + 1
        i = i + 1

    ds = None
    drv.Delete('tmp/rasterio3.tif')

    return 'success'

###############################################################################
# Test extensive read & writes into a tiled raster


def rasterio_4():

    data = ['' for i in range(5 * 4)]
    for size in range(5 * 4):
        for k in range(size + 1):
            data[size] = data[size] + 'A'
        data[size] = data[size].encode('ascii')

    drv = gdal.GetDriverByName('GTiff')
    ds = drv.Create('tmp/rasterio4.tif', 20, 20, 1, options=['TILED=YES', 'BLOCKXSIZE=16', 'BLOCKYSIZE=16'])

    i = 0
    while i < ds.RasterXSize:
        j = 0
        while j < ds.RasterYSize:
            k = 0
            while k < ds.RasterXSize - i:
                m = 0
                while m < ds.RasterYSize - j:
                    for xsize in range(5):
                        for ysize in range(4):
                            ds.GetRasterBand(1).Fill(0)
                            ds.WriteRaster(i, j, k + 1, m + 1, data[(xsize + 1) * (ysize + 1) - 1],
                                           buf_type=gdal.GDT_Byte,
                                           buf_xsize=xsize + 1, buf_ysize=ysize + 1)
                            data2 = ds.ReadRaster(i, j, k + 1, m + 1, xsize + 1, ysize + 1, gdal.GDT_Byte)
                            if data2 != data[(xsize + 1) * (ysize + 1) - 1]:
                                gdaltest.post_reason('Didnt get expected buffer ')
                                print(i, j, k, m, xsize, ysize)
                                print(data2)
                                print(data[(xsize + 1) * (ysize + 1) - 1])
                                return 'fail'
                    m = m + 1
                k = k + 1
            if j >= 15:
                j = j + 1
            else:
                j = j + 3
        if i >= 15:
            i = i + 1
        else:
            i = i + 3

    ds = None
    drv.Delete('tmp/rasterio4.tif')

    return 'success'

###############################################################################
# Test error cases of ReadRaster()


def rasterio_5():

    ds = gdal.Open('data/byte.tif')

    for obj in [ds, ds.GetRasterBand(1)]:
        obj.ReadRaster(0, 0, -2000000000, 1, 1, 1)
        obj.ReadRaster(0, 0, 1, -2000000000, 1, 1)

    for band_number in [-1, 0, 2]:
        gdal.ErrorReset()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        res = ds.ReadRaster(0, 0, 1, 1, band_list=[band_number])
        gdal.PopErrorHandler()
        error_msg = gdal.GetLastErrorMsg()
        if res is not None:
            gdaltest.post_reason('expected None')
            return 'fail'
        if error_msg.find('this band does not exist on dataset') == -1:
            gdaltest.post_reason('did not get expected error msg')
            print(error_msg)
            return 'fail'

    res = ds.ReadRaster(0, 0, 1, 1, band_list=[1, 1])
    if res is None:
        gdaltest.post_reason('expected non None')
        return 'fail'

    for obj in [ds, ds.GetRasterBand(1)]:
        gdal.ErrorReset()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        res = obj.ReadRaster(0, 0, 21, 21)
        gdal.PopErrorHandler()
        error_msg = gdal.GetLastErrorMsg()
        if res is not None:
            gdaltest.post_reason('expected None')
            return 'fail'
        if error_msg.find('Access window out of range in RasterIO()') == -1:
            gdaltest.post_reason('did not get expected error msg (1)')
            print(error_msg)
            return 'fail'

        # This should only fail on a 32bit build
        try:
            maxsize = sys.maxint
        except AttributeError:
            maxsize = sys.maxsize

        # On win64, maxsize == 2147483647 and ReadRaster()
        # fails because of out of memory condition, not
        # because of integer overflow. I'm not sure on how
        # to detect win64 better.
        if maxsize == 2147483647 and sys.platform != 'win32':
            gdal.ErrorReset()
            gdal.PushErrorHandler('CPLQuietErrorHandler')
            res = obj.ReadRaster(0, 0, 1, 1, 1000000, 1000000)
            gdal.PopErrorHandler()
            error_msg = gdal.GetLastErrorMsg()
            if res is not None:
                gdaltest.post_reason('expected None')
                return 'fail'
            if error_msg.find('Integer overflow') == -1:
                gdaltest.post_reason('did not get expected error msg (2)')
                print(error_msg)
                return 'fail'

        gdal.ErrorReset()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        res = obj.ReadRaster(0, 0, 0, 1)
        gdal.PopErrorHandler()
        error_msg = gdal.GetLastErrorMsg()
        if res is not None:
            gdaltest.post_reason('expected None')
            return 'fail'
        if error_msg.find('Illegal values for buffer size') == -1:
            gdaltest.post_reason('did not get expected error msg (3)')
            print(error_msg)
            return 'fail'

    ds = None

    return 'success'

###############################################################################
# Test error cases of WriteRaster()


def rasterio_6():

    ds = gdal.GetDriverByName('MEM').Create('', 2, 2)

    for obj in [ds, ds.GetRasterBand(1)]:
        try:
            obj.WriteRaster(0, 0, 2, 2, None)
            gdaltest.post_reason('expected exception')
            return 'fail'
        except:
            pass

        gdal.ErrorReset()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        obj.WriteRaster(0, 0, 2, 2, ' ')
        gdal.PopErrorHandler()
        error_msg = gdal.GetLastErrorMsg()
        if error_msg.find('Buffer too small') == -1:
            gdaltest.post_reason('did not get expected error msg (1)')
            print(error_msg)
            return 'fail'

        gdal.ErrorReset()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        obj.WriteRaster(-1, 0, 1, 1, ' ')
        gdal.PopErrorHandler()
        error_msg = gdal.GetLastErrorMsg()
        if error_msg.find('Access window out of range in RasterIO()') == -1:
            gdaltest.post_reason('did not get expected error msg (2)')
            print(error_msg)
            return 'fail'

        gdal.ErrorReset()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        obj.WriteRaster(0, 0, 0, 1, ' ')
        gdal.PopErrorHandler()
        error_msg = gdal.GetLastErrorMsg()
        if error_msg.find('Illegal values for buffer size') == -1:
            gdaltest.post_reason('did not get expected error msg (3)')
            print(error_msg)
            return 'fail'

    ds = None

    return 'success'

###############################################################################
# Test that default window reading works via ReadRaster()


def rasterio_7():

    ds = gdal.Open('data/byte.tif')

    data = ds.GetRasterBand(1).ReadRaster()
    if len(data) != 400:
        gdaltest.post_reason('did not read expected band data via ReadRaster()')
        return 'fail'

    data = ds.ReadRaster()
    if len(data) != 400:
        gdaltest.post_reason('did not read expected dataset data via ReadRaster()')
        return 'fail'

    return 'success'

###############################################################################
# Test callback of ReadRaster()


def rasterio_8_progress_callback(pct, message, user_data):
    if abs(pct - (user_data[0] + 0.05)) > 1e-5:
        print('Expected %f, got %f' % (user_data[0] + 0.05, pct))
        user_data[1] = False
    user_data[0] = pct
    return 1  # 1 to continue, 0 to stop


def rasterio_8_progress_interrupt_callback(pct, message, user_data):
    user_data[0] = pct
    if pct >= 0.5:
        return 0
    return 1  # 1 to continue, 0 to stop


def rasterio_8_progress_callback_2(pct, message, user_data):
    if pct < user_data[0]:
        print('Got %f, last pct was %f' % (pct, user_data[0]))
        return 0
    user_data[0] = pct
    return 1  # 1 to continue, 0 to stop


def rasterio_8():

    ds = gdal.Open('data/byte.tif')

    # Progress not implemented yet
    if gdal.GetConfigOption('GTIFF_DIRECT_IO') == 'YES' or \
       gdal.GetConfigOption('GTIFF_VIRTUAL_MEM_IO') == 'YES':
        return 'skip'

    # Test RasterBand.ReadRaster
    tab = [0, True]
    data = ds.GetRasterBand(1).ReadRaster(resample_alg=gdal.GRIORA_NearestNeighbour,
                                          callback=rasterio_8_progress_callback,
                                          callback_data=tab)
    if len(data) != 400:
        gdaltest.post_reason('did not read expected band data via ReadRaster()')
        return 'fail'
    if abs(tab[0] - 1) > 1e-5 or not tab[1]:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test interruption
    tab = [0]
    data = ds.GetRasterBand(1).ReadRaster(resample_alg=gdal.GRIORA_NearestNeighbour,
                                          callback=rasterio_8_progress_interrupt_callback,
                                          callback_data=tab)
    if data is not None:
        gdaltest.post_reason('failure')
        return 'fail'
    if tab[0] < 0.50:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster with type change
    tab = [0, True]
    data = ds.GetRasterBand(1).ReadRaster(buf_type=gdal.GDT_Int16,
                                          callback=rasterio_8_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('did not read expected band data via ReadRaster()')
        return 'fail'
    if abs(tab[0] - 1) > 1e-5 or not tab[1]:
        gdaltest.post_reason('failure')
        return 'fail'

    # Same with interruption
    tab = [0]
    data = ds.GetRasterBand(1).ReadRaster(buf_type=gdal.GDT_Int16,
                                          callback=rasterio_8_progress_interrupt_callback,
                                          callback_data=tab)
    if data is not None or tab[0] < 0.50:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster with resampling
    tab = [0, True]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=40,
                                          callback=rasterio_8_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('did not read expected band data via ReadRaster()')
        return 'fail'
    if abs(tab[0] - 1) > 1e-5 or not tab[1]:
        gdaltest.post_reason('failure')
        return 'fail'

    # Same with interruption
    tab = [0]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=40,
                                          callback=rasterio_8_progress_interrupt_callback,
                                          callback_data=tab)
    if data is not None or tab[0] < 0.50:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test Dataset.ReadRaster
    tab = [0, True]
    data = ds.ReadRaster(resample_alg=gdal.GRIORA_NearestNeighbour,
                         callback=rasterio_8_progress_callback,
                         callback_data=tab)
    if len(data) != 400:
        gdaltest.post_reason('did not read expected dataset data via ReadRaster()')
        return 'fail'
    if abs(tab[0] - 1) > 1e-5 or not tab[1]:
        gdaltest.post_reason('failure')
        return 'fail'

    ds = None

    # Test Dataset.ReadRaster on a multi band file, with INTERLEAVE=BAND
    ds = gdal.Open('data/rgbsmall.tif')
    last_pct = [0]
    data = ds.ReadRaster(resample_alg=gdal.GRIORA_NearestNeighbour,
                         callback=rasterio_8_progress_callback_2,
                         callback_data=last_pct)
    if data is None or abs(last_pct[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Same with interruption
    tab = [0]
    data = ds.ReadRaster(callback=rasterio_8_progress_interrupt_callback,
                         callback_data=tab)
    if data is not None or tab[0] < 0.50:
        gdaltest.post_reason('failure')
        return 'fail'

    ds = None

    # Test Dataset.ReadRaster on a multi band file, with INTERLEAVE=PIXEL
    ds = gdal.Open('data/rgbsmall_cmyk.tif')
    last_pct = [0]
    data = ds.ReadRaster(resample_alg=gdal.GRIORA_NearestNeighbour,
                         callback=rasterio_8_progress_callback_2,
                         callback_data=last_pct)
    if data is None or abs(last_pct[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Same with interruption
    tab = [0]
    data = ds.ReadRaster(callback=rasterio_8_progress_interrupt_callback,
                         callback_data=tab)
    if data is not None or tab[0] < 0.50:
        gdaltest.post_reason('failure')
        return 'fail'

    return 'success'

###############################################################################
# Test resampling algorithm of ReadRaster()


def rasterio_9_progress_callback(pct, message, user_data):
    if pct < user_data[0]:
        print('Got %f, last pct was %f' % (pct, user_data[0]))
        return 0
    user_data[0] = pct
    if user_data[1] is not None and pct >= user_data[1]:
        return 0
    return 1  # 1 to continue, 0 to stop


def rasterio_9_checksum(data, buf_xsize, buf_ysize, data_type=gdal.GDT_Byte):
    ds = gdal.GetDriverByName('MEM').Create('', buf_xsize, buf_ysize, 1)
    ds.GetRasterBand(1).WriteRaster(0, 0, buf_xsize, buf_ysize, data, buf_type=data_type)
    cs = ds.GetRasterBand(1).Checksum()
    return cs


def rasterio_9():
    ds = gdal.Open('data/byte.tif')

    # Test RasterBand.ReadRaster, with Bilinear
    tab = [0, None]
    data = ds.GetRasterBand(1).ReadRaster(buf_type=gdal.GDT_Int16,
                                          buf_xsize=10,
                                          buf_ysize=10,
                                          resample_alg=gdal.GRIORA_Bilinear,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    data_ar = struct.unpack('h' * 10 * 10, data)
    cs = rasterio_9_checksum(data, 10, 10, data_type=gdal.GDT_Int16)
    if cs != 1211:  # checksum of gdal_translate data/byte.tif out.tif -outsize 10 10 -r BILINEAR
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Same but query with GDT_Float32. Check that we do not get floating-point
    # values, since the band type is Byte
    data = ds.GetRasterBand(1).ReadRaster(buf_type=gdal.GDT_Float32,
                                          buf_xsize=10,
                                          buf_ysize=10,
                                          resample_alg=gdal.GRIORA_Bilinear)

    data_float32_ar = struct.unpack('f' * 10 * 10, data)
    if data_ar != data_float32_ar:
        gdaltest.post_reason('failure')
        print(data_float32_ar)
        return 'fail'

    # Test RasterBand.ReadRaster, with Lanczos
    tab = [0, None]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=10,
                                          buf_ysize=10,
                                          resample_alg=gdal.GRIORA_Lanczos,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 10, 10)
    if cs != 1154:  # checksum of gdal_translate data/byte.tif out.tif -outsize 10 10 -r LANCZOS
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster, with Bilinear and UInt16 data type
    src_ds_uint16 = gdal.Open('data/uint16.tif')
    tab = [0, None]
    data = src_ds_uint16.GetRasterBand(1).ReadRaster(buf_type=gdal.GDT_UInt16,
                                                     buf_xsize=10,
                                                     buf_ysize=10,
                                                     resample_alg=gdal.GRIORA_Bilinear,
                                                     callback=rasterio_9_progress_callback,
                                                     callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 10, 10, data_type=gdal.GDT_UInt16)
    if cs != 1211:  # checksum of gdal_translate data/byte.tif out.tif -outsize 10 10 -r BILINEAR
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster, with Bilinear on Complex, thus using warp API
    tab = [0, None]
    complex_ds = gdal.GetDriverByName('MEM').Create('', 20, 20, 1, gdal.GDT_CInt16)
    complex_ds.GetRasterBand(1).WriteRaster(0, 0, 20, 20, ds.GetRasterBand(1).ReadRaster(), buf_type=gdal.GDT_Byte)
    data = complex_ds.GetRasterBand(1).ReadRaster(buf_xsize=10,
                                                  buf_ysize=10,
                                                  resample_alg=gdal.GRIORA_Bilinear,
                                                  callback=rasterio_9_progress_callback,
                                                  callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 10, 10, data_type=gdal.GDT_CInt16)
    if cs != 1211:  # checksum of gdal_translate data/byte.tif out.tif -outsize 10 10 -r BILINEAR
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test interruption
    tab = [0, 0.5]
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=10,
                                          buf_ysize=10,
                                          resample_alg=gdal.GRIORA_Bilinear,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    gdal.PopErrorHandler()
    if data is not None:
        gdaltest.post_reason('failure')
        return 'fail'
    if tab[0] < 0.50:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster, with Gauss, and downsampling
    tab = [0, None]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=10,
                                          buf_ysize=10,
                                          resample_alg=gdal.GRIORA_Gauss,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 10, 10)
    if cs != 1089:  # checksum of gdal_translate data/byte.tif out.tif -outsize 10 10 -r GAUSS
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster, with Cubic, and downsampling
    tab = [0, None]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=10,
                                          buf_ysize=10,
                                          resample_alg=gdal.GRIORA_Cubic,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 10, 10)
    if cs != 1059:  # checksum of gdal_translate data/byte.tif out.tif -outsize 10 10 -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test RasterBand.ReadRaster, with Cubic, and downsampling with >=8x8 source samples used for a dest sample
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=5,
                                          buf_ysize=5,
                                          resample_alg=gdal.GRIORA_Cubic)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 5, 5)
    if cs != 214:  # checksum of gdal_translate data/byte.tif out.tif -outsize 5 5 -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    # Same with UInt16
    data = src_ds_uint16.GetRasterBand(1).ReadRaster(buf_xsize=5,
                                                     buf_ysize=5,
                                                     resample_alg=gdal.GRIORA_Cubic)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 5, 5, data_type=gdal.GDT_UInt16)
    if cs != 214:  # checksum of gdal_translate data/byte.tif out.tif -outsize 5 5 -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    # Test RasterBand.ReadRaster, with Cubic and supersampling
    tab = [0, None]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=40,
                                          buf_ysize=40,
                                          resample_alg=gdal.GRIORA_Cubic,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 40, 40)
    if cs != 19556:  # checksum of gdal_translate data/byte.tif out.tif -outsize 40 40 -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test Dataset.ReadRaster, with Cubic and supersampling
    tab = [0, None]
    data = ds.ReadRaster(buf_xsize=40,
                         buf_ysize=40,
                         resample_alg=gdal.GRIORA_CubicSpline,
                         callback=rasterio_9_progress_callback,
                         callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 40, 40)
    if cs != 19041:  # checksum of gdal_translate data/byte.tif out.tif -outsize 40 40 -r CUBICSPLINE
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    # Test Dataset.ReadRaster on a multi band file, with INTERLEAVE=PIXEL
    ds = gdal.Open('data/rgbsmall_cmyk.tif')
    tab = [0, None]
    data = ds.ReadRaster(buf_xsize=25,
                         buf_ysize=25,
                         resample_alg=gdal.GRIORA_Cubic,
                         callback=rasterio_9_progress_callback,
                         callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data[0:25 * 25], 25, 25)
    if cs != 5975:  # checksum of gdal_translate data/rgbsmall_cmyk.tif out.tif -outsize 25 25 -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'
    cs = rasterio_9_checksum(data[25 * 25:2 * 25 * 25], 25, 25)
    if cs != 6248:  # checksum of gdal_translate data/rgbsmall_cmyk.tif out.tif -outsize 25 25 -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'

    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'
    ds = None

    # Test Band.ReadRaster on a RGBA with parts fully opaque, and fully transparent and with huge upscaling
    ds = gdal.Open('data/stefan_full_rgba.png')
    tab = [0, None]
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=162 * 16,
                                          buf_ysize=150 * 16,
                                          resample_alg=gdal.GRIORA_Cubic,
                                          callback=rasterio_9_progress_callback,
                                          callback_data=tab)
    if data is None:
        gdaltest.post_reason('failure')
        return 'fail'
    cs = rasterio_9_checksum(data, 162 * 16, 150 * 16)
    if cs != 30836:  # checksum of gdal_translate data/stefan_full_rgba.png out.tif -outsize 1600% 1600% -r CUBIC
        gdaltest.post_reason('failure')
        print(cs)
        return 'fail'
    if abs(tab[0] - 1.0) > 1e-5:
        gdaltest.post_reason('failure')
        return 'fail'

    return 'success'

###############################################################################
# Test error when getting a block


def rasterio_10():
    ds = gdal.Open('data/byte_truncated.tif')

    gdal.PushErrorHandler()
    data = ds.GetRasterBand(1).ReadRaster()
    gdal.PopErrorHandler()
    if data is not None:
        gdaltest.post_reason('failure')
        return 'fail'

    # Change buffer type
    gdal.PushErrorHandler()
    data = ds.GetRasterBand(1).ReadRaster(buf_type=gdal.GDT_Int16)
    gdal.PopErrorHandler()
    if data is not None:
        gdaltest.post_reason('failure')
        return 'fail'

    # Resampling case
    gdal.PushErrorHandler()
    data = ds.GetRasterBand(1).ReadRaster(buf_xsize=10,
                                          buf_ysize=10)
    gdal.PopErrorHandler()
    if data is not None:
        gdaltest.post_reason('failure')
        return 'fail'

    return 'success'

###############################################################################
# Test cubic resampling and nbits


def rasterio_11():

    try:
        from osgeo import gdalnumeric
        gdalnumeric.zeros
        import numpy
    except (ImportError, AttributeError):
        return 'skip'

    mem_ds = gdal.GetDriverByName('MEM').Create('', 4, 3)
    mem_ds.GetRasterBand(1).WriteArray(numpy.array([[80, 125, 125, 80], [80, 125, 125, 80], [80, 125, 125, 80]]))

    # A bit dummy
    mem_ds.GetRasterBand(1).SetMetadataItem('NBITS', '8', 'IMAGE_STRUCTURE')
    ar = mem_ds.GetRasterBand(1).ReadAsArray(0, 0, 4, 3, 8, 3, resample_alg=gdal.GRIORA_Cubic)
    if ar.max() != 129:
        gdaltest.post_reason('failure')
        print(ar.max())
        return 'fail'

    # NBITS=7
    mem_ds.GetRasterBand(1).SetMetadataItem('NBITS', '7', 'IMAGE_STRUCTURE')
    ar = mem_ds.GetRasterBand(1).ReadAsArray(0, 0, 4, 3, 8, 3, resample_alg=gdal.GRIORA_Cubic)
    # Would overshoot to 129 if NBITS was ignored
    if ar.max() != 127:
        gdaltest.post_reason('failure')
        print(ar.max())
        return 'fail'

    return 'success'

###############################################################################
# Test cubic resampling on dataset RasterIO with an alpha channel


def rasterio_12_progress_callback(pct, message, user_data):
    if pct < user_data[0]:
        print('Got %f, last pct was %f' % (pct, user_data[0]))
        return 0
    user_data[0] = pct
    return 1  # 1 to continue, 0 to stop


def rasterio_12():

    try:
        from osgeo import gdalnumeric
        gdalnumeric.zeros
        import numpy
    except (ImportError, AttributeError):
        return 'skip'

    mem_ds = gdal.GetDriverByName('MEM').Create('', 4, 3, 4)
    for i in range(3):
        mem_ds.GetRasterBand(i + 1).SetColorInterpretation(gdal.GCI_GrayIndex)
    mem_ds.GetRasterBand(4).SetColorInterpretation(gdal.GCI_AlphaBand)
    for i in range(4):
        mem_ds.GetRasterBand(i + 1).WriteArray(numpy.array([[0, 0, 0, 0], [0, 255, 0, 0], [0, 0, 0, 0]]))

    tab = [0]
    ar_ds = mem_ds.ReadAsArray(0, 0, 4, 3, buf_xsize=8, buf_ysize=3, resample_alg=gdal.GRIORA_Cubic,
                               callback=rasterio_12_progress_callback,
                               callback_data=tab)
    if tab[0] != 1.0:
        gdaltest.post_reason('failure')
        print(tab)
        return 'fail'

    ar_ds2 = mem_ds.ReadAsArray(0, 0, 4, 3, buf_xsize=8, buf_ysize=3, resample_alg=gdal.GRIORA_Cubic)
    if not numpy.array_equal(ar_ds, ar_ds2):
        gdaltest.post_reason('failure')
        print(ar_ds)
        print(ar_ds2)
        return 'fail'

    ar_bands = [mem_ds.GetRasterBand(i + 1).ReadAsArray(0, 0, 4, 3, buf_xsize=8, buf_ysize=3, resample_alg=gdal.GRIORA_Cubic) for i in range(4)]

    # Results of band or dataset RasterIO should be the same
    for i in range(4):
        if not numpy.array_equal(ar_ds[i], ar_bands[i]):
            gdaltest.post_reason('failure')
            print(ar_ds)
            print(ar_bands[i])
            return 'fail'

    # First, second and third band should have identical content
    if not numpy.array_equal(ar_ds[0], ar_ds[1]):
        gdaltest.post_reason('failure')
        print(ar_ds[0])
        print(ar_ds[1])
        return 'fail'

    # Alpha band should be different
    if numpy.array_equal(ar_ds[0], ar_ds[3]):
        gdaltest.post_reason('failure')
        print(ar_ds[0])
        print(ar_ds[3])
        return 'fail'

    return 'success'

###############################################################################
# Test cubic resampling with masking


def rasterio_13():

    try:
        from osgeo import gdalnumeric
        gdalnumeric.zeros
        import numpy
    except (ImportError, AttributeError):
        return 'skip'

    for dt in [gdal.GDT_Byte, gdal.GDT_UInt16, gdal.GDT_UInt32]:

        mem_ds = gdal.GetDriverByName('MEM').Create('', 4, 3, 1, dt)
        mem_ds.GetRasterBand(1).SetNoDataValue(0)
        mem_ds.GetRasterBand(1).WriteArray(numpy.array([[0, 0, 0, 0], [0, 255, 0, 0], [0, 0, 0, 0]]))

        ar_ds = mem_ds.ReadAsArray(0, 0, 4, 3, buf_xsize=8, buf_ysize=3, resample_alg=gdal.GRIORA_Cubic)

        expected_ar = numpy.array([[0, 0, 0, 0, 0, 0, 0, 0], [0, 255, 255, 255, 255, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]])
        if not numpy.array_equal(ar_ds, expected_ar):
            gdaltest.post_reason('failure')
            print(dt)
            print(ar_ds)
            print(expected_ar)
            return 'fail'

    return 'success'

###############################################################################
# Test average downsampling by a factor of 2 on exact boundaries


def rasterio_14():

    gdal.FileFromMemBuffer('/vsimem/rasterio_14.asc',
                           """ncols        6
nrows        6
xllcorner    0
yllcorner    0
cellsize     0
  0   0   100 0   0   0
  0   100 0   0   0 100
  0   0   0   0 100   0
100   0 100   0   0   0
  0 100   0 100   0   0
  0   0   0   0   0 100""")

    ds = gdal.Translate('/vsimem/rasterio_14_out.asc', '/vsimem/rasterio_14.asc', options='-of AAIGRID -r average -outsize 50% 50%')
    cs = ds.GetRasterBand(1).Checksum()
    if cs != 110:
        gdaltest.post_reason('fail')
        print(cs)
        print(ds.ReadAsArray())
        return 'fail'

    gdal.Unlink('/vsimem/rasterio_14.asc')
    gdal.Unlink('/vsimem/rasterio_14_out.asc')

    ds = gdal.GetDriverByName('MEM').Create('', 1000000, 1)
    ds.GetRasterBand(1).WriteRaster(ds.RasterXSize - 1, 0, 1, 1, struct.pack('B' * 1, 100))
    data = ds.ReadRaster(buf_xsize=int(ds.RasterXSize / 2), buf_ysize=1, resample_alg=gdal.GRIORA_Average)
    data = struct.unpack('B' * int(ds.RasterXSize / 2), data)
    if data[-1:][0] != 50:
        gdaltest.post_reason('fail')
        print(data[-1:][0])
        return 'fail'

    data = ds.ReadRaster(ds.RasterXSize - 2, 0, 2, 1, buf_xsize=1, buf_ysize=1, resample_alg=gdal.GRIORA_Average)
    data = struct.unpack('B' * 1, data)
    if data[0] != 50:
        gdaltest.post_reason('fail')
        print(data[0])
        return 'fail'

    ds = gdal.GetDriverByName('MEM').Create('', 1, 1000000)
    ds.GetRasterBand(1).WriteRaster(0, ds.RasterYSize - 1, 1, 1, struct.pack('B' * 1, 100))
    data = ds.ReadRaster(buf_xsize=1, buf_ysize=int(ds.RasterYSize / 2), resample_alg=gdal.GRIORA_Average)
    data = struct.unpack('B' * int(ds.RasterYSize / 2), data)
    if data[-1:][0] != 50:
        gdaltest.post_reason('fail')
        print(data[-1:][0])
        return 'fail'

    data = ds.ReadRaster(0, ds.RasterYSize - 2, 1, 2, buf_xsize=1, buf_ysize=1, resample_alg=gdal.GRIORA_Average)
    data = struct.unpack('B' * 1, data)
    if data[0] != 50:
        gdaltest.post_reason('fail')
        print(data[0])
        return 'fail'

    return 'success'

###############################################################################
# Test average oversampling by an integer factor (should behave like nearest)


def rasterio_15():

    gdal.FileFromMemBuffer('/vsimem/rasterio_15.asc',
                           """ncols        2
nrows        2
xllcorner    0
yllcorner    0
cellsize     0
  0   100
100   100""")

    ds = gdal.Translate('/vsimem/rasterio_15_out.asc', '/vsimem/rasterio_15.asc', options='-of AAIGRID -outsize 200% 200%')
    data_ref = ds.GetRasterBand(1).ReadRaster()
    ds = None
    ds = gdal.Translate('/vsimem/rasterio_15_out.asc', '/vsimem/rasterio_15.asc', options='-of AAIGRID -r average -outsize 200% 200%')
    data = ds.GetRasterBand(1).ReadRaster()
    cs = ds.GetRasterBand(1).Checksum()
    if data != data_ref or cs != 134:
        gdaltest.post_reason('fail')
        print(cs)
        print(ds.ReadAsArray())
        return 'fail'

    gdal.Unlink('/vsimem/rasterio_15.asc')
    gdal.Unlink('/vsimem/rasterio_15_out.asc')

    return 'success'

###############################################################################
# Test mode downsampling by a factor of 2 on exact boundaries


def rasterio_16():

    gdal.FileFromMemBuffer('/vsimem/rasterio_16.asc',
                           """ncols        6
nrows        6
xllcorner    0
yllcorner    0
cellsize     0
  0   0   0   0   0   0
  2   100 0   0   0   0
100   100 0   0   0   0
  0   100 0   0   0   0
  0   0   0   0   0   0
  0   0   0   0   0  0""")

    ds = gdal.Translate('/vsimem/rasterio_16_out.asc', '/vsimem/rasterio_16.asc', options='-of AAIGRID -r mode -outsize 50% 50%')
    cs = ds.GetRasterBand(1).Checksum()
    if cs != 15:
        gdaltest.post_reason('fail')
        print(cs)
        print(ds.ReadAsArray())
        return 'fail'

    gdal.Unlink('/vsimem/rasterio_16.asc')
    gdal.Unlink('/vsimem/rasterio_16_out.asc')

    return 'success'


gdaltest_list = [
    rasterio_1,
    rasterio_2,
    rasterio_3,
    rasterio_4,
    rasterio_5,
    rasterio_6,
    rasterio_7,
    rasterio_8,
    rasterio_9,
    rasterio_10,
    rasterio_11,
    rasterio_12,
    rasterio_13,
    rasterio_14,
    rasterio_15,
    rasterio_16
]

# gdaltest_list = [ rasterio_16 ]

if __name__ == '__main__':

    gdaltest.setup_run('rasterio')

    gdaltest.run_tests(gdaltest_list)

    gdaltest.summarize()
