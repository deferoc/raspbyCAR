#!/usr/bin/env python3
"""Unico entry point del progetto: eseguire `python main.py` sul Raspberry Pi."""

from raspbycar.car import Car


def main() -> None:
    car = Car()
    try:
        car.run()
    except KeyboardInterrupt:
        pass
    finally:
        car.close()


if __name__ == "__main__":
    main()
