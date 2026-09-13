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
STEERING_SETTLE_TIME = 0.04  # secondi di assestamento servo dopo il comando angolare

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

# Il motore ha un minimo di avviamento reale di circa 1.2V.
# In base alla tua taratura, il valore di trigger che manda 1.2V è 1,
# per entrambi i trigger L2 e R2.
DC_MOTOR_SUPPLY_VOLTAGE = 7.0
DC_MOTOR_MIN_START_VOLTAGE = 1.2

# Re-arm periodico del bridge: aiuta a uscire da rari stati di blocco
# senza riavviare il processo Python.
DC_MOTOR_REARM_INTERVAL = 0.8
DC_MOTOR_REARM_PULSE = 0.03
DC_MOTOR_REARM_EPSILON = 0.01

# Raw del trigger da cui inizia la curva di accelerazione.
# 1 -> 1.2V ; 255 -> 7.0V
BT_TRIGGER_START_RAW = 1
BT_TRIGGER_THRESHOLD = 1


# Mappatura lineare dell'asse X del joypad sul range del servo.
# 0 -> -10°  ; 255 -> 65°
# Il centro in questo intervallo è calcolato come:
# center_raw = (255 - 0) / 2 = 127.5 ≈ 128
# angolo_centrale = -10 + ((128 - 0) / 255) * (65 - (-10)) ≈ 22°
BT_STEER_RAW_MIN = 0
BT_STEER_RAW_MAX = 255
BT_STEER_ANGLE_MIN = -10
BT_STEER_ANGLE_MAX = 65
BT_STEER_CENTER_RAW = 128

# Soglie con isteresi per il comando discreto sinistra/centro/destra.
BT_STEER_LEFT_ENTER_RAW = 96
BT_STEER_LEFT_EXIT_RAW = 112
BT_STEER_RIGHT_ENTER_RAW = 160
BT_STEER_RIGHT_EXIT_RAW = 144

# Inverte i comandi left/right se la cinematica dello sterzo è montata al contrario.
STEERING_INVERT_DIRECTION = True

# --- Sensore alimentazione L298N ---
# Pin collegato, tramite un partitore di tensione (es. 10k+10k) o un
# optoisolatore, alla linea a 7V del L298N. NON collegare i 7V direttamente
# al GPIO (max 3.3V): si danneggerebbe il Raspberry Pi.
L298N_POWER_SENSE_PIN = 22


