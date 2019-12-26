# How to port a Sugar application with Sugarapp and package it with Flatpak (by example)

As a first step read this [blog post](https://blogs.gnome.org/tchx84/2019/11/22/linux-app-summit-2019-and-sugar-learning-tools/) to understand the context and scope of this project.

## Assumptions

You already know the basics for:

1. Use the Linux terminal.
2. Python programming.
3. Git.

## Setting up the development environment

1. Install Flatpak and add the Flathub repository. Find the instructions for almost every Linux distribution [here](https://flatpak.org/setup/).

2. Double check that everything is setup correctly by installing and running an existing application from the terminal.

    ```
    $ flatpak install flathub org.sugarlabs.AbacusActivity
    $ flatpak run org.sugarlabs.AbacusActivity
    ```

3. Use the application as a development environment. The application already comes with all the basic dependencies we need. Including Sugarapp, which is the main library we use to port the Sugar applications to the desktop.

    ```
    $ flatpak run --command=bash org.sugarlabs.AbacusActivity # Enter the development environment
    $ exit # Exit the development environment
    ```

## Porting an application with Sugarapp

1. Get the application source code. Let's use the Implode activity as an example.

    ```
    $ git clone https://github.com/sugarlabs/implode-activity.git
    $ cd implode-activity
    ```

2. Identify the main activity class.

    ```
    $ cat activity/activity.info | grep exec # To find that is the ImplodeActivity class in the implodeactivity.py file
    $ vim implodeactivity.py # Edit the file with you preferred text editor
    ```

3. Replace the Sugar Activity class by the Sugarapp SugarCompatibleActivity class.

    ```diff
    diff --git a/implodeactivity.py b/implodeactivity.py
    index 71900d5..2107df6 100644
    --- a/implodeactivity.py
    +++ b/implodeactivity.py
    @@ -20,8 +20,6 @@ import logging
     _logger = logging.getLogger('implode-activity')
     
     from gettext import gettext as _
    -
    -from sugar3.activity.activity import Activity
     from sugar3.graphics import style
     from sugar3.graphics.icon import Icon
     from sugar3.graphics.radiotoolbutton import RadioToolButton
    @@ -43,8 +41,10 @@ from gi.repository import Gdk
     
     from keymap import KEY_MAP
     
    +from sugarapp.widgets import SugarCompatibleActivity
    +
     
    -class ImplodeActivity(Activity):
    +class ImplodeActivity(SugarCompatibleActivity):
         def __init__(self, handle):
             super(ImplodeActivity, self).__init__(handle)
    ```

4. Run the application with Sugarapp.

    ```
    $ cat activity/activity.info | grep bundle_id # To find that is com.jotaro.ImplodeActivity
    $ flatpak run --command=bash --filesystem=$PWD --socket=session-bus  org.sugarlabs.AbacusActivity # To enter the development environment
    $ SUGAR_BUNDLE_ID=com.jotaro.ImplodeActivity SUGAR_BUNDLE_PATH=$PWD sugarapp
    ```

5. The application will run, but the close button won't work. The reason is that the application is trying to access a file that is outside of its permissions, so we need to fix the application. Like this example, there will be other issues that need to be addressed. In this case the fix is simple because Sugarapp always provides a valid `file_path` to the `write_file` method to persist the application state between sessions. We can remove the other file path.

    ```diff
    diff --git a/implodeactivity.py b/implodeactivity.py
    index 2107df6..8001f9b 100644
    --- a/implodeactivity.py
    +++ b/implodeactivity.py
    @@ -102,15 +102,8 @@ class ImplodeActivity(SugarCompatibleActivity):
         def write_file(self, file_path):
             # Writes the game state to a file.
             game_data = self._game.get_game_state()
    -        file_data = ['Implode save game', [1, 0], game_data]
    -        last_game_path = self._get_last_game_path()
    -        for path in (file_path, last_game_path):
    -            f = open(path, 'wt')
    -            io = StringIO()
    -            json.dump(file_data, io)
    -            content = io.getvalue()
    -            f.write(content)
    -            f.close()
    +        with open(file_path, 'w') as save_file:
    +            save_file.write(json.dumps(game_data))
    ```

    To see the most common issues take a look at this [list](flatpak-guide-common-issues.md).

6. Sugarapp provides widgets to support more interactions with the desktop. As an example, buttons for opening and saving files.

    ```diff
    diff --git a/implodeactivity.py b/implodeactivity.py
    index 8001f9b..f94b659 100644
    --- a/implodeactivity.py
    +++ b/implodeactivity.py
    @@ -25,7 +25,7 @@ from sugar3.graphics.icon import Icon
     from sugar3.graphics.radiotoolbutton import RadioToolButton
     from sugar3.graphics.toolbutton import ToolButton
     
    -from sugar3.activity.widgets import ActivityToolbarButton, StopButton
    +from sugar3.activity.widgets import StopButton
     from sugar3.graphics.toolbarbox import ToolbarBox
     
     from implodegame import ImplodeGame
    @@ -42,6 +42,7 @@ from gi.repository import Gdk
     from keymap import KEY_MAP
     
     from sugarapp.widgets import SugarCompatibleActivity
    +from sugarapp.widgets import ExtendedActivityToolbarButton
     
     
     class ImplodeActivity(SugarCompatibleActivity):
    @@ -145,7 +146,7 @@ class ImplodeActivity(SugarCompatibleActivity):
             toolbar_box = ToolbarBox()
             toolbar = toolbar_box.toolbar
     
    -        activity_button = ActivityToolbarButton(self)
    +        activity_button = ExtendedActivityToolbarButton(self)
             toolbar_box.toolbar.insert(activity_button, 0)
             activity_button.show()
    ```

7. Before we can move on to packaging, we need to make sure the `activity/activity.info` file has all the required fields.

    ```diff
    diff --git a/activity/activity.info b/activity/activity.info
    index b05bdd8..3d6c3dc 100644
    --- a/activity/activity.info
    +++ b/activity/activity.info
    @@ -1,12 +1,18 @@
     [Activity]
     name = Implode
     activity_version = 20
    -bundle_id = com.jotaro.ImplodeActivity
    +release_date = 2019-10-15
    +bundle_id = org.sugarlabs.ImplodeActivity
     icon = activity-implode
     exec = sugar-activity3 implodeactivity.ImplodeActivity
     license = GPLv2+
    +metadata_license = CC0-1.0
     show_launcher = yes
    -repository = https://github.com/quozl/implode-activity.git
    -summary = Implode blocks of the same colour until they are all gone.
    +repository = https://github.com/sugarlabs/implode-activity.git
    +summary = Implode blocks of the same colour until they are all gone
    +description = Implode is a logic game based on the "falling block" model of Tetris. The game starts with a grid partially filled with blocks. The player makes a move by removing adjacent blocks of the same color in groups of three or more.
     url = https://help.sugarlabs.org/en/implode.html
     tags = Game
    +update_contact = tch@sugarlabs.org
    +developer_name = Sugar Labs Community
    +screenshots = https://help.sugarlabs.org/en/_images/implode-image1.png
    ```

    Most of the missing information can be found in places like [ASLO](http://activities.sugarlabs.org/), [help pages](https://help.sugarlabs.org) and the git repository it-self. Note that I renamed the `bundle_id` to `org.sugarlabs.ImplodeActivty` so we can publish Sugar applications with a consistent and more useful identity.

8. We need to create patches for the changes we made. As an example, one patch for the changes to the activity.info file. It can be called `implode-info.patch`. It's preferred to separate patches for bug fixes and other issues. This will simplify the process of up-streaming bug fixes later.

    ```
    $ git diff activity/activity.info > implode-info.patch 
    ```

## Packaging the applications with Flatpak

1. The application is ready for the desktop. Now we need to write a Flatpak manifest to build and package the application. A manifest is a JSON file with all the information needed to build the application. All the heavy lifting work is already done for this application, so let's re-use it.

    ```
    $ git clone https://github.com/flathub/org.sugarlabs.ImplodeActivity.git
    $ cd org.sugarlabs.ImplodeActivity
    $ git submodule update
    $ rm -rf .git # Let's remove this to continue with the guide
    $ vim org.sugarlabs.ImplodeActivity.json
    ```

2. There's a lot of things in the manifest, so let's omit most of it and show here only what's specific for the application we want to build. 

    ```json
    {
        "app-id": "org.sugarlabs.ImplodeActivity",
        "finish-args": [
            "--env=SUGAR_BUNDLE_ID=org.sugarlabs.ImplodeActivity",
            "--env=SUGAR_BUNDLE_PATH=/app/share/sugar/activities/Implode.activity/"
        ],
        "modules": [
            {
                "name": "implode",
                "buildsystem": "simple",
                "build-commands": [
                    "python3 setup.py install --prefix=${FLATPAK_DEST} --skip-install-desktop-file --skip-install-mime"
                ],
                "sources": [
                    {
                        "type": "git",
                        "url": "https://github.com/sugarlabs/implode-activity",
                        "tag": "v20",
                        "commit": "3073f6bf235dc83c2227ad34c2b46cad0a192c8a"
                    },
                    {
                        "type": "patch",
                        "path": "implode-port.patch"
                    },
                    {
                        "type": "patch",
                        "path": "implode-monitors.patch"
                    },
                    {
                        "type": "patch",
                        "path": "implode-info.patch"
                    }
                ],
                "post-install": [
                    "sugarapp-gen-mimetypes activity/activity.info mimetypes",
                    "sugarapp-gen-appdata activity/activity.info appdata",
                    "sugarapp-gen-desktop activity/activity.info desktop --mimetypes mimetypes",
                    "install -D mimetypes /app/share/mime/packages/org.sugarlabs.ImplodeActivity.xml",
                    "install -D mimetypes /app/share/sugar/activities/Implode.activity/activity/mimetypes.xml",
                    "install -D appdata /app/share/metainfo/org.sugarlabs.ImplodeActivity.appdata.xml",
                    "install -D desktop /app/share/applications/org.sugarlabs.ImplodeActivity.desktop",
                    "install -D activity/activity-implode.svg /app/share/icons/hicolor/scalable/apps/org.sugarlabs.ImplodeActivity.svg"
                ]
            }
        ]
    }
    ```

    * `app-id` is what makes the application unique and it's a critical piece of information needed by the desktop.
    * `finish-args` is where we define `SUGAR_BUNDLE_ID` and `SUGAR_BUNDLE_PATH`variables because it's needed by the Sugarapp to run.
    * `modules` is a list of dependencies that we need to build our application. including the application it-self. Note that many dependencies are already provided by the `runtime` and `sdk` defined in the full manifest.
    * `sources` is the list of git repositories, files and patches needed to build the application. Here is where we apply the patches we have created before.
    * `post-install` is where we generate all the metadata needed by the desktop.

    To learn more about the manifest just take a look at the Flatpak [documentation](http://docs.flatpak.org/en/latest/manifests.html).

3. Let's build and run the application now.

    ```
    $ flatpak-builder --force-clean --repo=repo build org.sugarlabs.ImplodeActivity.json
    $ flatpak build-bundle repo implode.flatpak org.sugarlabs.ImplodeActivity
    $ flatpak install implode.flatpak # This is the whole application in one single file
    $ flatpak run org.sugarlabs.ImplodeActivity
    ```

4. Once it's installed, we need to double check that the metadata was generated correctly.

    ```
    $ flatpak install flathub org.freedesktop.appstream-glib # Install the tools
    $ desktop-file-validate /var/lib/flatpak/app/org.sugarlabs.ImplodeActivity/current/active/files/share/applications/org.sugarlabs.ImplodeActivity.desktop
    $ appstream-util validate /var/lib/flatpak/app/org.sugarlabs.ImplodeActivity/current/active/files/share/appdata/org.sugarlabs.ImplodeActivity.appdata.xml
    ```

    If appstream-util validate is not running, you can also try `flatpak run org.freedesktop.appstream-glib validate` as documented in https://github.com/flathub/flathub/wiki/AppData-Guidelines#use-flathubs-appstream-util

    If the validate command is having trouble reading the appdata XML file, you can try using `cat` to read the xml file, pipe the result into a local directory, and change the path that you pass into the validate function.

    If both commands finish without errors, it means we are ready!

5. Create a new repository in Github, as an example, `https://github.com/<YOUR_USER>/org.sugarlabs.ImplodeActivity`, and then commit and push changes there.

```
$ git init
$ git remote add origin https://github.com/<YOUR_USER>/org.sugarlabs.ImplodeActivity.git
# git submodule add https://github.com/flathub/shared-modules.git
$ git add org.sugarlabs.ImplodeActivity.json # and all the other files referrenced in your manifest
$ git commit -m "Add org.sugarlabs.ImplodeActivity"
$ git push origin master
```

And that's it for now!
