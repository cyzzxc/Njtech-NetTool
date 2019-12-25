# demo.tcl - Copyright (C) 2005 Pat Thoyts <patthoyts@users.sourceforge.net>
#
# Winico package demo
#
#
# $Id: demo.tcl,v 1.2 2005/09/27 14:02:54 patthoyts Exp $

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
}

package require Winico 0.6

# -------------------------------------------------------------------------

variable App
if {![info exists App]} { array set App {run 0 cleanup 0 dlg 0 wmstate normal} }

proc Main {} {
    variable App

    wm title . "Winico [package provide Winico] Demo"

    # Load an icon file with multiple icons or default to a system icon.
    set icofile [file join [file dirname [info script]] tkchat.ico]
    if {[file exists $icofile]} {
        set icon [winico createfrom $icofile]
    } else {
        set icon [winico load exclamation]
    }

    # As of 0.6 unicode is supported in the text strings
    winico text $icon "Nothing selected (unicode: \u043a\u043c\u0436)"

    # Create a context menu to tie to the taskbar
    set m [menu .popup -tearoff 0]
    $m add command -label "Item One"   -command [list MenuCommand $icon 1]
    $m add command -label "Item Two"   -command [list MenuCommand $icon 2]
    $m add command -label "Item Three" -command [list MenuCommand $icon 3]
    $m add command -label "Item Four"  -command [list MenuCommand $icon 4]
    $m add separator
    $m add command -label "Withdraw"   -command [list Withdraw $m]
    $m add command -label "Exit"       -command [list Exit]

    # Hook up our taskbar icon and callback procedure
    winico taskbar add $icon -pos 0 \
        -callback [list WinicoCallback $m %m %i %w %l %x %y %H]

    # Create our GUI
    text .t -width 80 -height 10 -yscrollcommand {.s set}
    scrollbar .s -command {.t yview}
    button .d -text Dialog -command [list Dialog]
    button .b -text Exit -command [list Exit]
    grid .t  - .s -sticky news
    grid .d .b -  -sticky ne
    grid rowconfigure . 0 -weight 1
    grid columnconfigure . 0 -weight 1

    bind . <Control-F2> {console show}
    bind . <Escape> {Exit}

    # Wait for the window to map and then change the icon
    tkwait visibility .
    winico setwindow . $icon small 0
    wm protocol . WM_DELETE_WINDOW Exit

    # Run the program and wait for the user to finish.
    tkwait variable [namespace current]::App(run)

    # Remove our taskbar icon and clean up.
    # This needs to be done before we destroy the window!
    winico taskbar delete $icon
    winico delete $icon

    # Finish.
    if {[winfo exists .]} {destroy .}
}

proc MenuCommand {icon index} {
    set text [format "Last selected item $index (%c)" [expr {0x043a + $index}]]
    .t insert end $text {} "\n" {}
    winico taskbar modify $icon -text $text -pos $index
}

proc Dialog {} {
    variable App
    set dlg [toplevel .dlg[incr App(dlg)]]
    pack [entry $dlg.e -textvariable [namespace current]::App($dlg)]
}

proc Withdraw {m} {
    variable App
    if {[wm state .] eq "withdrawn"} {
        set ndx [$m index "Restore"]
        if {$ndx != -1} {
            $m entryconfigure $ndx -label "Withdraw"
        }
        wm state . $App(wmstate)
        wm deiconify .
    } else {
        set ndx [$m index "Withdraw"]
        if {$ndx != -1} {
            $m entryconfigure $ndx -label "Restore"
        }
        set App(wmstate) [wm state .]
        wm withdraw .
    }
}

proc Exit {} {
    set [namespace current]::App(run) 1
}

proc WinicoCallback {popup msg icon wparam lparam x y args} {
    .t insert end "$msg ico:$icon wp:$wparam lp:$lparam @($x,$y) $args\n"
    .t see end
    switch -exact -- $msg {
        WM_RBUTTONUP {
            $popup post $x $y
        }
        WM_LBUTTONUP {
            $popup post $x $y
        }
    }
}

# -------------------------------------------------------------------------

if {!$tcl_interactive} {
    set r [catch [linsert $argv 0 Main] err]
    if {$r} {puts $err}
    exit $r
}

# -------------------------------------------------------------------------
# Local variables:
# mode: tcl
# indent-tabs-mode: nil
# End:
