"""Configurazione centralizzata: pin GPIO e parametri regolabili."""

# --- Motore DC (avanti/indietro) ---
# Driver H-bridge: due pin di direzione (IN1/IN2) + un pin PWM di enable.
DC_MOTOR_FORWARD_PIN = 4    # IN1
DC_MOTOR_BACKWARD_PIN = 27  # IN2
DC_MOTOR_ENABLE_PIN = 17    # PWM per la velocità

DC_MOTOR_DEFAULT_SPEED = 0.5  # 0.0 - 1.0, usata se il gamepad non è collegato

# --- Servo di sterzo (destra/centro/sinistra) ---
STEERING_SERVO_PIN = 18
STEERING_MIN_ANGLE = -90
STEERING_MAX_ANGLE = 90
STEERING_MIN_PULSE_WIDTH = 0.0005
STEERING_MAX_PULSE_WIDTH = 0.0025

STEERING_LEFT_ANGLE = -10
STEERING_CENTER_ANGLE = 22
STEERING_RIGHT_ANGLE = 65
STEERING_SETTLE_TIME = 0.05  # secondi di attesa prima di rilasciare il servo (detach)

# --- Controller Bluetooth (gamepad) ---
# Nome (o parte del nome) del device come appare in /dev/input/ tramite evdev.
BT_CONTROLLER_NAME_HINT = "Wireless Controller"

# Secondi tra un tentativo di connessione al joypad e il successivo.
BT_RECONNECT_INTERVAL = 2.0

# ASSI / TRIGGER DEL DUALSHOCK 4
# ============================================================

# Stick sinistro X -> sterzo
# ABS_X = codice 0
BT_STEER_AXIS = 0

# L2 -> retromarcia
# ABS_Z = codice 2
BT_BACKWARD_TRIGGER = 2

# R2 -> marcia avanti
# ABS_RZ = codice 5
BT_FORWARD_TRIGGER = 5

# Zona morta del trigger: valori vicini a 0 sono rumore / offset del joypad.
# Dopo la zona morta, i valori vengono considerati come pressione reale.
BT_TRIGGER_DEADBAND = 20

# Valore minimo del trigger considerato "premuto" dopo la zona morta.
# 0 = non premuto
# 255 = completamente premuto
BT_TRIGGER_THRESHOLD = 10


# Soglie per discretizzare l'asse di sterzo in sinistra/centro/destra.
BT_STEER_RIGHT_THRESHOLD = 10
BT_STEER_LEFT_THRESHOLD = 240

# --- Sensore alimentazione L298N ---
# Pin collegato, tramite un partitore di tensione (es. 10k+10k) o un
# optoisolatore, alla linea a 7V del L298N. NON collegare i 7V direttamente
# al GPIO (max 3.3V): si danneggerebbe il Raspberry Pi.
L298N_POWER_SENSE_PIN = 22


