#! /usr/bin/env python

import wnck
import sys
import pdb
import subprocess
import gtk
import globalhotkeys

globalhotkeys.init()

# Constants
geometry_mask = wnck.WINDOW_CHANGE_X|wnck.WINDOW_CHANGE_Y|wnck.WINDOW_CHANGE_HEIGHT|wnck.WINDOW_CHANGE_WIDTH
window_gravity = wnck.WINDOW_GRAVITY_STATIC


check_ob_decorated=True


Ignore=["gmrun"]

def decoration_size(window):
    """Return the decoration thickness at the top of the window, ignores borders"""
    (a, client, c, d) = window.get_client_window_geometry()
    (a, decoclient, c, d) = window.get_geometry()
    decosize=client-decoclient
    return decosize

def openbox_undecorated(window):
    """Check if a window has decorations in openbox"""
    if not check_ob_decorated:
        return False
    return not subprocess.call("xprop -id "+str(window.get_xid())+"|grep -q _OB_WM_STATE_UNDECORATED", shell=True)
          



class WindowManager (object):
    def __init__(self,screen):
        self.screen=screen
        self.windows=[ w for w in self.screen.get_windows() if not w.is_skip_tasklist() ]

        self.dimensions=ScreenDimensions(screen, 0,0,0,22)
        
        self.screen.connect("window-opened", self.window_opened)
        self.screen.connect("window-closed", self.window_closed)
        self.screen.connect("active-workspace-changed", self.active_workspace_changed)
        self.screen.connect("active-window-changed", self.active_window_changed)
        # TODO: add support for adding/removing workspaces.
        
        self.hotkeys = globalhotkeys.GlobalHotkey()
    
        
        if not self.hotkeys.bind("<Alt>R", self.reshuffle):
            print "FAIL: key taken"
            
            
        layout_maximise(self.windows, self.dimensions)
        
    def window_opened(self, screen, window):
        self.relayout_from_window(window)

        
    def window_closed(self, screen, window):
        self.relayout_from_window(window)
        
    def active_window_changed(self, screen, window):
        pass
        #self.relayout_from_window(window)
        
    def active_workspace_changed(self, screen, workspace):
        pass
       
    def reshuffle(self, *args):
        print "OMG"
        workspace=self.screen.get_active_workspace()
        self.relayout(workspace)
        
    def relayout(self, workspace):
        workspace_name=workspace.get_number()
        windows=[ w for w in self.screen.get_windows() if w and not w.is_skip_tasklist() and w.is_on_workspace(workspace) and not w.is_skip_pager() and not w.get_class_group().get_name() in Ignore]
        
        Workspaces[workspace_name](windows,self.dimensions)    

    def relayout_from_window(self, window):
        if not window:
            return False
        if window.get_class_group().get_name() in Ignore:
            return False
        workspace=window.get_workspace()
        if not workspace:
            return
        self.relayout(workspace)


class ScreenDimensions (object):
    def __init__(self,screen, reserve_left,reserve_right,reserve_top,reserve_bottom):
        
        self.left = 0+reserve_left
        self.top = 0+reserve_top
        self.bottom = screen.get_height()-reserve_bottom
        self.right = screen.get_width()-reserve_right

        self.width=self.right-self.left
        self.height=self.bottom-self.top

def layout_maximise(windows, dimensions):
    print "laying out"
    for window in windows:                
        window.maximize()
        
def layout_left(windows, dimensions):
    
    fraction=0.70
    
    # Dimensions
    if len(windows) == 1:
        return layout_maximise(windows, dimensions)
    
    side_w=int(dimensions.width*(1-fraction))       
    side_h=int(dimensions.height/(len(windows)-1))     
    master_w=int(dimensions.width*fraction)
    master_h=dimensions.height
    
    # Co-ordinates
    master_y=dimensions.top
    master_x=dimensions.left
    side_y=dimensions.top
    side_x=master_w+1
    
    
    active = Screen.get_active_window()

    if not active:
        active = windows.pop()
                
    ymod=0
    if openbox_undecorated(active):
        ymod=decoration_size(active)
        print "undecorated window"                                                
    active.set_geometry(window_gravity, geometry_mask, master_x,master_y-ymod,master_w,master_h+ymod)    

       
    for window in windows:
        window.unmaximize()
        if not window.is_active():
            ymod=0
            if openbox_undecorated(window):
                ymod=decoration_size(window) 
                print "undecorated window",            
            window.set_geometry(window_gravity, geometry_mask, side_x, side_y-ymod, side_w, side_h+ymod)  
            side_y+=side_h
     

Workspaces={0:layout_maximise, 1:layout_left}

        
if __name__ == '__main__':
    Screen = wnck.screen_get_default()    
    wm = WindowManager(Screen)
    gtk.main()


