# helpers.py
#
# Copyright 2019 Martin Abente Lahaye
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

from gi.repository import Gdk
from gi.repository import GObject


class PrimaryMonitor(object):

    @staticmethod
    def width():
        geometry = PrimaryMonitor.get_geometry()
        return geometry.width

    @staticmethod
    def height():
        geometry = PrimaryMonitor.get_geometry()
        return geometry.height

    @staticmethod
    def get_geometry():
        monitor = PrimaryMonitor.get_monitor()
        return monitor.get_geometry()

    @staticmethod
    def get_monitor():
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        # wayland don't support primary monitor
        if monitor is None:
            monitor = display.get_monitor(PrimaryMonitor.get_number())
        return monitor

    @staticmethod
    def get_number():
        display = Gdk.Display.get_default()
        number = 0
        for n in range(0, display.get_n_monitors() + 1):
            monitor = display.get_monitor(n)
            if monitor.is_primary():
                number = n
                break
        return number
