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

Changes apply to the next spoken message; no restart is needed.

The language selects the voice. It does not translate: a Signal K notification written in English is read with Italian pronunciation if the language is `it-IT`. Sentences the device composes itself, which are the startup announcement and the NMEA 2000 alerts, are in the chosen language.

## 4.2 Raise a test alarm

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

## 4.3 Try the buttons

1. Press **Snooze**. The speech stops and the LED turns steady red. After the snooze time (5 minutes by default) the alarm is spoken again.
2. Press **Acknowledge**. The speech stops for good and the LED stays steady red.
3. In the Signal K server's *Data Browser*, look at `notifications.test`: its `method` is now an empty list. That is the acknowledgement sent by the device.

## 4.4 Clear the test alarm

Send the same delta again with `"state": "normal"`. The LED goes off.

## 4.5 Install it on board

1. Disconnect the USB cable.
2. Power the board's 5 V pin from the 12 V to 5 V converter.
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

The LED **blinks** while at least one alarm is waiting for a reaction, and is **steady** once all alarms have been acknowledged or snoozed. It goes off when the alarm conditions have cleared.

The LED does not show the WiFi or Signal K connection status. Use the web interface's status page for that.

## Buttons

Both buttons act on all the alarms that are waiting at that moment.

| Button | Effect |
|--------|--------|
| Acknowledge | The alarms are no longer spoken. The LED stays lit, steady, until the conditions clear. |
| Snooze | The alarms keep quiet for the snooze time. If they are still raised afterwards, they are spoken again. |

An alarm that changes, for example from warning to alarm or with a new message, is announced again even if it had been acknowledged.

The BOOT button on the board keeps its SensESP function: a short press restarts the device, a long press resets the network settings and a very long press does a factory reset.

## How alarms are spoken

- The most severe alarm is spoken first.
- An alarm is repeated at the configured interval until it clears or is acknowledged or snoozed.
- Several alarms take turns, one sentence at a time.

For exactly how each kind of notification and alert is treated, see [Alarm sources](alarm_sources).
