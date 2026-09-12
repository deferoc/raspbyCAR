"""Classe Car: combina controller, motore e sterzo in un unico ciclo di guida."""

import time

from . import config
from .bluetooth_controller import BluetoothController, ControllerState
from .dc_motor import DCMotor
from .power_monitor import PowerMonitor
from .steering_motor import SteeringMotor


class Car:
    def __init__(self) -> None:
        self._power = PowerMonitor()
        self._controller = BluetoothController()
        self._motor = DCMotor()
        self._steering = SteeringMotor()
        # registrato per ultimo: self.stop() usa _motor/_steering, già creati a questo punto
        self._power.on_power_lost(self.stop)

    def _apply_state(self, state: ControllerState) -> None:
        if state.direction == "forward":
            self._motor.forward(state.speed)
        elif state.direction == "backward":
            self._motor.backward(state.speed)
        else:
            self._motor.stop()

        if state.steer == config.STEERING_LEFT_ANGLE:
            self._steering.left()
        elif state.steer == config.STEERING_RIGHT_ANGLE:
            self._steering.right()
        else:
            self._steering.center()

    def _wait_ready(self) -> None:
        """Attende che il L298N sia alimentato e il joypad connesso."""
        while True:
            print("In attesa che il L298N sia alimentato...")
            self._power.wait_until_powered()

            if self._controller.is_connected or self._controller.connect():
                print("L298N alimentato e joypad connesso: guida abilitata.")
                return

            print(f"Joypad non trovato, nuovo tentativo tra {config.BT_RECONNECT_INTERVAL:.0f}s...")
            time.sleep(config.BT_RECONNECT_INTERVAL)

    def run(self) -> None:
        """Attende L298N alimentato e joypad connesso, poi pilota motore/sterzo."""
        while True:
            self._wait_ready()
            try:
                for state in self._controller.events():
                    if not self._power.is_powered:
                        break
                    self._apply_state(state)
            except OSError:
                print("Joypad disconnesso: in attesa di riconnessione...")
                self._controller.disconnect()
                self.stop()

    def stop(self) -> None:
        self._motor.stop()
        self._steering.center()

    def close(self) -> None:
        self.stop()
        self._motor.close()
        self._steering.close()
        self._controller.close()
        self._power.close()


