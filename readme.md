# TuxBook
## Linux Ereader

# Overview
TuxBook is a RaspberryPI based ereader that is designed to hand control back to you, the user. The basic OS runs as a GuiZero app, that is projected onto the eink screen. Touch input is processed using a AR1100 resistive touchscreen controller which controls the OS via a python driver. The ereader OS was degigned in a way to make app development easy, requiring minimal boilerplate and easy app structure, only needing an info.json file and an actuall app file.

## Writing apps
* Apps are folders, Each app must have
    * Info.json
    * main.py
* In info.json, make sure to specify: name (app name to display in GUI) and entrypoint (the home screen for the app, name of python file no extention)

*