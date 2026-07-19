# TM4C123 IR Remote

An embedded systems project that replaces a TV (or other IR-controlled device) remote using a TM4C123GXL LaunchPad. Point any existing remote at the board, record the raw IR signal for a button, and replay it later on command over a serial terminal.

## How it works

- **Record (`recv <1-16>`)** — A TSOP13438 IR receiver demodulates the incoming 38 kHz signal. Timer0A captures the timestamp of every edge on the receiver's output pin, and the deltas between edges (mark/space durations) are stored in a buffer. A 65 ms gap with no new edge marks the end of the frame.
- **Transmit (`xmit <1-16>`)** — The stored timing array is replayed by toggling a 38 kHz PWM carrier (Timer0B) on and off for the exact recorded durations, driving an IR LED through a transistor.

Because the system captures and replays raw edge timings instead of decoding a specific protocol (NEC, RC5, Sony SIRC, etc.), it works with any remote that uses a 38 kHz IR carrier, regardless of brand or protocol. Recordings are stored in SRAM only and are lost on power-down.

16 keys are supported; key 1 is conventionally reserved for power on/off.

## Hardware

- EK-TM4C123GXL LaunchPad
- TSOP13438 IR receiver
- IR333-A IR LED
- 2N3904 NPN transistor (drives the LED with enough current)
- Resistors/capacitor for receiver filtering and LED current limiting

Full wiring details, the schematic, and the design rationale are in [`plan/`](plan/).

## Firmware layout (`ir_remote/`)

| File | Purpose |
|---|---|
| `main.c` | Command loop: reads `recv`/`xmit` commands from UART |
| `ir.c` / `ir.h` | Core IR capture and playback logic, timer configuration |
| `clock.c` / `clock.h` | PLL setup (40 MHz system clock) |
| `uart0.c` / `uart0.h` | Polled UART0 driver (115200 baud) |
| `wait.c` / `wait.h` | Busy-wait delay helpers |
| `tm4c123gh6pm.h` | TI register definitions |
| `tm4c123gh6pm.cmd` | Linker command file |
| `tm4c123gh6pm_startup_ccs.c` | Interrupt vector table |

## Building

Built with TI Code Composer Studio, targeting the TM4C123GH6PM. Create a CCS project for that target, add all files in `ir_remote/`, and build/flash.

## Usage

1. Connect to the board's virtual COM port at 115200 8-N-1.
2. `recv 1` — point a remote at the receiver and press the power button.
3. `xmit 1` — replay the recorded signal at the target device.
4. Repeat `recv <n>` / `xmit <n>` for keys 2-16 to record and replay other buttons.

See [`plan/project_explanation.txt`](plan/project_explanation.txt) for a full technical writeup, including timer register settings, interrupt priorities, and the software-AND-gate trick used to gate the PWM carrier without extra hardware.
