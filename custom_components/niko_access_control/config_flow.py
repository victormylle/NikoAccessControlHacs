from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
import voluptuous as vol

DOMAIN = "niko_access_control"

class MyCloudPlatformConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            # Validate input by trying to login or do other checks
            # ...

            return self.async_create_entry(
                title=email,
                data={
                    CONF_EMAIL: email,
                    CONF_PASSWORD: password
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str
            }),
            errors=errors
        )
