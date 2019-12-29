# application.py
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

import gettext
import gi
import logging
import os
import sys

gi.require_version('Gtk', '3.0')

from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk

from sugar3 import config
from sugar3 import logger
from sugar3.activity.activityhandle import ActivityHandle
from sugar3.bundle.activitybundle import ActivityBundle
from sugar3.bundle.bundle import MalformedBundleException


logger.start()

_logger = logging.getLogger()


class Application(Gtk.Application):
    def __init__(self):
        if 'SUGAR_BUNDLE_ID' not in os.environ:
            _logger.error("SUGAR_BUNDLE_ID must be set to run application")
            sys.exit(1)
        Gtk.Application.__init__(
            self,
            application_id=os.environ['SUGAR_BUNDLE_ID'],
            flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self._activity = None
        self._path = None

    def do_activate(self):
        if self._activity is None:
            self._activity = self._setup_activity()
            self.add_window(self._activity)
        self._activity.present()

    def do_open(self, files, hint, data):
        self._path = files[0].get_path()
        if self._activity is None:
            self.do_activate()
        else:
            self._activity.read_file(self._path)

    def do_shutdown(self):
        if self._activity is not None:
            self._activity.close()
            self._activity = None
        Gtk.Application.do_shutdown(self)

    def _quit(self, activity):
        self._activity = None
        self.quit()

    def _setup_activity(self):
        if 'SUGAR_BUNDLE_PATH' not in os.environ:
            _logger.error("SUGAR_BUNDLE_PATH must be set to run application")
            sys.exit(1)

        bundle_path = os.environ['SUGAR_BUNDLE_PATH']
        sys.path.insert(0, bundle_path)

        try:
            bundle = ActivityBundle(bundle_path)
        except MalformedBundleException as e:
            _logger.error(e)
            sys.exit(1)

        activity_root = GLib.get_user_data_dir()

        subdirs = [
            os.path.join(activity_root, 'tmp'),
            os.path.join(activity_root, 'data'),
            os.path.join(activity_root, 'instance'),
        ]
        for subdir in subdirs:
            try:
                os.makedirs(subdir)
            except:
                pass

        os.environ['SUGAR_BUNDLE_ID'] = bundle.get_bundle_id()
        os.environ['SUGAR_ACTIVITY_ROOT'] = activity_root
        os.environ['SUGAR_BUNDLE_NAME'] = bundle.get_name()
        os.environ['SUGAR_BUNDLE_VERSION'] = str(bundle.get_activity_version())

        locale_path = config.locale_path
        gettext.bindtextdomain(bundle.get_bundle_id(), locale_path)
        gettext.bindtextdomain('sugar-toolkit-gtk3', config.locale_path)
        gettext.textdomain(bundle.get_bundle_id())

        activity_class = bundle.get_command().split(" ")[1]
        splitted_module = activity_class.rsplit('.', 1)
        module_name = splitted_module[0]
        class_name = splitted_module[1]

        module = __import__(module_name)
        for component in module_name.split('.')[1:]:
            module = getattr(module, component)

        constructor = getattr(module, class_name)
        handle = ActivityHandle(
            activity_id=bundle.get_bundle_id(),
            uri=self._path)

        os.chdir(bundle_path)

        activity = constructor(handle)
        activity.connect('_closing', self._quit)
        activity.show()
        return activity


def main():
    app = Application()
    return app.run(sys.argv)
