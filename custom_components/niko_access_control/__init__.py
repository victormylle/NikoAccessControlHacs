DOMAIN = "niko_access_control"

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, entry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )
    return True
