# TuxBook

## Overview
TuxBook is a RaspberryPI based ereader that is designed to hand control back to you, the user. The basic OS runs as a GuiZero app, that is projected onto the eink screen. Touch input is processed using a AR1100 resistive touchscreen controller which controls the OS via a python driver. The ereader OS was degigned in a way to make app development easy, requiring minimal boilerplate and easy app structure, only needing an info.json file and an actuall app file.

## Hardware
1. Raspberry PI zero 2W
2. Waveshare 6 inch HD e paper screen with IT8951 Driver
3. AR1100 resistive touchscreen driver (I used adafruit but you can use any)
4. Any 4 wire resistive touchscreen that roughly matches the size of the screen
5. SD card (min 16 GB) 

## Setup
1. Clone the repository 
```
git clone https://github.com/michael-206/TuxBook
```
2. Create virtual environment and install dependencies
```bash
python -m venv venv

source ./venv/bin/activate

pip install -r requirements.txt
```
3. Connect hardware
    * Connect the touch digitizer to the AR1100, and connect the AR1100 to the PI with a usb cable
    * Connect the Eink Screen to the PI by connecting the following wires
        * Screen -> PI (BCM)
        * 5V -> 5V
        * GND -> GND
        * MISO -> P9
        * MOSI -> P10
        * SCK -> P11
        * CS -> P8
        * RST -> P17
        * HRDY -> P24
    * Place touch digitizer over screen
4. Go into the touch_bridge.py file and edit the config values to match your screen and touch digitizer.
```python
# Xvfb screen dimensions
SCREEN_WIDTH = 1072
SCREEN_HEIGHT = 1448

# Coordinate orientation
SWAP_XY = True
INVERT_X = True
INVERT_Y = False

# Raw touchscreen calibration limits
RAW_MIN_X = 0
RAW_MAX_X = 4095
RAW_MIN_Y = 0
RAW_MAX_Y = 4095

# Active touch area
ACTIVE_MIN_X = 300
ACTIVE_MAX_X = 3700
ACTIVE_MIN_Y = 300
ACTIVE_MAX_Y = 3700

# Screen-coordinate offsets
OFFSET_X = 0
OFFSET_Y = 30
```
5. Make start.sh executable (use sudo if doesnt work)
```bash
chmod +x ./start.sh
```
6. Run the ./start.sh file 
```bash
./start.sh
```

## Writing apps
* Apps are folders, Each app must have
    * Info.json
        * Tells the OS the name of the app, where to find the icon for the app, and where to find the actual app file
        * Example:
        ```json
        {
            "name": "Hello",
            "version": "1.0",
            "author": "Michael Prokoudine",
            "entrypoint": "main",
            "description": "A Hello World",
            "icon": "happy-face.png"
        }
        ```
    * main.py
        * Import guizro
        * Create a function called build(), and then put your code in that
        * To access some OS functions, such as:
            * Navigate to other apps
            * Navigate to other screens within app
            * Access data supplied with app launch
            
            You need to access them from the supplied keyword arguments (kwargs)
        * The root for the app will be supplied as parent
        * Example
        ```python
        from guizero import Text

        def build(parent, **kwargs):
            load_app = kwargs["load_app"]
            navigate = kwargs["navigate"]
            data = kwargs["data"]

            title = Text(parent, text="Hello World!", size=48)
            message = Text(parent, text="This is the Hello World app.", size=24)
        ```

    