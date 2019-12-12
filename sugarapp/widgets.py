# widgets.py
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

import gi
import json
import os
import signal

from xml.dom import minidom

gi.require_version('Gtk', '3.0')

from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk

from sugar3.activity.activity import _
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.datastore.datastore import DSMetadata
from sugar3.bundle.activitybundle import get_bundle_instance
from sugar3.graphics import style
from sugar3.graphics.toolbutton import ToolButton

from .helpers import PrimaryMonitor


class SugarCompatibleWindow(Gtk.ApplicationWindow):
    def __init__(self, **args):
        Gtk.ApplicationWindow.__init__(self, **args)

        self.set_decorated(False)
        display = Gdk.Display.get_default()
        self.fullscreen_on_monitor(
            display.get_default_screen(),
            PrimaryMonitor.get_number())

        self._toolbar_box = None
        self._alerts = []
        self._canvas = None

        self.__vbox = Gtk.VBox()
        self.__hbox = Gtk.HBox()
        self.__vbox.pack_start(self.__hbox, True, True, 0)
        self.__hbox.show()

        self.add_events(Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.TOUCH_MASK)

        self.add(self.__vbox)
        self.__vbox.show()

    def is_fullscreen(self):
        return True

    def set_canvas(self, canvas):
        if self._canvas:
            self.__hbox.remove(self._canvas)

        if canvas:
            self.__hbox.pack_start(canvas, True, True, 0)

        self._canvas = canvas
        self.__vbox.set_focus_child(self._canvas)

    def get_canvas(self):
        return self._canvas

    canvas = property(get_canvas, set_canvas)

    def get_toolbar_box(self):
        return self._toolbar_box

    def set_toolbar_box(self, toolbar_box):
        if self._toolbar_box:
            self.__vbox.remove(self._toolbar_box)

        if toolbar_box:
            self.__vbox.pack_start(toolbar_box, False, False, 0)
            self.__vbox.reorder_child(toolbar_box, 0)

        self._toolbar_box = toolbar_box

    toolbar_box = property(get_toolbar_box, set_toolbar_box)

    def add_alert(self, alert):
        self._alerts.append(alert)
        if len(self._alerts) == 1:
            self.__vbox.pack_start(alert, False, False, 0)
            if self._toolbar_box is not None:
                self.__vbox.reorder_child(alert, 1)
            else:
                self.__vbox.reorder_child(alert, 0)

    def remove_alert(self, alert):
        if alert in self._alerts:
            self._alerts.remove(alert)
            if alert.get_parent() is not None:
                self.__vbox.remove(alert)
                if len(self._alerts) >= 1:
                    self.__vbox.pack_start(self._alerts[0], False, False, 0)
                    if self._toolbar_box is not None:
                        self.__vbox.reorder_child(self._alerts[0], 1)
                    else:
                        self.__vbox.reorder_child(self._alert[0], 0)

    def set_enable_fullscreen_mode(self, enable_fullscreen_mode):
        pass

    def get_enable_fullscreen_mode(self):
        return False

    enable_fullscreen_mode = GObject.Property(
        type=object,
        setter=set_enable_fullscreen_mode,
        getter=get_enable_fullscreen_mode)


class SugarCompatibleActivity(SugarCompatibleWindow, Gtk.Container):

    __gtype_name__ = 'SugarCompatibleActivity'

    __gsignals__ = {
        'shared': (GObject.SignalFlags.RUN_FIRST, None, ([])),
        'joined': (GObject.SignalFlags.RUN_FIRST, None, ([])),
        '_closing': (GObject.SignalFlags.RUN_FIRST, None, ([])),
    }

    def __init__(self, handle, create_jobject=True):
        if hasattr(GLib, 'unix_signal_add'):
            GLib.unix_signal_add(
                GLib.PRIORITY_DEFAULT, signal.SIGINT, self.close)

        icons_path = os.path.join(self._get_bundle_path(), 'icons')
        Gtk.IconTheme.get_default().append_search_path(icons_path)

        sugar_theme = 'sugar-72'
        if 'SUGAR_SCALING' in os.environ:
            if os.environ['SUGAR_SCALING'] == '100':
                sugar_theme = 'sugar-100'

        settings = Gtk.Settings.get_default()
        settings.set_property('gtk-theme-name', sugar_theme)
        settings.set_property('gtk-icon-theme-name', 'sugar')
        settings.set_property('gtk-button-images', True)
        settings.set_property('gtk-font-name',
                              '%s %f' % (style.FONT_FACE, style.FONT_SIZE))

        SugarCompatibleWindow.__init__(self)

        self._handle = handle
        self._read_file_called = False

        bundle = get_bundle_instance(self._get_bundle_path())
        self.set_icon_from_file(bundle.get_icon())

        self._restore_metadata()

    def add_stop_button(self, button):
        pass

    def iconify(self):
        pass

    def run_main_loop(self):
        pass

    def get_active(self):
        return True

    def set_active(self, active):
        pass

    active = GObject.Property(
        type=bool, default=False, getter=get_active, setter=set_active)

    def get_max_participants(self):
        return 1

    def set_max_participants(self, participants):
        pass

    max_participants = GObject.Property(
        type=int, default=0, getter=get_max_participants,
        setter=set_max_participants)

    def get_id(self):
        return self._handle.activity_id

    def get_bundle_id(self):
        return os.environ['SUGAR_BUNDLE_ID']

    def get_canvas(self):
        return SugarCompatibleWindow.get_canvas(self)

    def set_canvas(self, canvas):
        SugarCompatibleWindow.set_canvas(self, canvas)
        if not self._read_file_called:
            canvas.connect('map', self.__canvas_map_cb)

    canvas = property(get_canvas, set_canvas)

    def get_activity_root(self):
        return os.environ['SUGAR_ACTIVITY_ROOT']

    def read_file(self, file_path):
        raise NotImplementedError

    def write_file(self, file_path):
        raise NotImplementedError

    def notify_user(self, summary, body):
        pass

    def save(self):
        try:
            self.write_file(self._get_autosave_filename())
        except NotImplementedError:
            pass

    def get_shared_activity(self):
        return None

    def get_shared(self):
        return False

    shared_activity = property(get_shared_activity, None)

    def invite(self, account_path, contact_id):
        pass

    def share(self, private=False):
        pass

    def can_close(self):
        return True

    def close(self, skip_save=False):
        self.can_close()
        self.save()
        self._save_metadata()
        self.emit('_closing')

    def __delete_event_cb(self, widget, event):
        self.close()
        return True

    def get_metadata(self):
        return self._metadata

    def set_metadata(self, metadata):
        pass

    metadata = property(get_metadata, None)

    def handle_view_source(self):
        pass

    def get_document_path(self, async_cb, async_err_cb):
        pass

    def busy(self):
        pass

    def unbusy(self):
        pass

    def get_filename_suffix(self):
        filepath = os.path.join(
            self._get_bundle_path(),
            'activity',
            'mimetypes.xml')
        if not os.path.exists(filepath):
            return ''

        xml = minidom.parse(filepath)
        items = xml.getElementsByTagName('glob')
        if not items:
            return ''

        pattern = items[0].attributes['pattern'].value
        return pattern.replace('*', '')

    def _get_bundle_path(self):
        return os.environ['SUGAR_BUNDLE_PATH']

    def _get_autosave_filename(self):
        return GLib.build_filenamev([GLib.get_user_data_dir(), 'autosave'])

    def _get_preferred_filename(self):
        if self._handle.uri:
            return self._handle.uri
        return self._get_autosave_filename()

    def _save_metadata(self):
        if not self._metadata:
            return
        metadata_path = self._get_autosave_filename() + '.metadata'
        with open(metadata_path, 'w') as metadata_file:
            properties = self._metadata.get_dictionary()
            metadata_file.write(json.dumps(properties))

    def _restore_metadata(self):
        properties = {}
        metadata_path = self._get_autosave_filename() + '.metadata'
        try:
            with open(metadata_path, 'r') as metadata_file:
                properties = json.loads(metadata_file.read())
        except:
            pass
        if 'title' not in properties:
            properties['title'] = ''
        self._metadata = DSMetadata(properties)

    def __canvas_map_cb(self, canvas):
        try:
            self.read_file(self._get_preferred_filename())
        except Exception:
            pass
        self._read_file_called = True
        canvas.disconnect_by_func(self.__canvas_map_cb)


class ExtendedActivityToolbarButton(ActivityToolbarButton):

    __gtype_name__ = 'ExtendedActivityToolbarButton'

    def __init__(self, activity):
        ActivityToolbarButton.__init__(self, activity)
        self._activity = activity
        GLib.idle_add(self.__setup_buttons_cb)

    def __setup_buttons_cb(self):
        save_button = ToolButton(icon_name='document-save')
        save_button.props.tooltip = _("Save")
        save_button.connect('clicked', self.__save_clicked_cb)
        save_button.show()
        save_button.set_sensitive(True)
        self.page.insert(save_button, -1)

        open_button = ToolButton(icon_name='document-open')
        open_button.props.tooltip = _("Open")
        open_button.connect('clicked', self.__open_clicked_cb)
        open_button.show()
        open_button.set_sensitive(True)
        self.page.insert(open_button, -1)

    def __save_clicked_cb(self, widget):
        suffix = self._activity.get_filename_suffix()
        filename = _('Untitled') + suffix
        chooser = DesktopSaveChooser(self._activity, filename=filename)
        chooser.add_filter(suffix, _("Default"))
        filename = chooser.get_filename()
        if filename:
            self._activity.write_file(filename)

    def __open_clicked_cb(self, widget):
        chooser = DesktopOpenChooser(self._activity)
        chooser.add_filter(self._activity.get_filename_suffix(), _("Default"))
        filename = chooser.get_filename()
        if filename:
            self._activity.read_file(filename)


class DesktopOpenChooser(object):

    __gtype_name__ = 'DesktopOpenChooser'

    def __init__(self, activity):
        self._activity = activity
        self._setup_chooser()

    def get_filename(self):
        if self._chooser.run() != Gtk.ResponseType.ACCEPT:
            return None
        return self._chooser.get_filename()

    def add_filter(self, suffix, name):
        if not suffix:
            return
        file_filter = Gtk.FileFilter()
        file_filter.add_pattern('*' + suffix)
        file_filter.set_name(name)
        self._chooser.add_filter(file_filter)

    def _setup_chooser(self):
        self._chooser = Gtk.FileChooserNative.new(
            None,
            self._activity,
            Gtk.FileChooserAction.OPEN,
            '_Open',
            '_Cancel')


class DesktopSaveChooser(DesktopOpenChooser):

    __gtype_name__ = 'DesktopSaveChooser'

    def __init__(self, activity, filename=_('untitled')):
        self._filename = filename
        DesktopOpenChooser.__init__(self, activity)

    def _setup_chooser(self):
        self._chooser = Gtk.FileChooserNative.new(
            None,
            self._activity,
            Gtk.FileChooserAction.SAVE,
            '_Save',
            '_Cancel')
        self._chooser.set_current_name(self._filename)
        self._chooser.set_do_overwrite_confirmation(True)
