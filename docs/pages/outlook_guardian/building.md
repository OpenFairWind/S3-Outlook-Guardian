---
layout: default
title: "Step 2: Install the software and flash the firmware"
parent: Outlook Guardian
nav_order: 20
---

# Step 2: Install the software and flash the firmware

You need a computer running Windows, macOS or Linux, and about 3 GB of free disk space. The first build downloads the compiler and the libraries, so it needs an internet connection.

## 2.1 Install the tools

1. Install [Git](https://git-scm.com/downloads).
2. Install [Visual Studio Code](https://code.visualstudio.com/).
3. Start Visual Studio Code, open the *Extensions* view, search for **PlatformIO IDE** and install it. Wait until it has finished installing and restart Visual Studio Code when asked.

## 2.2 Get the source code

Open a terminal and run:

```bash
git clone --recursive https://github.com/OpenFairWind/S3-Outlook-Guardian.git
```

The `--recursive` option matters: the speech engine is a git submodule. If you cloned without it, run this inside the project folder:

```bash
git submodule update --init
```

## 2.3 Open the project

1. In Visual Studio Code, choose *File → Open Folder* and select the `S3-Outlook-Guardian` folder.
2. Wait for PlatformIO to finish setting up the project. Its progress is shown in the status bar at the bottom.

## 2.4 Select the environment

1. Click the environment name in the PlatformIO status bar at the bottom of the window (it shows `Default` or `env:...`).
2. Choose **env:pioarduino_esp32s3**.

## 2.5 Build

Click the *Build* button (the check mark) in the status bar. Or, in a terminal:

```bash
pio run -e pioarduino_esp32s3
```

The first build takes several minutes. It is finished when you see `SUCCESS`.

The PicoTTS sources produce many compiler warnings. They are harmless.

## 2.6 Connect the board

1. The board has two USB connectors. Plug the cable into the one marked **UART** (on some boards **COM**).
2. The board powers up from USB. Nothing is heard or seen yet, as it has no firmware.

## 2.7 Flash

Click the *Upload* button (the arrow) in the status bar. Or, in a terminal:

```bash
pio run -e pioarduino_esp32s3 -t upload
```

The firmware is about 8.3 MB, so the upload takes a bit over a minute. It is finished when you see `SUCCESS`, after which the board restarts by itself.

If the upload cannot find or connect to the board, hold the **BOOT** button, press and release **RESET**, release **BOOT**, and upload again.

## 2.8 Check that it started

Within about ten seconds of the restart, the speaker says **"Signal K Outlook Guardian active"**.

To see what the device is doing, open the serial monitor with the *Serial Monitor* button (the plug) in the status bar, or:

```bash
pio device monitor -e pioarduino_esp32s3
```

On the very first start the device formats its configuration storage. For a few seconds the log fills with `task_wdt: esp_task_wdt_reset` messages. They stop when the format is done and do not come back on later starts.

If you hear nothing, check the amplifier wiring from step 1 and look in the log for a line containing `Failed to start`.

## Later firmware updates

To update the firmware, repeat 2.5 to 2.7 with the board connected over USB. Over-the-air updates are **not available**: with all six languages the firmware does not fit twice in 16 MB of flash. [Development notes](development) explains how to get them back by building fewer languages.

## Building the test programs

SensESP is a library with no `setup()` or `loop()` of its own, so the environment also compiles one application from the `examples` directory, chosen by `custom_example` in `platformio.ini`:

```ini
[env:pioarduino_esp32s3]
custom_example = outlook_guardian
```

For troubleshooting the hardware, you can set it to `max98357a_tone` (plays a chime, to test the amplifier), `picotts_shallow_water` (speaks a sentence every 15 seconds, without WiFi) or `picotts_app`.

Next: [Step 3: Connect to WiFi and Signal K](first_start).
