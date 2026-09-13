"""Classe Car: combina controller, motore e sterzo in un unico ciclo di guida."""

import time

from . import config
from .bluetooth_controller import BluetoothController, ControllerState
from .dc_motor import DCMotor
from .power_monitor import PowerMonitor
from .steering_motor import SteeringMotor


class Car:
    def __init__(self) -> None:
        self._controller = BluetoothController()
        self._power = PowerMonitor()
        self._motor = DCMotor()
        self._steering = SteeringMotor()
        self._steer_mode = "center"
        self._last_power_warning_ts = 0.0

    def _format_debug_report(self, state: ControllerState) -> str:
        """Crea un log leggibile da CLI con i valori attuali del controller e dell'impianto."""
        return (
            "[DEBUG] L2={:3d} R2={:3d} axis_x={:3d} "
            "dir={:7s} speed={:.2f} motor={:.2f}V "
            "steer_angle={:.0f}° servo={:.0f}° "
            "mode={:6s} invert={} pwr={}"
        ).format(
            state.backward_trigger,
            state.forward_trigger,
            state.steer_axis,
            state.direction,
            state.speed,
            self._motor.command_voltage,
            state.steer,
            self._steering.current_angle,
            self._steer_mode,
            config.STEERING_INVERT_DIRECTION,
            "ON" if self._power.is_powered else "OFF",
        )

    def _apply_state(self, state: ControllerState) -> None:
        if not self._power.is_powered:
            self._motor.stop()
            now = time.monotonic()
            if (now - self._last_power_warning_ts) >= config.POWER_MONITOR_LOG_INTERVAL:
                print("[WARN] L298N non alimentato (PWR=OFF): comando trazione ignorato.")
                self._last_power_warning_ts = now
        elif state.direction == "forward":
            self._motor.forward(state.speed)
        elif state.direction == "backward":
            self._motor.backward(state.speed)
        else:
            self._motor.stop()

        axis = state.steer_axis
        if self._steer_mode == "left":
            if axis >= config.BT_STEER_LEFT_EXIT_RAW:
                self._steer_mode = "center"
        elif self._steer_mode == "right":
            if axis <= config.BT_STEER_RIGHT_EXIT_RAW:
                self._steer_mode = "center"
        else:
            if axis <= config.BT_STEER_LEFT_ENTER_RAW:
                self._steer_mode = "left"
            elif axis >= config.BT_STEER_RIGHT_ENTER_RAW:
                self._steer_mode = "right"

        if self._steer_mode == "left":
            if config.STEERING_INVERT_DIRECTION:
                self._steering.right()
            else:
                self._steering.left()
        elif self._steer_mode == "right":
            if config.STEERING_INVERT_DIRECTION:
                self._steering.left()
            else:
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
        self._power.close()
        self._controller.close()