# sugarapp

sugarapp helps integrate [sugar](https://sugarlabs.org) activities to other desktop environments like [GNOME](https://www.gnome.org). To do this, it provides a base [GTK](https://www.gtk.org) application and set of widgets to:

* Simplify the port process.
* Bypass sugar services.
* Mimic the store-and-restore behavior of activities.
* Extend activities with explicit save-and-open options.

## Usage

Port the activity by replacing `Activity` class by `SugarCompatibleActivity` class, e.g:
```python
from sugarapp.widgets import SugarCompatibleActivity
...

class SpeakActivity(SugarCompatibleActivity):
    def __init__(self, handle):
...
```

And then just run the application:
```
SUGAR_BUNDLE_ID=vu.lux.olpc.Speak SUGAR_BUNDLE_PATH=~/Activities/Speak.activity sugarapp
```

## Improvements

There are MANY possible ways to simplify this even more, or even completely different ways of achieving this. This project is just exploratory, so if you are interested in this, just contact me.
