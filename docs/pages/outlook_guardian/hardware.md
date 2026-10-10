---
layout: default
title: "Step 1: Assemble the hardware"
parent: Outlook Guardian
nav_order: 10
---

# Step 1: Assemble the hardware

Do all the wiring with the board **unpowered**: USB cable unplugged and no 12 V connected.

## 1.1 Collect the parts

| Part | Notes |
|------|-------|
| ESP32-S3-DevKitC-1 **N16R8** | 16 MB flash and 8 MB PSRAM are both required: the firmware is about 8.3 MB and the speech engine needs about 1.1 MB of PSRAM. Other variants of the board will not work. |
| MAX98357A I2S amplifier breakout | Mono, 3 W class D. |
| Speaker | 4 or 8 Ω, 3 W or more. |
| CAN transceiver breakout | A 3.3 V type such as SN65HVD230. Only needed if you want the NMEA 2000 fallback. |
| 2 momentary push buttons | Normally open. |
| USB cable | A data cable that fits the board, for flashing. |
| Breadboard and jumper wires | Or solder the connections for a permanent installation. |
| 12 V to 5 V DC-DC converter | For powering the device on board, once everything works. |

## 1.2 Wire the amplifier

| Amplifier pin | Connect to |
|---------------|-----------|
| VIN | 5 V pin of the board |
| GND | GND |
| LRC | GPIO 4 |
| BCLK | GPIO 5 |
| DIN | GPIO 6 |
| SD, GAIN | Leave unconnected |

Then connect the speaker to the amplifier's **+** and **−** terminals.

## 1.3 Wire the two buttons

Wire each button between its GPIO and GND. No resistor is needed; the board's internal pull-ups are used.

| Button | Connect between |
|--------|----------------|
| Acknowledge | GPIO 15 and GND |
| Snooze | GPIO 16 and GND |

## 1.4 Wire the CAN transceiver

Skip this step if you will only use Signal K over WiFi.

| Transceiver pin | Connect to |
|-----------------|-----------|
| 3V3 | 3.3 V pin of the board |
| GND | GND |
| CTX (also marked D or TX) | GPIO 17 |
| CRX (also marked R or RX) | GPIO 18 |
| CANH | NMEA 2000 CAN-H (white wire) |
| CANL | NMEA 2000 CAN-L (blue wire) |

1. If the breakout has a 120 Ω termination resistor, remove it. An NMEA 2000 backbone is already terminated at both ends.
2. Connect to the bus with a drop cable on a T-piece. You can leave the bus unconnected until the device works on the bench.

The device only listens on the bus. It does not claim an address and sends nothing.

## 1.5 Check the wiring

Before applying power, check that:

- nothing connects 5 V or 3.3 V directly to GND,
- the amplifier is on the **5 V** pin and the CAN transceiver on the **3.3 V** pin,
- every module shares GND with the board.

## Pin summary

The pins are set as build flags in the `[esp32s3]` section of `platformio.ini`. If your wiring differs, change them there before building in step 2.

| Function | Build flag | GPIO |
|----------|-----------|------|
| Amplifier LRC (word select) | `MAX98357A_LRC_PIN` | 4 |
| Amplifier BCLK | `MAX98357A_BCLK_PIN` | 5 |
| Amplifier DIN | `MAX98357A_DIN_PIN` | 6 |
| CAN transceiver TX | `N2K_CAN_TX_PIN` | 17 |
| CAN transceiver RX | `N2K_CAN_RX_PIN` | 18 |
| Acknowledge button | `ACK_BUTTON_PIN` | 15 |
| Snooze button | `SNOOZE_BUTTON_PIN` | 16 |
| On-board RGB LED | `PIN_RGB_LED` | 48 |
| On-board BOOT button | `BUTTON_BUILTIN` | 0 |

The on-board RGB LED is on GPIO 48 on DevKitC-1 v1.0 boards and on GPIO 38 on v1.1 boards (the version is printed on the board). On a v1.1 board, change `PIN_RGB_LED` to 38.

Next: [Step 2: Install the software and flash the firmware](building).
