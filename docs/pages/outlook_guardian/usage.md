---
layout: default
title: "Step 4: Configure and test"
parent: Outlook Guardian
nav_order: 40
---

# Step 4: Configure and test

## 4.1 Choose the language and voice

1. Open the device's web interface (`http://outlook-guardian.local/`).
2. Open the **Configuration** page and find the **Speech and alarms** card.
3. Set the language, voice and volume, and save.

| Setting | Default | Meaning |
|---------|---------|---------|
| Language | en-US | The language of the voice: `en-US`, `en-GB`, `it-IT`, `de-DE`, `es-ES` or `fr-FR`. |
| Voice | Standard | *Standard*, *Deep* or *High*. PicoTTS has one speaker per language, so these are pitch variations of it. |
| Speech speed | 100 | In percent, from 50 to 200. |
| Volume | 50 | In percent. |
| Repeat an unacknowledged alarm every | 30 | In seconds. 0 speaks each alarm once. |
| Snooze time | 5 | In minutes. |
| Speak a welcome message at startup | On | Untick to start silently. |
| Welcome message | *(empty)* | The sentence spoken at startup. Leave it empty for the standard announcement, "Signal K Outlook Guardian active", in the chosen language. |

Changes apply to the next spoken message; no restart is needed. The welcome message is heard at the next start.

The language selects the voice. It does not translate: a Signal K notification written in English is read with Italian pronunciation if the language is `it-IT`. Sentences the device composes itself, which are the startup announcement and the NMEA 2000 alerts, are in the chosen language.

## 4.2 Choose what is announced

By default the device announces every Signal K notification and every NMEA 2000 alert. To narrow that down, open the **Alarm sources** card on the **Configuration** page, save, and restart the device.

| Setting | Default | Meaning |
|---------|---------|---------|
| Signal K notification paths | `notifications.*` | The paths the device subscribes to, separated by commas. `*` stands for any text. `notifications.` is added to a path that does not start with it. An empty field means all notifications. |
| NMEA 2000: emergency alarms, alarms, warnings, cautions and other alerts | On | The alert types that are announced. |
| NMEA 2000: navigational alerts, technical alerts | On | The alert categories that are announced. |

For example, `notifications.mob, notifications.propulsion.*, notifications.navigation.anchor` takes the man overboard and anchor alarms and everything about the engines, and nothing else. A path without `*` matches that notification only, not the ones below it.

An NMEA 2000 alert is announced if both its type and its category are ticked. Unticking all the types, or both categories, switches the NMEA 2000 fallback off. An alert that is not announced does not light the LED either.

## 4.3 Raise a test alarm

Send the device a notification to check the whole chain.

1. In the Signal K server's admin interface, open *Data Fiddler*. If your server version does not have it, use any other way of sending a delta, for example a Node-RED flow.
2. Send this delta:

   ```json
   {
     "updates": [
       {
         "values": [
           {
             "path": "notifications.test",
             "value": {
               "state": "alarm",
               "method": ["visual", "sound"],
               "message": "This is a test alarm"
             }
           }
         ]
       }
     ]
   }
   ```

3. The device says "This is a test alarm" and the LED blinks red. The sentence is repeated every 30 seconds.

## 4.4 Try the buttons

1. Press **Snooze**. The speech stops and the LED turns steady red. After the snooze time (5 minutes by default) the alarm is spoken again.
2. Press **Acknowledge**. The speech stops for good and the LED stays steady red.
3. In the Signal K server's *Data Browser*, look at `notifications.test`: its `method` is now an empty list. That is the acknowledgement sent by the device.

## 4.5 Clear the test alarm

Send the same delta again with `"state": "normal"`. The LED goes off.

## 4.6 Install it on board

1. Disconnect the USB cable.
2. Power the board's 5 V pin from the 12 V to 5 V converter, as described in [Power the device](hardware#power-the-device).
3. If you wired the CAN transceiver, connect it to the NMEA 2000 bus with a drop cable.

The device is ready. The rest of this page describes how it behaves in daily use.

## RGB LED

The LED shows the most severe alarm currently raised.

| LED | Meaning |
|-----|---------|
| Off | No alarm |
| Blue | Alert (Signal K) or caution (NMEA 2000) |
| Yellow | Warning |
| Red | Alarm |
| Red, blinking fast | Emergency |
| Red, two short flashes every second | The audio output failed to start: the device cannot speak |

The LED **blinks** while at least one alarm is waiting for a reaction, and is **steady** once all alarms have been acknowledged or snoozed. It goes off when the alarm conditions have cleared.

The LED does not show the WiFi or Signal K connection status. Use the web interface's status page for that.

The two red flashes replace the alarm colours for as long as the device runs, and the display shows `NO AUDIO` on its second line. Everything else keeps working: the alarms are received, shown on the display and answered with the buttons, but none is spoken. The fault is detected when the board cannot start its I2S output or the speech engine, which happens for example on a board without PSRAM. A disconnected amplifier or speaker cannot be detected, as the amplifier sends nothing back to the board. Check the serial console for the reason and restart the device.

## Display

If an SSD1306 display is connected, it shows the state of the device and the latest notification received. The display is optional: without it the device speaks, lights the LED and reads the buttons just the same. It may be plugged in while the device is running, and is found within ten seconds.

| Line | Content |
|------|---------|
| 1 | The IP address of the device and the WiFi mode: `AP` while the device is its own access point, `INFRA` once it has joined the boat's network. *No WiFi* if neither. |
| 2 | The alarm streams. `SK:ON` while the Signal K server is connected. `N2K:ON` while messages are arriving from the NMEA 2000 bus (any message in the last five seconds). `--` instead of `ON` otherwise. |
| 3 | The source (`SK` or `N2K`) and severity (`ALERT`, `WARNING`, `ALARM`, `EMERGENCY`) of the latest notification, and its state: `ACTIVE`, `SNOOZED`, `ACK` (acknowledged), `SILENCED` (the source asked for no sound) or `CLEARED`. |
| 4 to 7 | The message of that notification. |

The latest notification is the alarm that was raised or changed most recently. It stays on the display, marked `CLEARED`, after its condition has ended. Until the first one arrives, the display says *No notifications*.

NMEA 2000 alerts are only taken while the Signal K server is not connected, so with both streams `ON` the notifications are the Signal K ones.

The display dims while no alarm is raised. Accented letters that the display font lacks are shown without the accent.

## Buttons

Both buttons act on all the alarms that are waiting at that moment.

| Button | Effect |
|--------|--------|
| Acknowledge | The alarms are no longer spoken. The LED stays lit, steady, until the conditions clear. |
| Snooze | The alarms keep quiet for the snooze time. If they are still raised afterwards, they are spoken again. |

An alarm that changes, for example from warning to alarm or with a new message, is announced again even if it had been acknowledged.

The BOOT button on the board keeps its SensESP function: a short press restarts the device, a long press resets the network settings and a very long press does a factory reset.

## If the device cannot join the WiFi network

When the device has not been able to join the configured network for one minute, for example because of a mistyped password, it opens its own access point again: `outlook-guardian`, password `thisisfine`. The display then shows `AP` and the address `192.168.4.1`. Join the access point and open `http://192.168.4.1/` to correct the WiFi settings.

The device keeps trying to join the configured network in the meantime. The access point stays open until the next restart.

## How alarms are spoken

- The most severe alarm is spoken first.
- An alarm is repeated at the configured interval until it clears or is acknowledged or snoozed.
- Several alarms take turns, one sentence at a time.

For exactly how each kind of notification and alert is treated, see [Alarm sources](alarm_sources).
