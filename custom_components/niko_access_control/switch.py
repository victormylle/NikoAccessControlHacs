from homeassistant.components.switch import SwitchEntity
from .lock_methods import get_locks, lock_action, get_session_id  # import these methods from your existing code

async def async_setup_entry(hass, config_entry, async_add_entities):
    email = config_entry.data["email"]
    password = config_entry.data["password"]

    session_id = get_session_id(email, password)
    locks = get_locks(session_id)

    async_add_entities([GuardingVisionSwitch(session_id, lock) for lock in locks], True)

class GuardingVisionSwitch(SwitchEntity):
    def __init__(self, session_id, lock):
        self._session_id = session_id
        self._lock = lock

    @property
    def name(self):
        return f"Niko_AC_{self._lock[1]}"

    @property
    def unique_id(self):
        return f"niko_ac_{self._lock[0]}"

    @property
    def is_on(self):
        return None  # No state available

    @property
    def assumed_state(self):
        return True  # Indicate that the state is assumed, not definite

    def turn_on(self, **kwargs):
        lock_action(self._session_id, self._lock[0])

    def turn_off(self, **kwargs):
        lock_action(self._session_id, self._lock[0])
