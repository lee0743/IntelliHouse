# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IntelliHouse is an Arduino-based smart home light-tracking system. A servo motor rotates to face whichever of three analog light sensors reads the highest brightness value.

## Hardware

- **Servo motor**: pin 11 (`SERVO_PIN`)
- **Light sensors**: analog pins A0, A1, A2 → mapped to servo angles 0°, 90°, 180°
- **Digital outputs**: pins 3 and 4 (reserved, purpose TBD)
- **Serial**: 9600 baud for debug output

## Building and Flashing

There is no automated build system. Use either:

**Arduino IDE**: Open `2024-11-01.ino`, select your board (Arduino Uno/AVR), and upload.

**Arduino CLI**:
```bash
# Compile
arduino-cli compile --fqbn arduino:avr:uno 2024-11-01.ino

# Upload (replace /dev/ttyUSB0 with the actual port)
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno 2024-11-01.ino
```

## Verifying Behavior

There is no test suite. Verification is done on hardware:
1. Flash the sketch
2. Open Serial Monitor at **9600 baud**
3. The sketch prints the current angle, the winning sensor index, and all three raw brightness values every second
4. Shine light on each sensor in turn and confirm the servo rotates to the corresponding angle

## Code Conventions

- The sketch follows standard Arduino structure: `setup()` runs once, `loop()` runs repeatedly with a 1-second `delay()`.
- `get_max_brightness_sensor_index()` is a plain C-style linear scan — keep helper functions simple and stateless.
- Variable `min_index` in `loop()` is misnamed; it holds the **maximum**-brightness sensor index. Fix the name if touching that code.
- `buf[1024]` is significantly oversized for the `sprintf` call; keep allocations proportionate if adding new serial output.
- Pin numbers are `#define` constants at the top of the file — add new hardware pins there.
