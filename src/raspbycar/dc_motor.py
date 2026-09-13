"""Gestione del motore DC principale: avanti / indietro / stop."""

from time import monotonic, sleep

from gpiozero import Motor

from . import config


class DCMotor:
    """Motore di trazione, pilotato tramite driver H-bridge (es. L298N)."""

    def __init__(
        self,
        forward_pin: int = config.DC_MOTOR_FORWARD_PIN,
        backward_pin: int = config.DC_MOTOR_BACKWARD_PIN,
        enable_pin: int = config.DC_MOTOR_ENABLE_PIN,
    ) -> None:
        try:
            self._motor = Motor(forward=forward_pin, backward=backward_pin, enable=enable_pin)
        except Exception as exc:
            raise RuntimeError(
                "Impossibile inizializzare il motore DC sui pin "
                f"FWD={forward_pin}, BWD={backward_pin}, EN={enable_pin}. "
                "Possibili cause: servizio raspbycar gia' attivo in background, "
                "altro processo che usa i GPIO, oppure 1-Wire (w1-gpio) su GPIO4."
            ) from exc
        self.current_speed = 0.0
        self.command_voltage = 0.0
        self._last_direction = "stop"
        self._last_speed = 0.0
        self._last_apply_ts = 0.0

    def _set_speed(self, direction: str, speed: float) -> None:
        """Aggiorna velocità e tensione equivalente applicata al motore."""
        now = monotonic()
        self.current_speed = max(0.0, min(1.0, speed))
        self.command_voltage = self.current_speed * 7.0

        # Se il comando attivo resta uguale per molto tempo, invia un breve
        # impulso di reset (stop) per sbloccare rari stati di latch del driver.
        same_direction = direction == self._last_direction
        same_speed = abs(self.current_speed - self._last_speed) <= config.DC_MOTOR_REARM_EPSILON
        should_rearm = (
            direction in ("forward", "backward")
            and self.current_speed > 0.0
            and same_direction
            and same_speed
            and (now - self._last_apply_ts) >= config.DC_MOTOR_REARM_INTERVAL
        )

        if should_rearm:
            self._motor.stop()
            sleep(config.DC_MOTOR_REARM_PULSE)

        if direction == "forward":
            self._motor.forward(self.current_speed)
        elif direction == "backward":
            self._motor.backward(self.current_speed)
        else:
            self._motor.stop()
            self.current_speed = 0.0
            self.command_voltage = 0.0

        self._last_direction = direction
        self._last_speed = self.current_speed
        self._last_apply_ts = monotonic()

    def forward(self, speed: float = config.DC_MOTOR_DEFAULT_SPEED) -> None:
        self._set_speed("forward", speed)

    def backward(self, speed: float = config.DC_MOTOR_DEFAULT_SPEED) -> None:
        self._set_speed("backward", speed)

    def stop(self) -> None:
        self.current_speed = 0.0
        self.command_voltage = 0.0
        self._motor.stop()
        self._last_direction = "stop"
        self._last_speed = 0.0
        self._last_apply_ts = monotonic()

    def close(self) -> None:
        self._motor.close()
