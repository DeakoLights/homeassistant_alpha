_Alpha Component to integrate with Deako._

**This component will set up the following platforms.**

Platform | Description
-- | --
`light` | Control a Light.

{% if not installed %}

## Installation

1. Install via HACS

{% endif %}

## Setup

Deako should be discovered automatically with mdns if mdns is setup/working on your HA instance. Once discovered, setup the integration just like any other HA integration. No configuration is required.

This integration will connect to a device that is on WiFi, get the list of devices and their info, then register those devices with HA. If dimmable, will be dimmable.
