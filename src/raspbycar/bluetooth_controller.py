"""Lettura input da gamepad collegato via Bluetooth (protocollo HID / evdev).

Mapping fedele all'hardware usato in precedenza: asse 0 = sterzo, asse 4 =
velocità, trigger L2/R2 = retromarcia/marcia avanti.
"""

from __future__ import annotations

from dataclasses import dataclass

import evdev
from evdev import ecodes

from . import config


@dataclass
class ControllerState:
    """Stato normalizzato del controller in un dato istante."""

    steer: float = config.STEERING_CENTER_ANGLE  # angolo target dello sterzo
    direction: str = "stop"  # 'forward' | 'backward' | 'stop'
    speed: float = config.DC_MOTOR_DEFAULT_SPEED  # 0.0 - 1.0


class BluetoothController:
    """Wrapper su un joypad Bluetooth PlayStation 4 tramite evdev."""

    def __init__(self, name_hint: str = config.BT_CONTROLLER_NAME_HINT) -> None:
        self._name_hint = name_hint
        self._device: evdev.InputDevice | None = None
        self.state = ControllerState()
        self._backward_pressed = False
        self._forward_pressed = False

    @property
    def is_connected(self) -> bool:
        return self._device is not None

def connect(self) -> bool:
    """Cerca il gamepad tra i device disponibili; ritorna True se trovato."""
    for path in evdev.list_devices():
        device = evdev.InputDevice(path)

        name = device.name.lower()

        if self._name_hint.lower() not in name:
            device.close()
            continue

        # Ignora il dispositivo dei sensori di movimento.
        if "motion sensors" in name:
            device.close()
            continue

        self._device = device
        print(f"Joypad trovato: {device.name} ({device.path})")
        return True

    return False

    def disconnect(self) -> None:
        """Dimentica il device corrente dopo una disconnessione rilevata."""
        self._device = None

    def _update_direction(self) -> None:
        if self._backward_pressed and not self._forward_pressed:
            self.state.direction = "backward"
        elif self._forward_pressed and not self._backward_pressed:
            self.state.direction = "forward"
        else:
            self.state.direction = "stop"  # nessun trigger premuto, o entrambi: stato sicuro

    @staticmethod
    def _discrete_steer_angle(value: int) -> float:
        """Discretizza il valore grezzo dell'asse in sinistra/centro/destra."""
        if value <= config.BT_STEER_RIGHT_THRESHOLD:
            return config.STEERING_RIGHT_ANGLE
        if value >= config.BT_STEER_LEFT_THRESHOLD:
            return config.STEERING_LEFT_ANGLE
        return config.STEERING_CENTER_ANGLE

    @staticmethod
    def _map_speed(value: int) -> float:
        """Asse velocità: 0 = veloce, 255 = lento."""
        return max(0.0, min(1.0, (255 - value) / 255))

    def events(self):
        """Genera lo stato aggiornato del controller ad ogni evento ricevuto (bloccante)."""
        for event in self._device.read_loop():
            if event.type != ecodes.EV_ABS:
                continue

            if event.code == config.BT_STEER_AXIS:
                self.state.steer = self._discrete_steer_angle(event.value)
            elif event.code == config.BT_SPEED_AXIS:
                self.state.speed = self._map_speed(event.value)
            elif event.code == config.BT_BACKWARD_TRIGGER:
                self._backward_pressed = event.value > config.BT_TRIGGER_THRESHOLD
                self._update_direction()
            elif event.code == config.BT_FORWARD_TRIGGER:
                self._forward_pressed = event.value > config.BT_TRIGGER_THRESHOLD
                self._update_direction()
            else:
                continue

            yield self.state

    def close(self) -> None:
        if self._device is not None:
            self._device.close()

