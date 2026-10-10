---
layout: default
title: Outlook Guardian
nav_order: 15
has_children: true
---

# Signal K Outlook Guardian

The Outlook Guardian is a talking alarm annunciator for boats.
It is an ESP32-S3 device that listens for vessel alarms and reads them out loud, so that the crew hears *what* is wrong and not just a buzzer.

It is built with SensESP and lives in this repository as the application [`examples/outlook_guardian.cpp`](https://github.com/OpenFairWind/S3-Outlook-Guardian/blob/main/examples/outlook_guardian.cpp).

## What it does

- **Speaks Signal K notifications.** It subscribes to `notifications.*` on the Signal K server and speaks the `message` of every raised notification.
- **Falls back to NMEA 2000.** When the Signal K server is not connected, it listens to the NMEA 2000 alert messages directly on the bus, composes a sentence from each alert and speaks it.
- **Shows the alarm on the RGB LED.** The color follows the most severe alarm, and the LED blinks until somebody reacts.
- **Has two push buttons**, one to acknowledge and one to snooze. For Signal K notifications the button press is sent to the server, so the other displays on board follow.
- **Speaks six languages.** The language, voice, speed and volume are chosen in the web interface.
- At startup it says "Signal K Outlook Guardian active".

Speech is synthesized on the device with the [PicoTTS](https://github.com/DiUS/esp-picotts) engine and played through a MAX98357A I2S amplifier. No internet connection or cloud service is involved.

## Step-by-step guide

The guide starts from a bare board and ends with the device speaking a test alarm. Follow the steps in order.

| Step | Page | What you do |
|------|------|-------------|
| 1 | [Assemble the hardware](hardware) | Collect the parts and wire them to the board |
| 2 | [Install the software and flash the firmware](building) | Install the tools, get the source, build it and load it onto the board |
| 3 | [Connect to WiFi and Signal K](first_start) | Join the device to the boat's network and let it into the Signal K server |
| 4 | [Configure and test](usage) | Choose the language and voice, raise a test alarm, learn the LED and the buttons |

Reference pages, for when you need the details:

| Page | Contents |
|------|----------|
| [Alarm sources](alarm_sources) | Exactly how Signal K notifications and NMEA 2000 alerts are handled |
| [Development notes](development) | Code structure, languages, flash layout |
