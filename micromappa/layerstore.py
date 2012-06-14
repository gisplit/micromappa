#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import datastore
import constants



class LayerStore:


    def __init__(self):
        self.layers=[]
        self.names=[]
        self.styles=[]

    def load_layer(self,filename):
        layer_index=len(self.layers)
        layer=datastore.DataStore()
        layer.load_geojson(filename)
        self.layers.append(layer)
        base,name=os.path.split(filename)
        self.names.append(name)
        self.styles.append(constants.DEFAULT_STYLE)
        return layer_index

    def remove_layer(self,layer_index):
        for data in (self.layers,self.names,self.styles):
            data.pop(layer_index)

    def set_layer_style(self,layer_index,color,width,alpha):
        style=(color,width,alpha)
        self.styles[layer_index]=style
