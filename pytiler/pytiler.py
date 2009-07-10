#! /usr/bin/env python
import wnck
import sys
import pdb
import subprocess


fraction=0.65
reserve_top=0
reserve_bottom=0
reserve_left=0
reserve_right=0
check_ob_decorated=True

tile=sys.argv[1]
screen = wnck.screen_get_default()
screen.force_update()

# Get usable screen corners
screen_left=0+reserve_left
screen_top=0+reserve_top
screen_bottom = screen.get_height()-reserve_bottom
screen_right = screen.get_width()-reserve_right

# Usable screen dimensions
screen_width=screen_right-screen_left
screen_height=screen_bottom-screen_top

# Constants
geometry_mask=wnck.WINDOW_CHANGE_X|wnck.WINDOW_CHANGE_Y|wnck.WINDOW_CHANGE_HEIGHT|wnck.WINDOW_CHANGE_WIDTH
window_gravity=wnck.WINDOW_GRAVITY_STATIC

# Only normal windows, only on the active desktop
active_workspace = screen.get_active_workspace()
windows = [ w for w in screen.get_windows() if w.is_on_workspace(active_workspace) and not w.is_skip_tasklist() ]

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
          
if tile in ["maximise"]:
    for window in windows:                
        window.maximize()
        window.maximize()
        
elif tile in ["left"]:
    # Dimensions
    side_w=int(screen_width*(1-fraction))       
    side_h=int(screen_height/(len(windows)-1))     
    master_w=int(screen_width*fraction)
    master_h=screen_height
    
    # Co-ordinates
    master_y=screen_top
    master_x=screen_left
    side_y=screen_top
    side_x=master_w+1
    
    for window in windows:
        window.unmaximize()
        if window.is_active():
            ymod=0
            # wnck assumes everything has decorations, so check if a window is undecorated and then resize/move accordingly
            if openbox_undecorated(window):
                ymod=decoration_size(window)
                print "undecorated window"
                                                  
            window.set_geometry(window_gravity, geometry_mask, master_x,master_y-ymod,master_w,master_h+ymod) 
            
        else:
            ymod=0
            if openbox_undecorated(window):
                ymod=decoration_size(window) 
                print "undecorated window",            
            window.set_geometry(window_gravity, geometry_mask, side_x, side_y-ymod, side_w, side_h+ymod)  
            side_y+=side_h
 
# ConfigParser()            
# hypothetical epic management
# on window create/destroy re-layout
# gtk.main()
# connect()
# on event, run layout hook. simple!
