# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:30:15 2017
@author: Daniel García Díaz

A partir de los archivos originales de la ESA, el código extrae dos imágenes (una en formato PNG y otra en formato GeoTIFF) RGB, por composición de 3 bandas originales del producto. El código realiza un resample de las bandas para ajustar las resoluciones de estas, y corta la imagen original con el polígono seleccionado. La imagen puede ser en True color si se escogen las bandas pertenecientes al azul, rojo y verde (B4, B3 y B2), o se puede utilizar cualquier otra combinación.
"""

#Importamos las funciones a utilizar
import numpy as np

import sys
sys.path.append('/home/ubuntu/.snap/snap-python/')
from snappy import (Product, ProductIO, ProductData, ProductUtils, jpy, GPF, HashMap, ProgressMonitor, String)

#Inputs de la funcion. path del archivo y las bandas seleccionadas. En este caso se #va a obtener una imagen True Color, RGB.
path='folder+file'
bands=['B4','B3','B2']

#funcion; necesita como Inputs el path y las banda con las que se va a realizar la #imagen RGB. El output de la funcion son dos imagenes, una en formato png y otra en #formato GeoTIF
def RGB_band(path, bands):

        p = ProductIO.readProduct(path)

#cambiamos la relsolucion de las bandas. Resample
        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        HashMap = jpy.get_type('java.util.HashMap')
        BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')

        parameters = HashMap()
        parameters.put('targetResolution',60)
        parameters.put('upsampling','Bicubic')
        parameters.put('downsampling','Mean')
        parameters.put('flagDownsampling','FlagMedianAnd')
        parameters.put('resampleOnPyramidLevels',True)
        product=GPF.createProduct('Resample', parameters, p)
        print "Resample ok!"

#Escogemos el poligono y cortamos la imagen de modo que tenemos un subset de la imagen original
        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        WKTReader = jpy.get_type('com.vividsolutions.jts.io.WKTReader')
        wkt="POLYGON((-2.83292 41.82416,-2.69014 41.82416,-2.69014 41.90993,-2.83292 41.90993,-2.83292 41.82416))"
        geom = WKTReader().read(wkt)

        parameters = HashMap()
        parameters.put('geoRegion', geom)
        parameters.put('outputImageScaleInDb', False)
        parameters.put('copyMetadata', True)
        subset = GPF.createProduct('Subset', parameters, product)
        print "subset ok!"

#ProductIO.writeProduct(subset, "snappy_subset_output.dim", "BEAM-DIMAP")

#leemos las bandas escogidas y guardamos la info en una lista
        Rband=subset.getBand(bands[0])
        Gband=subset.getBand(bands[1])
        Bband=subset.getBand(bands[2])
        RGB=[Rband, Gband, Bband]

#imagen en formato PNG
        image_info = ProductUtils.createImageInfo(RGB, True, ProgressMonitor.NULL)
        ImageManager=jpy.get_type('org.esa.snap.core.image.ImageManager')
        JAI=jpy.get_type('javax.media.jai.JAI')
        im=ImageManager.getInstance().createColoredBandImage(RGB, image_info, 0)
        image_rgb = ProductUtils.createRgbImage(RGB, image_info, ProgressMonitor.NULL)
        JAI.create("filestore", im,'RGB_%s%s%s.png' % (bands[0], bands[1], bands[2]), 'PNG')
        print "PNG Done!"

#imagen en formato GeoTIFF
	parameters = HashMap()
        parameters.put('sourceBands', '%s,%s,%s' % (bands[0], bands[1], bands[2]))
        result = GPF.createProduct('Subset', parameters, subset)
        ProductIO.writeProduct(result, 'RGB_%s%s%s.tif' % (bands[0], bands[1], bands[2]), 'GeoTIFF')
	print "GeoTIFF Done!"

