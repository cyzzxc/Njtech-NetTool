# sample2.tcl -
#
# This file is loaded by sample.tcl
#
# $Id: sample2.tcl,v 1.1 2005/09/27 02:05:50 patthoyts Exp $

lappend auto_path [pwd]
package require Winico

proc winico_seticon { w icofile } {
  set ico [winico create $icofile]
  set screendepth [winfo screendepth .]
  set bigsize "32x32"
  set bigpos -1
  set bigdepth 0
  set smallsize "16x16"
  set smallpos -1
  set smalldepth 0
  foreach i [winico info $ico] {
    array set opts $i
    set depth    $opts(-bpp)
    set pos      $opts(-pos)
    set geometry $opts(-geometry)
    if { $geometry=="$bigsize" && $depth<=$screendepth } {
      if { $depth>$bigdepth } {
        set bigpos $pos
        set bigdepth $depth
      }
    } elseif { $geometry=="$smallsize" && $depth<=$screendepth } {
      if { $depth>$smalldepth } {
        set smallpos $pos
        set smalldepth $depth
      }
    }
  }
    if { $bigpos==-1 && $smallpos==-1 } {
    puts stderr "couldn't find $bigsize and $smallsize icons in $icofile"
    return $ico
  } elseif { $bigpos==-1 } {
    set bigpos $smallpos
    puts stderr "couldn't find $bigsize icons in $icofile"
  } elseif { $smallpos==-1 } {
    set smallpos $bigpos
    puts stderr "couldn't find $smallsize icons in $icofile"
  }
  #puts stderr "big icon is $bigsize,bpp:$bigdepth,pos:$bigpos"
  #puts stderr "small icon is $smallsize,bpp:$smalldepth,pos:$smallpos"
  winico setwindow $w $ico big   $bigpos
  winico setwindow $w $ico small $smallpos
  return $ico
}
proc winico_delall {} {
  foreach i [winico info] { winico delete $i }
}
proc winico_loadicon { w symbol } {
  set ico [winico load $symbol]
  winico setwindow $w $ico big
  winico setwindow $w $ico small
}
proc taskbar_cmd { message ico wparam lparam x y } {
  puts stderr "taskbar_cmd with $message,ico:$ico,wParam:$wparam,lParam:$lparam,x:$x,y:$y"
}
update
set ico [winico_seticon . [file join [file dirname [info script]] smiley.ico]]
#new new new
winico text $ico "This is a taskbar sample text"
winico taskbar add $ico -callback "taskbar_cmd %m %i %w %l %x %y"

after 20000 "winico delete $ico"
