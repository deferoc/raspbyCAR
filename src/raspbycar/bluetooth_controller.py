"""Lettura input da gamepad collegato via Bluetooth (protocollo HID / evdev).

Mapping DualShock 4:
asse 0 = sterzo (stick sinistro X),
asse 2 = L2 = retromarcia,
asse 5 = R2 = marcia avanti.

La pressione di L2/R2 determina anche la velocità del motore.
"""

from __future__ import annotations

from dataclasses import dataclass

import evdev
from evdev import ecodes

from . import config


@dataclass
class ControllerState:
    """Stato normalizzato del controller in un dato istante."""

    steer_axis: int = 0
    steer: float = config.STEERING_CENTER_ANGLE
    direction: str = "stop"
    speed: float = 0.0
    backward_trigger: int = 0
    forward_trigger: int = 0


class BluetoothController:
    """Wrapper su un joypad Bluetooth tramite evdev."""

    def __init__(self, name_hint: str = config.BT_CONTROLLER_NAME_HINT) -> None:
        self._name_hint = name_hint
        self._device: evdev.InputDevice | None = None

        self.state = ControllerState()

        self._backward_value = 0
        self._forward_value = 0

    def _set_raw_state(self, event_code: int, value: int) -> None:
        """Aggiorna i valori grezzi del joypad usati per il debug."""
        if event_code == config.BT_STEER_AXIS:
            self.state.steer_axis = value
            self.state.steer = self._discrete_steer_angle(value)
        elif event_code == config.BT_BACKWARD_TRIGGER:
            self.state.backward_trigger = value
            self._backward_value = value
            self._update_direction()
        elif event_code == config.BT_FORWARD_TRIGGER:
            self.state.forward_trigger = value
            self._forward_value = value
            self._update_direction()

    @property
    def is_connected(self) -> bool:
        return self._device is not None

    def connect(self) -> bool:
        """Cerca il gamepad tra i device disponibili."""

        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            name = device.name.lower()

            if self._name_hint.lower() not in name:
                device.close()
                continue

            # Ignora il dispositivo dedicato ai sensori di movimento.
            if "motion sensors" in name or "touchpad" in name:
                device.close()
                continue

            self._device = device

            # Stato iniziale sicuro.
            self.state.direction = "stop"
            self.state.speed = 0.0

            print(f"Joypad trovato: {device.name} ({device.path})")

            return True

        return False

    def disconnect(self) -> None:
        """Disconnette il controller e porta il sistema in stato sicuro."""

        if self._device is not None:
            self._device.close()

        self._device = None

        self._backward_value = 0
        self._forward_value = 0

        # STOP DI SICUREZZA
        self.state.direction = "stop"
        self.state.speed = 0.0

    def _update_direction(self) -> None:
        """Aggiorna direzione e velocità in base a L2/R2.

        Il motore non parte sotto i ~1.2V richiesti al suo avviamento, quindi
        il trigger deve essere considerato spento finché il valore raw non
        raggiunge la soglia minima di accensione.
        """

        backward = self._backward_value
        forward = self._forward_value

        threshold = config.BT_TRIGGER_THRESHOLD
        start_raw = config.BT_TRIGGER_START_RAW

        # --------------------------------------------------
        # Entrambi premuti oppure nessuno premuto -> STOP
        # --------------------------------------------------
        if (
            (backward >= start_raw and forward >= start_raw)
            or
            (backward < start_raw and forward < start_raw)
        ):
            self.state.direction = "stop"
            self.state.speed = 0.0
            return

        # --------------------------------------------------
        # L2 -> RETROMARCIA
        # --------------------------------------------------
        if backward >= start_raw:
            self.state.direction = "backward"
            self.state.speed = self._map_trigger_speed(backward)
            return

        # --------------------------------------------------
        # R2 -> AVANTI
        # --------------------------------------------------
        if forward >= start_raw:
            self.state.direction = "forward"
            self.state.speed = self._map_trigger_speed(forward)
            return

        # Sicurezza
        self.state.direction = "stop"
        self.state.speed = 0.0

    @staticmethod
    def _discrete_steer_angle(value: int) -> float:
        """Mappa il valore dell'asse X del joypad sull'intervallo di angoli del servo.

        Convenzione richiesta:
        - raw 0 -> -10°
        - raw 255 -> 65°
        - raw 128 -> circa 22° (centro geometrico)
        """

        raw_min = config.BT_STEER_RAW_MIN
        raw_max = config.BT_STEER_RAW_MAX
        angle_min = config.BT_STEER_ANGLE_MIN
        angle_max = config.BT_STEER_ANGLE_MAX

        if value <= raw_min:
            return float(angle_min)

        if value >= raw_max:
            return float(angle_max)

        normalized = (value - raw_min) / (raw_max - raw_min)
        return angle_min + normalized * (angle_max - angle_min)

    @staticmethod
    def _map_trigger_speed(value: int) -> float:
        """Mappa il valore raw del trigger in velocità usando la taratura reale
        del motore: 1 -> 1.2V, 255 -> 7.0V.

        In questo modo il motore resta fermo sotto il primissimo valore utile
        e non vibra a riposo.
        """

        start_raw = config.BT_TRIGGER_START_RAW
        if value <= 0:
            return 0.0

        if value < start_raw:
            return 0.0

        raw_span = max(1, 255 - start_raw)
        mapped = (value - start_raw) / raw_span
        voltage = (
            config.DC_MOTOR_MIN_START_VOLTAGE
            + mapped * (config.DC_MOTOR_SUPPLY_VOLTAGE - config.DC_MOTOR_MIN_START_VOLTAGE)
        )
        return max(0.0, min(1.0, voltage / config.DC_MOTOR_SUPPLY_VOLTAGE))

    def events(self):
        """Genera lo stato aggiornato del controller ad ogni evento."""

        if self._device is None:
            return

        try:
            for event in self._device.read_loop():

                if event.type != ecodes.EV_ABS:
                    continue

                # --------------------------------------------------
                # Stick sinistro X -> sterzo
                # ABS_X = 0
                # --------------------------------------------------
                if event.code == config.BT_STEER_AXIS:
                    self._set_raw_state(event.code, event.value)

                # --------------------------------------------------
                # L2 -> retromarcia + velocità
                # ABS_Z = 2
                # --------------------------------------------------
                elif event.code == config.BT_BACKWARD_TRIGGER:
                    self._set_raw_state(event.code, event.value)

                # --------------------------------------------------
                # R2 -> avanti + velocità
                # ABS_RZ = 5
                # --------------------------------------------------
                elif event.code == config.BT_FORWARD_TRIGGER:
                    self._set_raw_state(event.code, event.value)

                else:
                    continue

                yield self.state

        except OSError:
            # Controller scollegato.
            self.disconnect()

    def close(self) -> None:
        """Chiude il dispositivo del gamepad."""

        self.disconnect()