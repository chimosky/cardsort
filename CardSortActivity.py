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
from sugar.bundle.activitybundle import ActivityBundle
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbarbox import ToolbarButton
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.icon import Icon
from sugar.graphics import style
from sugar.datastore import datastore

from sugar import profile
from gettext import gettext as _
import locale
import os.path
from sprites import *
from math import sqrt

class taWindow: pass

SERVICE = 'org.sugarlabs.CardSortActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/CardSortActivity'

CARD_DIM = 135
CARD_DEFS = ((1,3,-2,-3),(2,3,-3,-2),(2,3,-4,-4),\
             (2,1,-1,-4),(3,4,-4,-3),(4,2,-1,-2),\
             (1,1,-2,-4),(4,2,-3,-4),(1,3,-1,-2))


#
# class for defining 3x3 matrix of cards
#
class Grid:
    # 123
    # 456
    # 789
    def __init__(self,tw):
        self.grid = [1,2,3,4,5,6,7,8,9]
        self.card_table = {}
        # Initialize the cards
        i = 0
        x = (tw.width-(CARD_DIM*3))/2
        y = (tw.height-(CARD_DIM*3))/2
        for c in CARD_DEFS:
            self.card_table[i] = Card(tw,c,i,x,y)
            self.card_table[i].draw_card()
            x += CARD_DIM
            if x > (tw.width+(CARD_DIM*2))/2:
                x = (tw.width-(CARD_DIM*3))/2
                y += CARD_DIM
            i += 1

    def swap(self,a,b):
        # swap grid elements and x,y positions of sprites
        print "swapping cards " + str(a) + " and " + str(b)
        tmp = self.grid[a]
        x = self.card_table[a].spr.x
        y = self.card_table[a].spr.y
        self.grid[a] = self.grid[b]
        self.card_table[a].spr.x = self.card_table[b].spr.x
        self.card_table[a].spr.y = self.card_table[b].spr.y
        self.grid[b] = tmp
        self.card_table[b].spr.x = x
        self.card_table[b].spr.y = y

    def print_grid(self):
        print self.grid
        return

    def test(self):
        for i in (0,1,3,4,6,7):
            if self.card_table[self.grid[i]].east + \
               self.card_table[self.grid[i+1]].west != 0:
                return False
        for i in (0,1,2,3,4,5):
            if self.card_table[self.grid[i]].south + \
               self.card_table[self.grid[i+3]].north != 0:
                return False
        return True


#
# class for defining individual cards
#
class Card:
    # Spade   = 1,-1
    # Heart   = 2,-2
    # Club    = 3,-3
    # Diamond = 4,-4
    def __init__(self,tw,c,i,x,y):
        self.north = c[0]
        self.east = c[1]
        self.south = c[2]
        self.west = c[3]
        self.rotate = 0
        # create sprite from svg file
        self.spr = sprNew(tw,x,y,self.load_image(tw.path,i))
        self.spr.label = i

    def draw_card(self):
        setlayer(self.spr,2000)
        draw(self.spr)

    def load_image(self, file, i):
        print "loading " + os.path.join(file + str(i) + '.svg')
        return gtk.gdk.pixbuf_new_from_file(os.path.join(file + \
                                                         str(i) + "x" + \
                                                         '.svg'))

    def rotate_ccw(self):
        # print "rotating card " + str(self.spr.label)
        tmp = self.north
        self.north = self.east
        self.east = self.south
        self.south = self.west
        self.west = tmp
        self.rotate += 90
        if self.rotate > 359:
            self.rotate -= 360
        tmp = self.spr.image.rotate_simple(90)
        self.spr.image = tmp

    def print_card(self):
        print "(" + str(self.north) + "," + str(self.east) + \
              "," + str(self.south) + "," + str(self.west) + \
              ") " + str(self.rotate) + "ccw" + \
              " x:" + str(self.spr.x) + " y:" + str(self.spr.y)

#
# Sugar activity
#
class CardSortActivity(activity.Activity):

    def __init__(self, handle):
        super(CardSortActivity,self).__init__(handle)

        # Use 0.86 toolbar design
        toolbar_box = ToolbarBox()

        # Buttons added to the Activity toolbar
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        # Solver button
        self.solve_puzzle = ToolButton( "solve-off" )
        self.solve_puzzle.set_tooltip(_('Solve it'))
        self.solve_puzzle.props.sensitive = True
        self.solve_puzzle.connect('clicked', self._solver_cb)
        toolbar_box.toolbar.insert(self.solve_puzzle, -1)
        self.solve_puzzle.show()

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

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(), \
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        self.show_all()

        # Initialize the canvas
        self.tw = taWindow()
        self.tw.window = canvas
        canvas.set_flags(gtk.CAN_FOCUS)
        canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        canvas.connect("expose-event", self._expose_cb, self.tw)
        canvas.connect("button-press-event", self._button_press_cb, self.tw)
        canvas.connect("button-release-event", self._button_release_cb, self.tw)
        self.tw.width = gtk.gdk.screen_width()
        self.tw.height = gtk.gdk.screen_height()-style.GRID_CELL_SIZE
        self.tw.area = canvas.window
        self.tw.gc = self.tw.area.new_gc()
        self.tw.scale = 3
        self.tw.cm = self.tw.gc.get_colormap()
        self.tw.msgcolor = self.tw.cm.alloc_color('black')
        self.tw.sprites = []

        # Initialize the grid
        self.tw.path = os.path.join(activity.get_bundle_path(),'images/card')
        self.tw.grid = Grid(self.tw)

        # Start solving the puzzle
        self.tw.press = -1
        self.tw.release = -1
        self.tw.start_drag = [0,0]

    #
    # Solver
    #
    def _solver_cb(self, button):
        self.solve_puzzle.set_icon("solve-on")
        """
        We need to write this code
        """
        self.results_label.set_text(_("I don't know how to solve it."))
        self.results_label.show()
        self.solve_puzzle.set_icon("solve-off")
        return True


    #
    # Repaint
    #
    def _expose_cb(self, win, event, tw):
        redrawsprites(tw)
        return True

    #
    # Button press
    #
    def _button_press_cb(self, win, event, tw):
        win.grab_focus()
        x, y = map(int, event.get_coords())
        tw.start_drag = [x,y]
        spr = findsprite(tw,(x,y))
        if spr is None:
            tw.press = -1
            tw.release = -1
            return True
        # take note of card under button press
        tw.press = spr.label
        return True

    #
    # Button release
    #
    def _button_release_cb(self, win, event, tw):
        win.grab_focus()
        x, y = map(int, event.get_coords())
        spr = findsprite(tw,(x,y))
        if spr is None:
            tw.press = -1
            tw.release = -1
            return True
        # take note of card under button release
        tw.release = spr.label
        # if the same card (click) then rotate
        if tw.press == tw.release:
            # check to see if it was an aborted move
            if self.distance(tw.start_drag,[x,y]) < 20:
                tw.grid.card_table[tw.press].rotate_ccw()
                # tw.grid.card_table[tw.press].print_card()
        # if different card (drag) then swap
        else:
            tw.grid.swap(tw.press,tw.release)
            # tw.grid.print_grid()
        inval(tw.grid.card_table[tw.press].spr)
        inval(tw.grid.card_table[tw.release].spr)
        redrawsprites(tw)
        tw.press = -1
        tw.release = -1
        if tw.grid.test() == True:
            self.results_label.set_text(_("You solved the puzzle."))
            self.results_label.show()
        else:
            self.results_label.set_text(_("Keep trying."))
            self.results_label.show()

        return True

    def distance(self,start,stop):
        dx = start[0]-stop[0]
        dy = start[1]-stop[1]
        return sqrt(dx*dx+dy*dy)
