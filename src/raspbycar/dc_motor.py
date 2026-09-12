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

    def forward(self, speed: float = config.DC_MOTOR_DEFAULT_SPEED) -> None:
        self._motor.forward(speed)

    def backward(self, speed: float = config.DC_MOTOR_DEFAULT_SPEED) -> None:
        self._motor.backward(speed)

    def stop(self) -> None:
        self._motor.stop()

    def close(self) -> None:
        self._motor.close()
