# **This integration is now no longer necessary with deako being part of HA core.**

# Deako Alpha HA integration

Component to integrate with Deako using the public local api

**This component will set up the following platforms.**

Platform | Description
-- | --
`Lights` | Control your lights

## Installation using [HACS](https://hacs.xyz/)

1. Go to HACS/Integration in Home Assistant
2. In the upper right, click the three dots
3. Click "custom repositories"
4. Under "Repository", enter the url for Deako Alpha HA integration: [https://github.com/DeakoLights/homeassistant_alpha]()
5. Under "Category", select "Integration"
6. "Add"
7. Install Deako Alpha HA integration
8. Restart Home Assistant
9. Go to Configuration/Integrations
10. Deako should now be in the list of searchable integrations and auto discovered

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it. It's highly recommended using the custom components manager [HACS](https://hacs.xyz/).
3. In the `custom_components` directory (folder) create a new folder called `deako`.
4. Download _all_ the files from the `custom_components/deako/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. Deako should now be in the list of searchable integrations

## Configuration

Configuration is done automatically during integration setup.
