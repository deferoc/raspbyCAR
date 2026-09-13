#!/usr/bin/env python3
"""Unico entry point del progetto: eseguire python main.py sul Raspberry Pi."""

import atexit
import signal

from raspbycar.car import Car


def main() -> None:
    car = Car()
    is_closed = False

    def safe_close() -> None:
        nonlocal is_closed
        if is_closed:
            return
        is_closed = True
        try:
            car.close()
        except Exception as exc:
            print(f"Errore durante close sicuro: {exc}")

    def _signal_handler(signum, _frame) -> None:
        print(f"Segnale {signum} ricevuto: arresto sicuro in corso...")
        safe_close()
        raise SystemExit(0)

    atexit.register(safe_close)
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        car.run()
    except KeyboardInterrupt:
        pass
    finally:
        safe_close()


if __name__ == "__main__":
    main()
