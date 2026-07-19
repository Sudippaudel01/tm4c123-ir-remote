#!/usr/bin/env python3
"""Generate SVG schematic for IR Remote Control Replacement project."""

import os

SVG_W, SVG_H = 1200, 900

def header():
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}"
     font-family="monospace" font-size="12">
  <defs>
    <marker id="arrowhead" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
      <polygon points="0 0, 6 2, 0 4" fill="#333"/>
    </marker>
  </defs>
  <rect width="{SVG_W}" height="{SVG_H}" fill="white"/>
  <!-- Title block -->
  <rect x="2" y="2" width="{SVG_W-4}" height="{SVG_H-4}" fill="none" stroke="#333" stroke-width="2"/>
  <text x="600" y="35" text-anchor="middle" font-size="22" font-weight="bold" fill="#222">
    IR Remote Control Replacement — Full Circuit Schematic
  </text>
  <text x="600" y="55" text-anchor="middle" font-size="14" fill="#555">
    TM4C123GXL LaunchPad + TSOP13438 + IR333-A LED + 2N2222 NPN
  </text>
'''

def footer():
    return '</svg>\n'

# ─── Drawing helpers ─────────────────────────────────────────────────────────

def line(x1, y1, x2, y2, color="#333", width=2):
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>\n'

def rect(x, y, w, h, fill="none", stroke="#333", sw=2, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}/>\n'

def text(x, y, txt, size=12, anchor="middle", color="#222", weight="normal"):
    return f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{txt}</text>\n'

def circle(cx, cy, r, fill="none", stroke="#333", sw=2):
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'

def dot(cx, cy, r=4):
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#333" stroke="none"/>\n'

# ─── Component drawing functions ─────────────────────────────────────────────

def draw_resistor_v(x, y, label_text, value_text):
    """Vertical resistor, pins at (x, y-30) top and (x, y+30) bottom."""
    s = ""
    s += line(x, y-30, x, y-15)
    # Zigzag body
    pts = [(x, y-15)]
    for i, dy in enumerate([-12, -9, -6, -3, 0, 3, 6, 9, 12, 15]):
        px = x + (8 if (i % 2 == 0) else -8) if i > 0 and i < 9 else x
        if i == 0: px = x + 8
        if i == 9: px = x
        pts.append((px, y - 15 + (dy + 15) * 30/30))
    # Simpler: draw rectangle resistor (IEC style)
    s += rect(x-8, y-15, 16, 30, fill="#fff")
    s += line(x, y+15, x, y+30)
    s += text(x-20, y+5, label_text, size=11, anchor="end", color="#0066cc", weight="bold")
    s += text(x+20, y+5, value_text, size=11, anchor="start", color="#333")
    return s

def draw_resistor_h(x, y, label_text, value_text):
    """Horizontal resistor, pins at (x-30, y) left and (x+30, y) right."""
    s = ""
    s += line(x-30, y, x-15, y)
    s += rect(x-15, y-8, 30, 16, fill="#fff")
    s += line(x+15, y, x+30, y)
    s += text(x, y-15, label_text, size=11, color="#0066cc", weight="bold")
    s += text(x, y+22, value_text, size=11, color="#333")
    return s

def draw_capacitor_v(x, y, label_text, value_text):
    """Vertical polarized cap, pin1(+) at (x,y-20) top, pin2(-) at (x,y+20) bottom."""
    s = ""
    s += line(x, y-20, x, y-5)
    # Top plate (flat line)
    s += line(x-10, y-5, x+10, y-5, width=3)
    # Bottom plate (curved — approximate with arc/line)
    s += f'  <path d="M {x-10} {y+5} Q {x} {y+12} {x+10} {y+5}" fill="none" stroke="#333" stroke-width="2"/>\n'
    s += line(x, y+5, x, y+20)
    # Plus sign
    s += text(x+14, y-8, "+", size=14, anchor="start", weight="bold", color="#cc0000")
    s += text(x-22, y+2, label_text, size=11, anchor="end", color="#0066cc", weight="bold")
    s += text(x+18, y+8, value_text, size=11, anchor="start", color="#333")
    return s

def draw_led_v(x, y, label_text, value_text):
    """Vertical LED, anode at (x,y-25) top, cathode at (x,y+25) bottom. Current flows down."""
    s = ""
    s += line(x, y-25, x, y-10)
    # Triangle pointing down
    s += f'  <polygon points="{x-10},{y-10} {x+10},{y-10} {x},{y+10}" fill="none" stroke="#333" stroke-width="2"/>\n'
    # Cathode bar
    s += line(x-10, y+10, x+10, y+10, width=3)
    s += line(x, y+10, x, y+25)
    # Arrow lines (light emission)
    s += line(x+12, y-8, x+20, y-16, color="#cc0000")
    s += line(x+14, y-2, x+22, y-10, color="#cc0000")
    # Arrowheads
    s += f'  <polygon points="{x+18},{y-18} {x+22},{y-14} {x+16},{y-14}" fill="#cc0000"/>\n'
    s += f'  <polygon points="{x+20},{y-12} {x+24},{y-8} {x+18},{y-8}" fill="#cc0000"/>\n'
    s += text(x-18, y, label_text, size=11, anchor="end", color="#0066cc", weight="bold")
    s += text(x-18, y+14, value_text, size=10, anchor="end", color="#333")
    return s

def draw_npn(x, y, label_text, value_text):
    """NPN BJT. Base at (x-25, y), Collector at (x+10, y-30), Emitter at (x+10, y+30)."""
    s = ""
    # Base line in
    s += line(x-25, y, x-5, y)
    # Vertical bar
    s += line(x-5, y-15, x-5, y+15, width=3)
    # Collector line
    s += line(x-5, y-8, x+10, y-25)
    s += line(x+10, y-25, x+10, y-30)
    # Emitter line with arrow
    s += line(x-5, y+8, x+10, y+25)
    s += line(x+10, y+25, x+10, y+30)
    # Arrow on emitter
    s += f'  <polygon points="{x+6},{y+18} {x+12},{y+24} {x+4},{y+24}" fill="#333"/>\n'
    # Circle
    s += circle(x+2, y, 22, stroke="#333", sw=1.5)
    s += text(x+28, y-5, label_text, size=11, anchor="start", color="#0066cc", weight="bold")
    s += text(x+28, y+10, value_text, size=11, anchor="start", color="#333")
    return s

def draw_tsop(x, y):
    """TSOP13438, body centered at (x,y). Pins come out LEFT side.
    Pin 1 (OUT) at (x-55, y-20), Pin 2 (GND) at (x-55, y), Pin 3 (VS) at (x-55, y+20)."""
    s = ""
    s += rect(x-35, y-35, 70, 70, fill="#f0f0f0", stroke="#333", sw=2, rx=5)
    s += text(x, y-8, "TSOP13438", size=14, weight="bold")
    s += text(x, y+8, "38 kHz IR Receiver", size=10, color="#555")
    # Pin stubs + labels
    # Pin 1: OUT
    s += line(x-35, y-20, x-55, y-20)
    s += text(x-32, y-17, "OUT", size=10, anchor="start", color="#666")
    s += text(x-58, y-17, "1", size=10, anchor="end", color="#999")
    # Pin 2: GND
    s += line(x-35, y, x-55, y)
    s += text(x-32, y+4, "GND", size=10, anchor="start", color="#666")
    s += text(x-58, y+4, "2", size=10, anchor="end", color="#999")
    # Pin 3: VS
    s += line(x-35, y+20, x-55, y+20)
    s += text(x-32, y+24, "VS", size=10, anchor="start", color="#666")
    s += text(x-58, y+24, "3", size=10, anchor="end", color="#999")
    return s

def draw_mcu(x, y):
    """MCU block centered at (x,y). 
    Left pins: PA0 at (x-100,y-40), PA1 at (x-100,y-20), USB at (x-100,y+40)
    Right pins: PB6 at (x+100,y-40), PB7 at (x+100,y-20)
    Top: +5V at (x, y-70), Bottom: GND at (x, y+70)"""
    s = ""
    s += rect(x-80, y-60, 160, 120, fill="#e8f0ff", stroke="#333", sw=2, rx=8)
    s += text(x, y-20, "TM4C123GXL", size=18, weight="bold", color="#003366")
    s += text(x, y, "LaunchPad", size=13, color="#336699")
    s += text(x, y+18, "(EK-TM4C123GXL)", size=10, color="#999")

    # LEFT pins
    # PA0/U0RX
    s += line(x-80, y-40, x-100, y-40)
    s += text(x-78, y-37, "PA0/U0RX", size=9, anchor="start", color="#666")
    # PA1/U0TX
    s += line(x-80, y-20, x-100, y-20)
    s += text(x-78, y-17, "PA1/U0TX", size=9, anchor="start", color="#666")
    # USB
    s += line(x-80, y+40, x-100, y+40)
    s += text(x-78, y+43, "USB", size=9, anchor="start", color="#666")

    # RIGHT pins
    # PB6/T0CCP0
    s += line(x+80, y-40, x+100, y-40)
    s += text(x+78, y-37, "PB6/T0CCP0", size=9, anchor="end", color="#666")
    # PB7/T0CCP1
    s += line(x+80, y-20, x+100, y-20)
    s += text(x+78, y-17, "PB7/T0CCP1", size=9, anchor="end", color="#666")

    # TOP: +5V
    s += line(x, y-60, x, y-70)
    # BOTTOM: GND
    s += line(x, y+60, x, y+70)

    return s

def draw_power_5v(x, y):
    """Power symbol +5V. Connection at (x, y), symbol above."""
    s = ""
    s += line(x, y, x, y-10)
    s += line(x-8, y-15, x, y-10)
    s += line(x+8, y-15, x, y-10)
    s += text(x, y-22, "+5V", size=12, weight="bold", color="#cc0000")
    return s

def draw_gnd(x, y):
    """GND symbol. Connection at (x, y), symbol below."""
    s = ""
    s += line(x, y, x, y+8)
    s += line(x-10, y+8, x+10, y+8, width=2)
    s += line(x-6, y+12, x+6, y+12, width=2)
    s += line(x-3, y+16, x+3, y+16, width=2)
    return s

def draw_net_label(x, y, label_text, anchor="start"):
    """Net label with box."""
    tw = len(label_text) * 8 + 8
    lx = x if anchor == "start" else x - tw
    s = ""
    s += rect(lx, y-10, tw, 20, fill="#ffffcc", stroke="#999", sw=1, rx=3)
    tx = lx + tw//2
    s += text(tx, y+4, label_text, size=12, weight="bold", color="#006600")
    return s

# ─── Main schematic ──────────────────────────────────────────────────────────

def build():
    s = header()

    # ═══════════════════════════════════════════════════════════════════════
    # MCU  — center-left
    # ═══════════════════════════════════════════════════════════════════════
    MX, MY = 300, 400
    s += '  <!-- MCU -->\n'
    s += draw_mcu(MX, MY)

    # MCU +5V
    s += draw_power_5v(MX, MY - 70)
    # MCU GND
    s += draw_gnd(MX, MY + 70)

    # MCU pin header labels
    s += text(MX-100, MY - 40 - 10, "J1.03", size=9, anchor="end", color="#999")
    s += text(MX-100, MY - 20 - 10, "J1.04", size=9, anchor="end", color="#999")
    s += text(MX+100, MY - 40 - 10, "J2.07", size=9, anchor="start", color="#999")
    s += text(MX+100, MY - 20 - 10, "J2.06", size=9, anchor="start", color="#999")
    s += text(MX+15, MY - 75, "J3.01", size=9, anchor="start", color="#999")
    s += text(MX+15, MY + 75, "J3.02", size=9, anchor="start", color="#999")

    # USB label on left
    s += line(MX-100, MY+40, MX-140, MY+40)
    s += rect(MX-220, MY+28, 78, 24, fill="#f0f0f0", stroke="#999", sw=1, rx=4)
    s += text(MX-181, MY+44, "USB to PC", size=11, weight="bold", color="#333")
    s += text(MX-140, MY+58, "(Debug + UART)", size=9, color="#777")

    # UART labels
    s += line(MX-100, MY-40, MX-130, MY-40)
    s += draw_net_label(MX-130, MY-40, "UART_RX", "end")
    s += line(MX-100, MY-20, MX-130, MY-20)
    s += draw_net_label(MX-130, MY-20, "UART_TX", "end")

    # PB6 label on MCU right
    s += line(MX+100, MY-40, MX+130, MY-40)
    s += draw_net_label(MX+130, MY-40, "PB6")
    # PB7 label on MCU right
    s += line(MX+100, MY-20, MX+130, MY-20)
    s += draw_net_label(MX+130, MY-20, "PB7")

    # ═══════════════════════════════════════════════════════════════════════
    # IR RECEIVER SECTION — top right
    # ═══════════════════════════════════════════════════════════════════════
    s += '  <!-- IR Receiver Section -->\n'
    s += rect(590, 80, 380, 290, fill="none", stroke="#0066cc", sw=1.5)
    s += f'  <rect x="592" y="82" width="376" height="22" fill="#0066cc" rx="0"/>\n'
    s += text(780, 97, "IR RECEIVER CIRCUIT", size=13, weight="bold", color="white")

    TX, TY = 830, 220  # TSOP center
    s += draw_tsop(TX, TY)

    # R1: 100Ω between +5V and TSOP VS (pin 3 at TX-55, TY+20)
    R1X, R1Y = TX - 55 - 60, TY + 20  # R1 center
    s += draw_resistor_h(R1X, R1Y, "R1", "100Ω")
    # Wire R1 right to TSOP VS
    s += line(R1X + 30, R1Y, TX - 55, TY + 20)

    # +5V above R1 left
    s += line(R1X - 30, R1Y, R1X - 50, R1Y)
    s += line(R1X - 50, R1Y, R1X - 50, R1Y - 30)
    s += draw_power_5v(R1X - 50, R1Y - 30)

    # C1: 4.7µF between VS node and GND
    C1X, C1Y = TX - 55 - 20, TY + 60
    # Junction dot at VS node
    jx, jy = TX - 55, TY + 20
    s += dot(jx, jy)
    # Wire down from VS node to C1
    s += line(jx, jy, jx, TY + 40)
    s += line(jx, TY + 40, C1X, TY + 40)
    s += draw_capacitor_v(C1X, C1Y, "C1", "4.7µF")
    s += line(C1X, TY + 40, C1X, C1Y - 20)

    # GND on C1 bottom
    s += draw_gnd(C1X, C1Y + 20)

    # TSOP GND (pin 2 at TX-55, TY)
    s += line(TX - 55, TY, TX - 55 - 20, TY)
    s += line(TX - 55 - 20, TY, TX - 55 - 20, TY + 20)
    # Junction to ground path
    gnd_jx = TX - 55 - 20
    s += line(gnd_jx, TY + 20, gnd_jx, C1Y + 20 + 8)
    # Connect to C1's GND line
    s += line(gnd_jx, C1Y + 20 + 8, C1X, C1Y + 20 + 8)
    s += line(C1X, C1Y + 20, C1X, C1Y + 20 + 8)
    s += dot(C1X, C1Y + 20 + 8)

    # TSOP OUT (pin 1 at TX-55, TY-20) → PB6
    s += line(TX - 55, TY - 20, TX - 55 - 80, TY - 20)
    s += draw_net_label(TX - 55 - 80 - 60, TY - 20, "PB6", "start")
    s += line(TX - 55 - 80, TY - 20, TX - 55 - 80 - 60 + 1, TY - 20)

    # ═══════════════════════════════════════════════════════════════════════
    # IR LED TRANSMITTER SECTION — bottom right
    # ═══════════════════════════════════════════════════════════════════════
    s += '  <!-- IR LED Transmitter Section -->\n'
    s += rect(590, 400, 380, 370, fill="none", stroke="#cc6600", sw=1.5)
    s += f'  <rect x="592" y="402" width="376" height="22" fill="#cc6600" rx="0"/>\n'
    s += text(780, 417, "IR LED TRANSMITTER CIRCUIT", size=13, weight="bold", color="white")

    # Vertical chain: +5V → R2 (47Ω) → LED (IR333-A) → Q1 collector → Q1 emitter → GND
    CX = 800  # center X for vertical chain
    CY_START = 460

    # +5V
    s += draw_power_5v(CX, CY_START)

    # R2: 47Ω
    R2Y = CY_START + 40
    s += draw_resistor_v(CX, R2Y, "R2", "47Ω")
    s += line(CX, CY_START, CX, R2Y - 30)

    # LED
    LEDY = R2Y + 70
    s += draw_led_v(CX, LEDY, "D1", "IR333-A")
    s += line(CX, R2Y + 30, CX, LEDY - 25)

    # Q1: 2N2222 NPN
    Q1X, Q1Y = CX - 10, LEDY + 70
    s += draw_npn(Q1X, Q1Y, "Q1", "2N2222")
    # Wire LED cathode to Q1 collector
    s += line(CX, LEDY + 25, Q1X + 10, LEDY + 25)
    s += line(Q1X + 10, LEDY + 25, Q1X + 10, Q1Y - 30)

    # GND on Q1 emitter
    s += draw_gnd(Q1X + 10, Q1Y + 30)

    # R3: 1kΩ to Q1 base
    R3X = Q1X - 25 - 55
    R3Y = Q1Y
    s += draw_resistor_h(R3X, R3Y, "R3", "1kΩ")
    # Wire R3 right to Q1 base
    s += line(R3X + 30, R3Y, Q1X - 25, Q1Y)

    # PB7 label on R3 left
    s += line(R3X - 30, R3Y, R3X - 50, R3Y)
    s += draw_net_label(R3X - 50 - 55, R3Y, "PB7", "start")
    s += line(R3X - 50, R3Y, R3X - 50 - 55 + 1, R3Y)

    # ═══════════════════════════════════════════════════════════════════════
    # NOTES
    # ═══════════════════════════════════════════════════════════════════════
    s += '  <!-- Notes -->\n'
    s += rect(20, 600, 550, 270, fill="#fafafa", stroke="#999", sw=1, rx=5)
    s += text(30, 620, "WIRING  NOTES  &amp;  BOM", size=14, weight="bold", anchor="start", color="#333")

    notes = [
        "Pin Connections on TM4C123GXL LaunchPad:",
        "  PB6 (T0CCP0) = Header J2, Pin 7  →  TSOP13438 OUT (pin 1)",
        "  PB7 (T0CCP1) = Header J2, Pin 6  →  R3 (1kΩ) → Q1 Base",
        "  PA0 (U0RX)   = Header J1, Pin 3  →  USB Virtual COM (built-in)",
        "  PA1 (U0TX)   = Header J1, Pin 4  →  USB Virtual COM (built-in)",
        "  +5V           = Header J3, Pin 1  →  R1→TSOP VS, R2→LED chain",
        "  GND           = Header J3, Pin 2  →  TSOP GND, Q1 Emitter",
        "",
        "Bill of Materials:",
        "  R1 = 100Ω ¼W       (TSOP supply filter)",
        "  R2 = 47Ω  ¼W       (LED current limit: I≈50mA)",
        "  R3 = 1kΩ  ¼W       (Base drive: I≈3.2mA)",
        "  C1 = 4.7µF 16V electrolytic  (TSOP supply bypass, + to VS)",
        "  D1 = IR333-A IR LED  (940nm, long lead = Anode)",
        "  Q1 = 2N2222 NPN BJT  (TO-92, flat side: E-B-C left to right)",
        "  U2 = TSOP13438       (38kHz IR receiver, pin 1=OUT, 2=GND, 3=VS)",
    ]
    for i, n in enumerate(notes):
        color = "#333" if not n.startswith(" ") else "#555"
        weight = "bold" if n.startswith("Pin") or n.startswith("Bill") else "normal"
        s += text(30, 638 + i * 16, n, size=11, anchor="start", color=color, weight=weight)

    # Current flow annotation on LED circuit
    s += text(CX + 35, CY_START + 40, "I_LED ≈ 50 mA", size=10, anchor="start", color="#cc0000")
    s += text(CX + 35, CY_START + 55, "(5V - 1.2V - 0.2V) / 47Ω", size=9, anchor="start", color="#999")

    # Signal flow annotation on TSOP
    s += text(TX - 55 - 40, TY - 35, "IR signal (inverted,", size=9, anchor="middle", color="#0066cc")
    s += text(TX - 55 - 40, TY - 24, "active-low pulses)", size=9, anchor="middle", color="#0066cc")

    s += footer()
    return s

# Write
output_dir = "/home/rupert/Desktop/embedded Projecy/plan"
output_path = os.path.join(output_dir, "ir_remote_schematic.svg")
with open(output_path, 'w') as f:
    f.write(build())

print(f"SVG schematic written to: {output_path}")
print(f"File size: {os.path.getsize(output_path)} bytes")
print("Open in any web browser (Firefox, Chrome) or image viewer")
