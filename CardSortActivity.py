#Copyright (c) 2009, Walter Bender

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sugar
from sugar.activity import activity
try: # 0.86+ toolbar widgets
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.graphics.toolbarbox import ToolbarButton
except ImportError:
    pass
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.icon import Icon
from sugar.datastore import datastore

from gettext import gettext as _
import locale
import os.path

from sprites import *
import window

SERVICE = 'org.sugarlabs.CardSortActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/CardSortActivity'

#
# Sugar activity
#
class CardSortActivity(activity.Activity):

    def __init__(self, handle):
        super(CardSortActivity,self).__init__(handle)

        try:
            # Use 0.86 toolbar design
            toolbar_box = ToolbarBox()

            # Buttons added to the Activity toolbar
            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()

            # Blank piece button
            self.blank_piece = ToolButton( "blank-in" )
            self.blank_piece.set_tooltip(_('Blank piece'))
            self.blank_piece.props.sensitive = True
            self.blank_piece.connect('clicked', self._blank_cb)
            toolbar_box.toolbar.insert(self.blank_piece, -1)
            self.blank_piece.show()
            self.blank = False

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing status
            self.results_label = gtk.Label(_("click to rotate; drag to swap"))
            self.results_label.show()
            results_toolitem = gtk.ToolItem()
            results_toolitem.add(self.results_label)
            toolbar_box.toolbar.insert(results_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # The ever-present Stop Button
            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>Q'
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()

        except NameError:
            # Use pre-0.86 toolbar design
            self.toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(self.toolbox)

            self.projectToolbar = ProjectToolbar(self)
            self.toolbox.add_toolbar( _('Project'), self.projectToolbar )

            self.toolbox.show()

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(), \
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        # Initialize the canvas
        self.tw = window.new_window(canvas, \
                                    os.path.join(activity.get_bundle_path(), \
                                                 'images/card'), \
                                    self)


    #
    # Blank piece button callback
    #
    def _blank_cb(self, button):
        if self.blank is False:
            self.blank = True
            self.blank_piece.set_icon("blank-out")
            self.blank_piece.set_tooltip(_('Restore piece'))
            self.results_label.set_text(_("adding blank tile"))
        else:
            self.blank = False
            self.blank_piece.set_icon("blank-in")
            self.results_label.set_text(_("removing blank tile"))
            self.blank_piece.set_tooltip(_('Blank piece'))
        self.tw.grid.toggle_blank()
        redrawsprites(self.tw)
        self.results_label.show()
        return True


#
# Project toolbar for pre-0.86 toolbars
#
class ProjectToolbar(gtk.Toolbar):

    def __init__(self, pc):
        gtk.Toolbar.__init__(self)
        self.activity = pc

        # Blank piece button
        self.activity.blank_piece = ToolButton( "blank-in" )
        self.activity.blank_piece.set_tooltip(_('Blank it'))
        self.activity.blank_piece.props.sensitive = True
        self.activity.blank_piece.connect('clicked', self.activity._blank_cb)
        self.insert(self.activity.blank_piece, -1)
        self.activity.blank_piece.show()
        self.activity.blank = False

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        # Label for showing status
        self.activity.results_label = gtk.Label(\
            _("click to rotate; drag to swap"))
        self.activity.results_label.show()
        self.activity.results_toolitem = gtk.ToolItem()
        self.activity.results_toolitem.add(self.activity.results_label)
        self.insert(self.activity.results_toolitem, -1)
        self.activity.results_toolitem.show()
