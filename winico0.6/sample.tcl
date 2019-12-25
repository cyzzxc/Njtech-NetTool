# sample.tcl -
#
#  This is one of the original test files provided with the winico package.
#
# $Id: sample.tcl,v 1.1 2005/09/27 02:05:50 patthoyts Exp $

package require Tk 8.4

# Load winico - first look in the build directories for a dll to load
#
set srcdir [file dirname [file dirname [info script]]]
set dbgfile [file join $srcdir win Debug winico06g.dll]
set relfile [file join $srcdir win Release winico06.dll]
if {[file exists $dbgfile]} {
    load $dbgfile
} elseif {[file exists $relfile]} {
    load $relfile
} else {
    tk_messageBox -message "not found in $dbgfile"
}

package require Winico 0.6

# -------------------------------------------------------------------------

console show
wm withdraw .
set dir [pwd]
if ![catch {winico load exclamation} msg] {
    puts "1st Exclamation Test passed."
    console eval "wm geometry . 50x25+0+0"
    wm deiconify .;
    raise .;
    update
    wm geometry . +400+0
    update

    winico setwindow . [set msg]
    puts "you should see a exclamation icon in ."
    update
    after 4000
 
    set ndx [lsearch -glob [info loaded] *winico*]
    foreach {dll pkg} [lindex [info loaded] $ndx] break
    set l [winico load leo $dll]
    winico setwindow . [set l]
    puts "you should see a leo icon in ."
    update
    after 4000

    source [file join [file dirname [info script]] sample2.tcl]
    puts "you should see a red smiley in ."
    puts "and a yellow smiley in the Task-List"
    puts "now go to the taskbar status area"
    puts "and move the mouse over the smiley"
    after 20000 "exit 0"

} else {
    puts "[set msg]:Winico failed to load and run"
    after 5000 "exit 1"
}

