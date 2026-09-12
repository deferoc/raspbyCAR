from raspbycar.bluetooth_controller import ControllerState
from raspbycar.car import Car


def test_controller_state_exposes_raw_input_values() -> None:
    state = ControllerState(
        steer_axis=140,
        steer=22,
        direction="forward",
        speed=0.65,
        backward_trigger=40,
        forward_trigger=180,
    )

    assert state.steer_axis == 140
    assert state.backward_trigger == 40
    assert state.forward_trigger == 180


def test_car_reports_live_motor_and_steering_values() -> None:
    car = Car()

    state = ControllerState(
        steer_axis=128,
        steer=22,
        direction="forward",
        speed=0.5,
        backward_trigger=0,
        forward_trigger=128,
    )

    car._apply_state(state)

    assert car._motor.current_speed == 0.5
    assert car._motor.command_voltage == 3.5
    assert car._steering.current_angle == 22

    report = car._format_debug_report(state)
    assert "L2=" in report
    assert "R2=" in report
    assert "motor" in report.lower()
    assert "servo" in report.lower()
