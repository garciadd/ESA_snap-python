# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 11:52:22 2017

@author: Daniel García Díaz

A partir de los archivos originales de la ESA, el código construye una nueva 
capa a partir de las capas ya existentes, formando así los indices de vegetación. 
La función necesita la expresión que se desea implementar como indice, 
y las bandas a partir de las cuales se va a construir el indice de vegetación. 
El código también realiza un resample de las bandas para ajustar la resolución 
y corta la imagen original realizando un subset a partir del polígono deseado.
"""
#Importamos las funciones a utilizar
import numpy as np

import sys
sys.path.append('/home/ubuntu/.snap/snap-python/')
from snappy import (ProductIO, GPF, jpy, HashMap)

#Inputs de la funcion. path del archivo, nombre del indice de vegetacion y 
#expresion que queremos implementar.
path='folder+file'
name='RE-NDWI'
expr='(B3 - B5) / (B3 + B5)'

#funcion; necesita como entrada el path, el nombre del indice de vegetacion y 
#la expresion con la que construir el indice.
def indVegetacion(path, name, expr):

        p = ProductIO.readProduct(path)

#cambiamos la relsolucion de las bandas. Resample
        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        HashMap = jpy.get_type('java.util.HashMap')
        BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')

        parameters = HashMap()
        parameters.put('targetResolution',10)
        parameters.put('upsampling','Bicubic')
        parameters.put('downsampling','Mean')
        parameters.put('flagDownsampling','FlagMedianAnd')
        parameters.put('resampleOnPyramidLevels',True)
        product=GPF.createProduct('Resample', parameters, p)
        print "resample ok!"

#Escogemos el poligono y cortamos la imagen de modo que tenemos un subset 
#de la imagen original
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

        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        HashMap = jpy.get_type('java.util.HashMap')
        BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')

#generamos la nueva banda (indice de vegetacion), a partir de la expresion 
#proporcionada.
        targetBand = BandDescriptor()
        targetBand.name = name
        targetBand.type = 'float32'
        targetBand.expression = expr
        targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
        targetBands[0] = targetBand

        parameters = HashMap()
        parameters.put('targetBands', targetBands)
        result = GPF.createProduct('BandMaths', parameters, subset)
        print "Vegetation index ok!"

#leemos la banda que hemos construido
	band=result.getBand(name)
        print band

#imagen en formato PNG
        ImageManager=jpy.get_type('org.esa.snap.core.image.ImageManager')
        JAI=jpy.get_type('javax.media.jai.JAI')
        im=ImageManager.getInstance().createColoredBandImage([band], band.getImageInfo(), 0)
        JAI.create("filestore", im,'%s.png' % (name), 'PNG')
        print "PNG Done!"

#imagen en formato GeoTIFF
        parameters = HashMap()
        parameters.put('sourceBands', name)
        final_result = GPF.createProduct('Subset', parameters, result)
        ProductIO.writeProduct(final_result, '%s.tif' % (name), 'GeoTIFF')
        print "GeoTIFF Done!"
