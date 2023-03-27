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
    $ flatpak install flathub org.sugarlabs.BaseApp
    ```

3. Use this BaseApp as a development environment, it already comes with all the basic dependencies we need. Including Sugarapp, which is the main library we use to port the Sugar applications to the desktop.

    ```
    $ flatpak run --command=bash org.sugarlabs.BaseApp # Enter the development environment
    $ exit # Exit the development environment
    ```

## Porting an application with Sugarapp

1. Get the application source code. Let's use HelloWorld application as an example.

    ```
    $ git clone https://github.com/sugarlabs/hello-world.git
    $ cd hello-world
    ```

2. Identify the main activity class.

    ```
    $ cat activity/activity.info | grep exec # To find the main class
    $ vim activity.py # Edit the file with you preferred text editor
    ```

3. Replace the Sugar Activity class by the Sugarapp SugarCompatibleActivity class.

    ```diff
    diff --git a/activity.py b/activity.py
    index f6f1634..e4e6607 100644
    --- a/activity.py
    +++ b/activity.py
    @@ -30,13 +30,15 @@ from sugar3.activity.widgets import StopButton
     from sugar3.activity.widgets import ShareButton
     from sugar3.activity.widgets import DescriptionItem
     
    +from sugarapp.widgets import SugarCompatibleActivity
     
    -class HelloWorldActivity(activity.Activity):
    +
    +class HelloWorldActivity(SugarCompatibleActivity):
         """HelloWorldActivity class as specified in activity.info"""
     
         def __init__(self, handle):
             """Set up the HelloWorld activity."""
    -        activity.Activity.__init__(self, handle)
    +        SugarCompatibleActivity.__init__(self, handle)
     
             # we do not have collaboration features
             # make the share option insensitive
    ```

4. Run the application with Sugarapp.

    ```
    $ cat activity/activity.info | grep bundle_id # In this example, the app-id is org.sugarlabs.HelloWorld
    $ flatpak run --command=bash --filesystem=$PWD --socket=session-bus --socket=x11 org.sugarlabs.BaseApp # To enter the development environment
    $ SUGAR_BUNDLE_ID=org.sugarlabs.HelloWorld SUGAR_BUNDLE_PATH=$PWD sugarapp
    ```

5. Extend toolbars to be able to save and load projects.

    Sugar applications can automatically save and load projects, e.g. a user starts a new project in MusicKeyboard and then simply closes the application. The project will be restored when the user re-opens the application. This is supported by the Sugar API, where every application can provide a `write_file` and `read_file` method.

    Sugarapp mimics this behavior by always providing a valid `file_path` to these methods. Sugarapp can also to extend the application UI by providing widgets to support saving and loading files, just like any other desktop application. As an example:

    ```diff
    diff --git a/activity.py b/activity.py
    index b8d179a..76ad943 100644
    --- a/activity.py
    +++ b/activity.py
    @@ -25,9 +25,9 @@ from gettext import gettext as _
     from sugar3.activity import activity
     from sugar3.graphics.toolbarbox import ToolbarBox
     from sugar3.activity.widgets import StopButton
    -from sugar3.activity.widgets import ActivityToolbarButton
     
     from sugarapp.widgets import SugarCompatibleActivity
    +from sugarapp.widgets import ExtendedActivityToolbarButton
     
     
     class HelloWorldActivity(SugarCompatibleActivity):
    @@ -44,7 +44,7 @@ class HelloWorldActivity(SugarCompatibleActivity):
             # toolbar with the new toolbar redesign
             toolbar_box = ToolbarBox()
     
    -        activity_button = ActivityToolbarButton(self)
    +        activity_button = ExtendedActivityToolbarButton(self)
             toolbar_box.toolbar.insert(activity_button, 0)
             activity_button.show()
    ```

    To see the most common issues take a look at this [list](flatpak-guide-common-issues.md).

6. Before we can move on to packaging, we need to make sure the `activity/activity.info` file has all the required fields.

    ```diff
    diff --git a/activity/activity.info b/activity/activity.info
    index 4c1a510..6da1a7a 100644
    --- a/activity/activity.info
    +++ b/activity/activity.info
    @@ -2,7 +2,16 @@
     name = HelloWorld
     activity_version = 7
     bundle_id = org.sugarlabs.HelloWorld
    +release_date = 2020-03-12
     exec = sugar-activity3 activity.HelloWorldActivity
     icon = activity-helloworld
     license = GPLv2+
    +metadata_license = CC0-1.0
     repository = https://github.com/sugarlabs/hello-world.git
    +summary = A demo Sugar application
    +description = HelloWorld is a demo application used in tutorials for developing new Sugar applications or porting Sugar applications to Flatpak.
    +url = https://github.com/sugarlabs/hello-world.git
    +tags = Education
    +update_contact = tch@sugarlabs.org
    +developer_name = Sugar Labs Community
    +screenshots = https://i.imgur.com/N1uXt6S.png
    ```

    Most of the missing information can be found in places like [ASLO](http://activities.sugarlabs.org/), [help pages](https://help.sugarlabs.org) and the git repository it-self. Note that it is recommended to rename the `bundle_id` to something that starts with `org.sugarlabs.` so we can publish Sugar applications with a consistent and more useful identity.

7. We need to create patches for the changes we made. As an example, one patch for the changes to the activity.info file. It can be called `helloworld-info.patch`. It's preferred to separate patches for bug fixes and other issues. This will simplify the process of up-streaming bug fixes later.

    ```
    $ git diff activity/activity.info > helloworld-info.patch
    $ git diff activity.py > helloworld-port.patch
    ```

## Packaging the applications with Flatpak

1. The application is ready for the desktop. Now we need to write a Flatpak manifest to build and package the application. A manifest is a JSON file with all the information needed to build the application.

    ```json
    {
        "app-id": "org.sugarlabs.HelloWorld",
        "base": "org.sugarlabs.BaseApp",
        "base-version": "22.06",
        "runtime": "org.gnome.Platform",
        "runtime-version": "42",
        "sdk": "org.gnome.Sdk",
        "separate-locales": false,
        "command": "sugarapp",
        "finish-args": [
            "--socket=x11",
            "--socket=pulseaudio",
            "--share=ipc",
            "--device=dri",
            "--env=SUGAR_BUNDLE_ID=org.sugarlabs.HelloWorld",
            "--env=SUGAR_BUNDLE_PATH=/app/share/sugar/activities/HelloWorld.activity"
        ],
        "modules": [
            {
                "name": "hello-world",
                "buildsystem": "simple",
                "build-commands": [
                    "python3 setup.py install --prefix=${FLATPAK_DEST} --skip-install-desktop-file --skip-install-mime"
                ],
                "sources": [
                    {
                        "type": "git",
                        "url": "https://github.com/sugarlabs/hello-world.git",
                        "branch": "master",
                        "commit": "244bcaf802b5a093787a121ddcbefc0bec917a8e"
                    },
                    {
                        "type": "patch",
                        "path": "helloworld-port.patch"
                    },
                    {
                        "type": "patch",
                        "path": "helloworld-info.patch"
                    }
                ],
                "post-install": [
                    "sugarapp-gen-mimetypes activity/activity.info mimetypes",
                    "sugarapp-gen-appdata activity/activity.info appdata",
                    "sugarapp-gen-desktop activity/activity.info desktop --mimetypes mimetypes",
                    "install -D mimetypes /app/share/mime/packages/org.sugarlabs.HelloWorld.xml",
                    "install -D mimetypes /app/share/sugar/activities/HelloWorld.activity/activity/mimetypes.xml",
                    "install -D appdata /app/share/metainfo/org.sugarlabs.HelloWorld.appdata.xml",
                    "install -D desktop /app/share/applications/org.sugarlabs.HelloWorld.desktop",
                    "install -D activity/activity-helloworld.svg /app/share/icons/hicolor/scalable/apps/org.sugarlabs.HelloWorld.svg"
                ]
            }
        ]
    }
    ```

    To learn more about the manifest just take a look at the Flatpak [documentation](http://docs.flatpak.org/en/latest/manifests.html).

2. Let's build and run the application now.

    ```
    $ flatpak install flathub org.gnome.Sdk//42
    $ flatpak-builder --user --force-clean --install build org.sugarlabs.HelloWorld.json
    $ flatpak run org.sugarlabs.HelloWorld//master
    ```

3. Once it's installed, we need to double check that the metadata was generated correctly.

    ```
    $ flatpak install flathub org.freedesktop.appstream-glib # Install the tools
    $ desktop-file-validate /var/lib/flatpak/app/org.sugarlabs.HelloWorld/current/active/files/share/applications/org.sugarlabs.HelloWorld.desktop
    $ appstream-util validate /var/lib/flatpak/app/org.sugarlabs.HelloWorld/current/active/files/share/appdata/org.sugarlabs.HelloWorld.appdata.xml
    ```

    If both commands finish without errors, it means we are ready!

4. Create a new repository in Github, as an example, `https://github.com/<YOUR_USER>/org.sugarlabs.HelloWorld`, and then commit and push changes there.

    ```
    $ git clone https://github.com/<YOUR_USER>/org.sugarlabs.HelloWorld.git
    $ cd org.sugarlabs.HelloWorld
    $ git add org.sugarlabs.HelloWorld.json # and all the other files referrenced in your manifest
    $ git commit -m "Add org.sugarlabs.HelloWorld"
    $ git push origin master
    ```

And that's it for now! You can find the full example [here](https://github.com/tchx84/org.sugarlabs.HelloWorld).
