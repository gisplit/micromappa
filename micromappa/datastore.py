#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json




class DataStore:


    def __init__(self):
        self.data={"type": "FeatureCollection", "features": []}
        self.bbox=None

    def load_geojson(self,filename):
        self.__reset()
        self.data=json.load(open(filename,'r'))

    def data_to_track(self):
        for feature in self.data['features']:
            coordinates=feature['geometry']['coordinates']
            feature_type=feature['geometry']['type']
            data=[]
            if feature_type=='Point' or feature_type=='LineString':
                if feature_type=='Point':
                    coord=coordinates[:2] 
                    self.__append_point_in_bbox(coord)
                    coord.reverse()
                    data.append([coord])
                else:
                    line=[]
                    for point in coordinates:
                        coord=point[:2]
                        self.__append_point_in_bbox(coord)
                        coord.reverse()
                        line.append(coord)
                    data.append(line)
                yield data
            else:
                if feature_type=='Polygon' or feature_type=='MultiLineString':
                    for geometry in coordinates:
                        line=[]
                        for point in line:
                            coord=point[:2]
                            self.__append_point_in_bbox(coord)
                            coord.reverse()
                        data.append(line)
                elif feature_type=='MultiPoint':          
                    for point in coordinates:
                        coord=point[:2]
                        self.__append_point_in_bbox(coord)
                        coord.reverse()
                        data.append([coord])
                elif feature_type=='MultiPolygon':
                    for polygon in coordinates:
                        for geometry in polygon:
                             line=[]
                             for point in geometry:
                                 coord=point[:2]
                                 self.__append_point_in_bbox(coord)
                                 coord.reverse()
                                 line.append(coord)
                             data.append(line)
                yield data

    def __append_point_in_bbox(self,point):
        try:
            new_bbox=[]
            new_bbox.append(min(self.bbox[0],point[0]))
            new_bbox.append(min(self.bbox[1],point[1]))
            new_bbox.append(max(self.bbox[2],point[0]))
            new_bbox.append(max(self.bbox[3],point[1]))
            self.bbox=new_bbox
        except TypeError:
            self.bbox=[point[0],point[1],point[0],point[1]]

    def __reset(self):self.bbox=None

