"""Gestione dello sterzo tramite servo ad angolo: destra / centro / sinistra."""

from time import sleep

from gpiozero import AngularServo

from . import config


class SteeringMotor:
    """Sterzo motorizzato tramite servo, con posizioni discrete sinistra/centro/destra."""

    def __init__(
        self,
        pin: int = config.STEERING_SERVO_PIN,
        min_angle: float = config.STEERING_MIN_ANGLE,
        max_angle: float = config.STEERING_MAX_ANGLE,
        min_pulse_width: float = config.STEERING_MIN_PULSE_WIDTH,
        max_pulse_width: float = config.STEERING_MAX_PULSE_WIDTH,
    ) -> None:
        self._servo = AngularServo(
            pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
        )
        self._last_angle = None
        self.current_angle = config.STEERING_CENTER_ANGLE
        self.center()

    def set_angle(self, angle: float) -> None:
        """Muove il servo all'angolo indicato, poi lo rilascia per ridurre jitter."""
        if angle == self._last_angle:
            return
        self._servo.angle = angle
        sleep(config.STEERING_SETTLE_TIME)
        self._servo.detach()
        self._last_angle = angle
        self.current_angle = angle

    def left(self) -> None:
        self.set_angle(config.STEERING_LEFT_ANGLE)

    def right(self) -> None:
        self.set_angle(config.STEERING_RIGHT_ANGLE)

    def center(self) -> None:
        self.set_angle(config.STEERING_CENTER_ANGLE)

    def close(self) -> None:
        self._servo.detach()
        self._servo.close()

