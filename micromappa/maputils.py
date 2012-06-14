#!/usr/bin/env python
# -*- coding: utf-8 -*-



import math



def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = float((lon_deg + 180.0) / 360.0 * n)
    ytile = float((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return xtile, ytile


def bbox2center(bbox):
    '''Return center of bbox'''
    x=bbox[0]+abs(bbox[2]-bbox[0])/2.0
    y=bbox[1]+abs(bbox[3]-bbox[1])/2.0
    return x,y


def bbox2size(bbox,zoom):
    minx,miny=deg2num(bbox[0],bbox[1],zoom)
    maxx,maxy=deg2num(bbox[2],bbox[3],zoom)
    x=(maxx-minx)*256
    y=(miny-maxy)*256
    return x,y


