"""Gestione del motore DC principale: avanti / indietro / stop."""

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
        self._motor = Motor(forward=forward_pin, backward=backward_pin, enable=enable_pin)
        self.current_speed = 0.0
        self.command_voltage = 0.0

    def _set_speed(self, direction: str, speed: float) -> None:
        """Aggiorna velocità e tensione equivalente applicata al motore."""
        self.current_speed = max(0.0, min(1.0, speed))
        self.command_voltage = self.current_speed * 7.0
        if direction == "forward":
            self._motor.forward(self.current_speed)
        elif direction == "backward":
            self._motor.backward(self.current_speed)
        else:
            self._motor.stop()
            self.current_speed = 0.0
            self.command_voltage = 0.0

    def forward(self, speed: float = config.DC_MOTOR_DEFAULT_SPEED) -> None:
        self._set_speed("forward", speed)

    def backward(self, speed: float = config.DC_MOTOR_DEFAULT_SPEED) -> None:
        self._set_speed("backward", speed)

    def stop(self) -> None:
        self.current_speed = 0.0
        self.command_voltage = 0.0
        self._motor.stop()

    def close(self) -> None:
        self._motor.close()
