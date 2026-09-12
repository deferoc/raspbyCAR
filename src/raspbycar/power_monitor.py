"""Rilevamento dell'alimentazione del driver motore L298N.

Il Raspberry Pi è alimentato a parte (USB-C, sempre acceso). Solo il L298N
riceve i 7V della batteria tramite un pulsante fisico esterno. Il Pi legge
questo stato tramite un GPIO collegato alla stessa linea tramite un
partitore di tensione o un optoisolatore (mai i 7V direttamente su un
GPIO: si rischia di danneggiare il Pi, il cui massimo è 3.3V).
"""

from gpiozero import DigitalInputDevice


from . import config


class PowerMonitor:
    """Sente se il L298N è alimentato (batteria collegata / pulsante premuto)."""

    def __init__(self, pin: int = config.L298N_POWER_SENSE_PIN) -> None:
        self._sense = DigitalInputDevice(pin, bounce_time=0.1)

    @property
    def is_powered(self) -> bool:
        return self._sense.is_active

    def wait_until_powered(self) -> None:
        """Blocca finché il L298N non risulta alimentato."""
        self._sense.wait_for_active()

    def on_power_lost(self, callback) -> None:
        """Registra un callback invocato non appena l'alimentazione viene a mancare."""
        self._sense.when_deactivated = callback

    def close(self) -> None:
        self._sense.close()
