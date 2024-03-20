# Welcome
I created a basic Python Code base to interact with any CLI based board through a GUI.I created this specifically for my ESE 5160 Course at Upenn, I plan to add button for self tests once our final boards are received and many things. I request you to fork this repository and add button or features you think could be useful, Raise a PR when done.

## How the GUI Looks
It is a Basic GUI which has a text window which displays messages from the GUI as `GUI>>` and from connected device as `DEV>>`.

`Search Device and Connect` button: currently searches `EDBG` devices connected to your computer, find the comport and opens a serial communication with the device.
`Reset CLI` button: Clears the textbox

`Disconnect Device` button: Closes serial com

`Get Firmware Version` button: Retrieves Firmware version(**Command should exist in CLI**)

`Get Current Ticks` button: Get current Ticks(**Command should exist in CLI**)

`Reset Device` button: Resets the device(**Command should exist in CLI**)

`Close CLI` button: Closes the GUI window

`Light Indicator`: The Red light at the end shows the status of connection with device, Connected it will be green, otherwise red

## GUI
![GUI](https://github.com/saurabhparulekar24/SerialTerminalApp/blob/main/images/GUI.png)

## How to Run
Just double click gui_manager.py

