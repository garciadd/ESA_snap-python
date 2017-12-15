# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 13:12:06 2017
@author: Daniel García Díaz

A partir de los archivos originales descargados de la ESA, el código extrae la información disponible (fecha, bandas disponibles, ...). 
Una vez escogido el archivo y la banda que se desea tratar, la función realiza un resample en la resolución de las bandas, 
corta la imagen original seleccionando solo el polígono deseado y trata la banda de forma que guarda una imagen en formato PNG 
y otra en formato GeoTIFF, es decir, georeferenciada. 
"""

#Importamos las funciones a utilizar
import numpy as np

import sys
sys.path.append('/home/ubuntu/.snap/snap-python')
from snappy import (ProductIO, jpy, GPF, HashMap)

#Inputs de la funcion. path del archivo y banda.
path='folder+file'
band_name='B8A'

#Extraemos la infromacion del producto, nombre, bandas que continene, .....
p = ProductIO.readProduct(path)
print("the product %s" % (p.getName()))
print("Bands:   %s" % (list(p.getBandNames())))


#funcion; necesita como Inputs el path y la banda a tratar. El output de la funcion son dos imagenes, una en formato png
#y otra en formato GeoTIF
def band_to_array(band_name, path):

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
    
#leemos la banda que hemos escogido. Esta imagen ya no tendra las dimensiones (Height * Width) de la imagen original,
#si no que solo sera el subset ya cortado por el poligono anterior
    band=subset.getBand(band_name)
    print band

#creamos una imagen de la banda formato png.
    ImageManager=jpy.get_type('org.esa.snap.core.image.ImageManager')
    JAI=jpy.get_type('javax.media.jai.JAI')
    im=ImageManager.getInstance().createColoredBandImage([band], band.getImageInfo(), 0)
    JAI.create("filestore", im,'%s.png' % (band_name), 'PNG')
    print "PNG Done!"

#creamos una imagen de la banda formato GeoTIFF
    parameters = HashMap()
    parameters.put('sourceBands', band_name)
    result = GPF.createProduct('Subset', parameters, subset)
    ProductIO.writeProduct(result, '%s.tif' % (band_name), 'GeoTIFF')
    print "GeoTIFF Done!"
