---
layout: default
title: "Step 3: Connect to WiFi and Signal K"
parent: Outlook Guardian
nav_order: 30
---

# Step 3: Connect to WiFi and Signal K

A freshly flashed device knows nothing about your network, so it creates its own WiFi network for the setup.

## 3.1 Join the device's WiFi network

1. On a phone or computer, open the WiFi settings.
2. Connect to the network named **`outlook-guardian`**.
3. Enter the password **`thisisfine`**.

Your phone or computer may warn that this network has no internet access. That is expected; stay connected.

## 3.2 Open the web interface

A setup page may open by itself after connecting. If it does not, open a browser and go to:

```
http://192.168.4.1/
```

## 3.3 Enter the boat's WiFi settings

1. Open the **WiFi** page from the menu.
2. In the *client* settings, enter the name (SSID) and the password of the boat's WiFi network. It must be the network the Signal K server is on.
3. Save. Restart the device if the page asks for it, with the *Restart* button on the **System** page or by pressing RESET on the board.

The device now joins the boat's network.

## 3.4 Reconnect through the boat's network

1. Connect your phone or computer back to the boat's WiFi network.
2. Open:

```
http://outlook-guardian.local/
```

If that address does not open, your network does not resolve `.local` names. Look up the device's IP address in your router's list of connected devices and use that instead.

The **Status** page shows whether the device is connected to WiFi and to the Signal K server.

## 3.5 Change the access point password

The setup network uses a password that is the same on every SensESP device and is printed in this guide. On the **WiFi** page, either change the access point password or switch the access point off.

## 3.6 Let the device into the Signal K server

The device finds the Signal K server on the network by itself and asks it for access.

1. Open the Signal K server's admin interface in a browser.
2. Go to *Security → Access Requests*. A request from `outlook-guardian` is waiting.
3. Open the request and set:
   - *Permissions*: **Read/Write**. Read-only is enough to speak the alarms, but the acknowledge and snooze buttons would not reach the server.
   - *Authentication timeout*: **NEVER**.
4. Click *Approve*.

Within a few seconds the device's **Status** page shows the Signal K connection as connected.

If no request appears, the device did not find the server. Open the device's **Signal K** page, enter the server's address and port (usually 3000) by hand, save and restart.

## Without WiFi or without a Signal K server

You can skip this whole step. The device then works from the NMEA 2000 bus alone and keeps its setup network open.

Next: [Step 4: Configure and test](usage).
