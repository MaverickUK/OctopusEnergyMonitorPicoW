# Raspberry Pi Pico W Octopus Energy Monitor
Displays household energy usage on a Raspberry Pi Pico W via the Octopus Energy API

![YouTube demo video](https://img.youtube.com/vi/BpAdRYpYhJs/0.jpg)

[Watch video demo](https://www.youtube.com/watch?v=BpAdRYpYhJs)

This was a quick and dirty project over the Christmas 2022 holiday, so has plenty of scope to be refactored and extended.

## Quick start
1. Flash Pico W using [latest MicroPython firmware](https://micropython.org/download/rp2-pico-w/)
2. Copy all files to Raspberry Pi Pico W
3. Open `secrets.py` and enter your Wifi and Octopus Energy details

You can find out the majority of the required Octopus Energy details by visiting the [Octopus Developer dashboard](https://octopus.energy/dashboard/developer/)

## Warning
Currently the code doesn't automatically create the Base64 encoded basic auth header which is held in the `auth_header` value in the `secrets.py` file. You will need to manually create this from your [API auth key](https://octopus.energy/dashboard/developer/) using a service such as [Base64 Encode](https://www.base64encode.org/)

## Features
- Displays energy usage (electricty & gas)
- Group by day, week, month or quarter (Change mode using buttons)
- Auto refreshes every hour

## To do
- Automatically generate the `auth_header` from the supplied Octopus Energy credentials
- Show week number on weekly view
- Use screen colours to indicate energy savings during a particular period?

Thanks to [guylipman.com](https://www.guylipman.com/octopus/api_guide.html) for the useful information getting started with the Octopus Energy API
