"""Classe Car: combina controller, motore e sterzo in un unico ciclo di guida."""

import time

from . import config
from .bluetooth_controller import BluetoothController, ControllerState
from .dc_motor import DCMotor
from .steering_motor import SteeringMotor


class Car:
    def __init__(self) -> None:
        self._controller = BluetoothController()
        self._motor = DCMotor()
        self._steering = SteeringMotor()

    def _format_debug_report(self, state: ControllerState) -> str:
        """Crea un log leggibile da CLI con i valori attuali del controller e dell'impianto."""
        return (
            "[DEBUG] L2={:3d} R2={:3d} axis_x={:3d} "
            "dir={:7s} speed={:.2f} motor={:.2f}V "
            "steer_angle={:.0f}° servo={:.0f}°"
        ).format(
            state.backward_trigger,
            state.forward_trigger,
            state.steer_axis,
            state.direction,
            state.speed,
            self._motor.command_voltage,
            state.steer,
            self._steering.current_angle,
        )

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

        print(self._format_debug_report(state))

    def _wait_ready(self) -> None:
        """Attende che il joypad sia connesso."""
        while True:
            if self._controller.is_connected or self._controller.connect():
                print("Joypad connesso: guida abilitata.")
                return

            print(
                f"Joypad non trovato, nuovo tentativo tra "
                f"{config.BT_RECONNECT_INTERVAL:.0f}s..."
            )
            time.sleep(config.BT_RECONNECT_INTERVAL)

    def run(self) -> None:
        """Attende il joypad connesso, poi pilota motore e sterzo."""
        while True:
            self._wait_ready()

            try:
                for state in self._controller.events():
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