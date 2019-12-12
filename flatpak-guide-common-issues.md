# List of common issues while porting Sugar applications to the Desktop

## Invoking the Datastore directly

Sugar applications could access the Datastore API directly. Since there is no such service in Sugarapp, it will simply fail. Therefore, the functionality needs to be replaced. Here is a real example:

The Music Keyboard application allows the user to export the song to a `.ogg` file, in the following way:

```python
from sugar3.datastore import datastore

title = '%s saved as audio' % self.metadata['title']
jobject = datastore.create()
jobject.metadata['title'] = title
jobject.metadata['keep'] = '0'
jobject.metadata['mime_type'] = 'audio/ogg'
jobject.file_path = self._ogg_tempfile.name
datastore.write(jobject)
```

The issue here is that `datastore.write()` will always fail. For this reason Sugarapp provides widgets to replace this functionality.


```python
import shutil

from sugarapp.widgets import DesktopSaveChooser

chooser = DesktopSaveChooser(self, filename='untitled.ogg')
filename = chooser.get_filename()
if filename:
    shutil.copyfile(self._ogg_tempfile.name, filename)
```

The `DesktopSaveChooser` (and it counter-part `DesktopOpenChooser`) is capable of accessing the file system from within the Flatpak sandbox.

## Calculating the size of the Screen

Most Sugar applications were not developed with multiple monitor setups in mind. But it's common in the desktop world.

These applications use deprecated APIs such as `Gdk.Screen.width()`, which returns the sum of all the width available by all monitors as a single screen. This means that these calculations will be wrong under multiple monitors setups, resulting in width or height values that exceeds the physical space of these monitors. Becoming unusable.

To deal with this issue, Sugarapp provides a `PrimaryMonitor` helper to a) guarantee that the application will run exclusively on the primary monitor of the system, and to b) provide access these width and height values consistently. Here is another real example:

```python
self.width = Gdk.Screen.width()
self.height = Gdk.Screen.height() - GRID_CELL_SIZE
```

The Abacus application uses this API to calculate the size of some of its widget, but can be easily fixed with the helper:

```python
from sugarapp.helpers import PrimaryMonitor

self.width = PrimaryMonitor.width()
self.height = PrimaryMonitor.height() - GRID_CELL_SIZE
```
