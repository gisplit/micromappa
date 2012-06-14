#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import osmgpsmap
import os

import layerstore
import maputils
import constants

__NAME__='MicroMappa'
__WEBSITE__='https://github.com/gisplit/micromappa'
__VERSION__='0.1.9'
__AUTHOR__='Michail Shishkin'
__COMMENT__='Application to view geojson data'




class MicroMappa(gtk.Builder):


    def delete_event(self, *args):
        return False

    def destroy(self,*args):
        gtk.main_quit()

    def __init__(self):
        gtk.Builder.__init__(self)
        self.add_from_file(constants.GUI_BASE+'/micromappa_gui.glade')
        self.connect_signals(self)
        #Map
        self.map=osmgpsmap.GpsMap()
        self.get_object('mapbox').pack_start(self.map,True,True)
        #Data
        self.data=layerstore.LayerStore()
        self.layers_features=[]
        #Configure window
        self.get_object('window').set_title(__NAME__)
        self.get_object('window').show_all()
        self.get_object('window').maximize()

    def about(self,widget):
        about = gtk.AboutDialog()
        about.set_program_name(__NAME__)
        about.set_version(__VERSION__)
        about.set_copyright(__AUTHOR__)
        about.set_comments(__COMMENT__)
        about.set_website(__WEBSITE__)
        about.set_logo(gtk.gdk.pixbuf_new_from_file(constants.ICON))
        about.run()
        about.destroy()      

    def change_color(self,*args):
        '''Change color of current layer'''
        layer_index=self.__get_layer_index()
        if layer_index is None:
            return False
        color_name,width,alpha=self.__get_current_style()
        self.data.styles[layer_index]=(color_name,width,alpha)
        color=gtk.gdk.Color(color_name)
        for feature_list in self.layers_features[layer_index]:
            for feature in feature_list:
                feature.set_property('color',color)
                feature.set_property('alpha',alpha)       

    def change_layer(self,*args):
        '''Configure layer color/width button'''
        active=self.get_object('layercombobox').get_active()
        if active<0:
            return False
        color_name,width,alpha=self.data.styles[active]
        self.get_object('colorbutton').set_color(gtk.gdk.Color(color_name))
        self.get_object('widthspin').set_value(width)
        self.get_object('colorbutton').set_alpha(int(alpha*65535.0))

    def change_width(self,*args):
        '''Change width if current layer'''
        layer_index=self.__get_layer_index()
        if layer_index is None:
            return False
        color_name,width,alpha=self.__get_current_style()
        self.data.styles[layer_index]=(color_name,width,alpha)
        for feature_list in self.layers_features[layer_index]:
            for feature in feature_list:
                feature.set_property('line-width',width)                     

    def draw_data(self,layer_index):
        layer_features=[]
        color_name,width,alpha=self.data.styles[layer_index]
        color=gtk.gdk.Color(color_name)
        for coordinates in self.data.layers[layer_index].data_to_track():
            tracks=[]
            for points in coordinates:
                track=osmgpsmap.GpsMapTrack()
                for point in points:
                    p=osmgpsmap.point_new_degrees(*point)
                    track.add_point(p)
                track.set_property('line-width',width)
                track.set_property('color',color)
                track.set_property('alpha',alpha)
                self.map.track_add(track)
                tracks.append(track)
            layer_features.append(tracks)
        self.layers_features.append(layer_features)

    def full_zoom(self,*args):
        layer_index=self.__get_layer_index()
        if layer_index is None:
            return False
        bbox=self.data.layers[layer_index].bbox
        restangle=self.map.get_allocation()
        width=restangle[2]
        height=restangle[3]
        z=18
        while True:
            x,y=maputils.bbox2size(bbox,z)
            if width>y and height>x:         
                break
            z-=1
        xc,yc=maputils.bbox2center(bbox)
        self.map.set_center_and_zoom(latitude=yc,longitude=xc,zoom=z)
                     
    def load_file(self,*args):
        filechooserdialog = gtk.FileChooserDialog("Open geojson file", None,
             gtk.FILE_CHOOSER_ACTION_OPEN, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))      
        response = filechooserdialog.run()
        if response == gtk.RESPONSE_OK:
            filename=filechooserdialog.get_filename()
            try:
                #Read and draw file
                layer_index=self.data.load_layer(filename)
                self.draw_data(layer_index)
                #Configure widgets
                name=self.data.names[layer_index]
                self.get_object('layerstore').append([name])
                self.get_object('layercombobox').set_active(layer_index)
                self.get_object('removebutton').set_sensitive(True)
                self.full_zoom()
            except IOError:
                #Error data reading
                dialog = gtk.MessageDialog(None,
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_CLOSE, "Input Error. File %s is not valid."%filename)
                dialog.run()
                dialog.destroy() 
        filechooserdialog.destroy()

    def remove_layer(self,widget):
        layer_index=self.__get_layer_index()
        self.data.remove_layer(layer_index)
        del self.get_object('layerstore')[layer_index]
        #Empty/not empty data
        if len(self.data.layers)==0:
            self.get_object('removebutton').set_sensitive(False)
            self.map.track_remove_all()
        else:
            if layer_index==0:
                self.get_object('layercombobox').set_active(0)
            else:
                self.get_object('layercombobox').set_active(layer_index-1)
            for feature_list in self.layers_features[layer_index]:
                for feature in feature_list:
                    self.map.track_remove(feature)
        self.layers_features.pop(layer_index)


    def save_image(self, widget):
        '''Save map to PNG image'''
        filefilter=gtk.FileFilter()
        filefilter.add_mime_type("image/png")
        filefilter.add_mime_type("image/jpeg")
        #Make dialog
        filechooserdialog = gtk.FileChooserDialog("Save as PNG", None,
             gtk.FILE_CHOOSER_ACTION_SAVE, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)) 
        filechooserdialog.set_current_name('map.png')
        filechooserdialog.set_filter(filefilter)
        response=filechooserdialog.run()
        if response==gtk.RESPONSE_OK:
            filename=filechooserdialog.get_filename() 
            drawable = self.map.window
            colormap = drawable.get_colormap()
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
            pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0,0,0,0, *drawable.get_size())
            try:
                pixbuf.save(filename, 'png')
            except:
                dialog = gtk.MessageDialog(None,
                    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_CLOSE, "Writing Error. File %s is not valid."%filename)
                dialog.run()
                dialog.destroy()      
        filechooserdialog.destroy()

    def zoom_in(self,*args):self.map.zoom_in()

    def zoom_out(self,*args):self.map.zoom_out()

    def __get_layer_index(self):
        '''Return index active layer'''
        active=self.get_object('layercombobox').get_active()
        if active<0:
            return False
        return active

    def __get_current_style(self):
        color=self.get_object('colorbutton').get_color()
        alpha=self.get_object('colorbutton').get_alpha()/65535.0
        width=self.get_object('widthspin').get_value()
        return color.to_string(),width,alpha


def main():
    MicroMappa()
    gtk.main()



if __name__ == "__main__":
    main()
        

