#!/usr/bin/env python3
"""Generate a hand-drawn style SVG circuit schematic for IR Remote project.
Shows all connections as continuous wires - no net labels."""

import os, math

W, H = 1400, 1000

def L(x1,y1,x2,y2,c="#222",w=1.5):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>\n'

def T(x,y,t,sz=11,a="middle",c="#222",w="normal",rot=0):
    tr = f' transform="rotate({rot},{x},{y})"' if rot else ""
    return f'<text x="{x}" y="{y}" text-anchor="{a}" font-size="{sz}" font-weight="{w}" fill="{c}"{tr}>{t}</text>\n'

def D(cx,cy,r=3):
    """Junction dot"""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#222"/>\n'

def zigzag_v(x, y1, y2):
    """Vertical zigzag resistor body from y1 to y2 (y2>y1). Returns path string."""
    h = y2 - y1
    segs = 6
    dy = h / (segs * 2 + 2)
    pts = [(x, y1)]
    pts.append((x, y1 + dy))
    for i in range(segs):
        side = 6 if i % 2 == 0 else -6
        pts.append((x + side, y1 + dy + dy * (2*i+1)))
        pts.append((x - side, y1 + dy + dy * (2*i+2)))
    pts.append((x, y2 - dy))
    pts.append((x, y2))
    d = "M " + " L ".join(f"{px},{py}" for px,py in pts)
    return f'<path d="{d}" fill="none" stroke="#222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>\n'

def zigzag_h(x1, x2, y):
    """Horizontal zigzag resistor body from x1 to x2 (x2>x1)."""
    w = x2 - x1
    segs = 6
    dx = w / (segs * 2 + 2)
    pts = [(x1, y)]
    pts.append((x1 + dx, y))
    for i in range(segs):
        side = 6 if i % 2 == 0 else -6
        pts.append((x1 + dx + dx * (2*i+1), y + side))
        pts.append((x1 + dx + dx * (2*i+2), y - side))
    pts.append((x2 - dx, y))
    pts.append((x2, y))
    d = "M " + " L ".join(f"{px},{py}" for px,py in pts)
    return f'<path d="{d}" fill="none" stroke="#222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>\n'

def pwr5v(x, y):
    """"+5V" power rail arrow. Connection point at (x, y+12)."""
    s = ""
    s += L(x, y+12, x, y+4)
    s += L(x-6, y+6, x, y)
    s += L(x+6, y+6, x, y)
    s += T(x, y-4, "+5V", 11, "middle", "#cc0000", "bold")
    return s

def gnd(x, y):
    """GND symbol. Connection at (x, y)."""
    s = ""
    s += L(x, y, x, y+6)
    s += L(x-8, y+6, x+8, y+6, w=1.5)
    s += L(x-5, y+10, x+5, y+10, w=1.5)
    s += L(x-2, y+14, x+2, y+14, w=1.5)
    return s

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     font-family="'Courier New', monospace" font-size="11">
<rect width="{W}" height="{H}" fill="#fffff8"/>
<rect x="3" y="3" width="{W-6}" height="{H-6}" fill="none" stroke="#222" stroke-width="1.5"/>
'''

# ═══════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════
svg += T(700, 30, "IR Remote Control Replacement — Circuit Schematic", 20, "middle", "#222", "bold")
svg += T(700, 50, "TM4C123GXL + TSOP13438 + IR333-A + 2N2222", 13, "middle", "#555")

# ═══════════════════════════════════════════════════════════════════════════
# TM4C123GXL MCU BLOCK — center
# ═══════════════════════════════════════════════════════════════════════════
MX, MY = 450, 420  # MCU center
MW, MH = 180, 200  # half-width, half-height... nah let's do explicit

mcuL = MX - 100
mcuR = MX + 100
mcuT = MY - 90
mcuB = MY + 90

svg += f'<rect x="{mcuL}" y="{mcuT}" width="200" height="180" fill="#f8f8f0" stroke="#222" stroke-width="2" rx="3"/>\n'
svg += T(MX, MY-30, "TM4C123GXL", 16, "middle", "#222", "bold")
svg += T(MX, MY-12, "LaunchPad", 12, "middle", "#555")

# Pin labels INSIDE the box, stubs go OUT
# Left side pins
pa0_y = mcuT + 40
pa1_y = mcuT + 60
usb_y = mcuT + 140

svg += L(mcuL, pa0_y, mcuL - 30, pa0_y)
svg += T(mcuL + 5, pa0_y + 4, "PA0", 10, "start", "#222")
svg += T(mcuL + 5, pa0_y + 14, "U0RX", 8, "start", "#888")

svg += L(mcuL, pa1_y, mcuL - 30, pa1_y)
svg += T(mcuL + 5, pa1_y + 4, "PA1", 10, "start", "#222")
svg += T(mcuL + 5, pa1_y + 14, "U0TX", 8, "start", "#888")

svg += L(mcuL, usb_y, mcuL - 30, usb_y)
svg += T(mcuL + 5, usb_y + 4, "USB", 10, "start", "#222")

# Right side pins
pb6_y = mcuT + 40
pb7_y = mcuT + 70

svg += L(mcuR, pb6_y, mcuR + 30, pb6_y)
svg += T(mcuR - 5, pb6_y + 4, "PB6", 10, "end", "#222")
svg += T(mcuR - 5, pb6_y + 14, "T0CCP0", 8, "end", "#888")

svg += L(mcuR, pb7_y, mcuR + 30, pb7_y)
svg += T(mcuR - 5, pb7_y + 4, "PB7", 10, "end", "#222")
svg += T(mcuR - 5, pb7_y + 14, "T0CCP1", 8, "end", "#888")

# Top: +5V pin
v5_mcu_x = MX + 30
svg += L(v5_mcu_x, mcuT, v5_mcu_x, mcuT - 25)
svg += T(v5_mcu_x - 5, mcuT + 12, "+5V", 9, "end", "#222")
svg += pwr5v(v5_mcu_x, mcuT - 37)

# Bottom: GND pin
gnd_mcu_x = MX + 30
svg += L(gnd_mcu_x, mcuB, gnd_mcu_x, mcuB + 10)
svg += T(gnd_mcu_x - 5, mcuB - 5, "GND", 9, "end", "#222")
svg += gnd(gnd_mcu_x, mcuB + 10)

# Header pin labels (outside)
svg += T(mcuR + 35, pb6_y - 8, "J2 pin 7", 9, "start", "#0066aa")
svg += T(mcuR + 35, pb7_y - 8, "J2 pin 6", 9, "start", "#0066aa")
svg += T(v5_mcu_x + 15, mcuT - 28, "J3 pin 1", 9, "start", "#0066aa")
svg += T(gnd_mcu_x + 15, mcuB + 18, "J3 pin 2", 9, "start", "#0066aa")

# USB annotation
svg += L(mcuL - 30, usb_y, mcuL - 80, usb_y)
svg += f'<rect x="{mcuL - 180}" y="{usb_y - 18}" width="100" height="36" fill="#f0f0f0" stroke="#222" stroke-width="1" rx="5"/>\n'
svg += T(mcuL - 130, usb_y - 2, "USB Cable", 10, "middle", "#222", "bold")
svg += T(mcuL - 130, usb_y + 12, "to PC/Terminal", 9, "middle", "#666")

# ═══════════════════════════════════════════════════════════════════════════
# TSOP13438 IR RECEIVER — upper right, connected by wire to PB6
# ═══════════════════════════════════════════════════════════════════════════

# TSOP13438 chip box
TX, TY = 950, 220  # TSOP center
tsopW, tsopH = 60, 70  # half w/h
tsopL = TX - 50
tsopR = TX + 50
tsopT = TY - 45
tsopB = TY + 45

svg += f'<rect x="{tsopL}" y="{tsopT}" width="100" height="90" fill="#f0f0f0" stroke="#222" stroke-width="2" rx="2"/>\n'
svg += T(TX, TY - 8, "TSOP", 13, "middle", "#222", "bold")
svg += T(TX, TY + 8, "13438", 13, "middle", "#222", "bold")
svg += T(TX, TY + 25, "38kHz", 9, "middle", "#888")

# TSOP pins come out LEFT
# Pin 1 = OUT (top)
# Pin 2 = GND (middle)
# Pin 3 = VS  (bottom)
tout_y = tsopT + 20
tgnd_y = TY
tvs_y  = tsopB - 20

svg += L(tsopL, tout_y, tsopL - 25, tout_y)
svg += T(tsopL + 4, tout_y + 4, "OUT", 9, "start", "#555")
svg += T(tsopL - 28, tout_y + 4, "1", 9, "end", "#999")

svg += L(tsopL, tgnd_y, tsopL - 25, tgnd_y)
svg += T(tsopL + 4, tgnd_y + 4, "GND", 9, "start", "#555")
svg += T(tsopL - 28, tgnd_y + 4, "2", 9, "end", "#999")

svg += L(tsopL, tvs_y, tsopL - 25, tvs_y)
svg += T(tsopL + 4, tvs_y + 4, "VS", 9, "start", "#555")
svg += T(tsopL - 28, tvs_y + 4, "3", 9, "end", "#999")

# ── R1: 100Ω from +5V to TSOP VS (pin 3) ────────────────────────────────
# +5V rail above, wire down, R1 zigzag, then right to TSOP VS
r1_x = tsopL - 25 - 60  # R1 center X
r1_top = tvs_y - 55
r1_bot = tvs_y

# +5V above R1
svg += pwr5v(r1_x, r1_top - 22)
svg += L(r1_x, r1_top - 10, r1_x, r1_top)

# R1 zigzag vertical
svg += zigzag_v(r1_x, r1_top, r1_bot)
svg += T(r1_x + 12, (r1_top + r1_bot)//2 - 8, "R1", 11, "start", "#222", "bold")
svg += T(r1_x + 12, (r1_top + r1_bot)//2 + 6, "100Ω", 10, "start", "#222")

# Wire from R1 bottom to TSOP VS pin
svg += L(r1_x, r1_bot, tsopL - 25, tvs_y)

# ── C1: 4.7µF between VS rail and GND ────────────────────────────────────
# Junction dot on VS wire
jc_x = (r1_x + tsopL - 25) // 2
svg += D(jc_x, tvs_y)

# C1 below the junction
c1_top = tvs_y
c1_bot = tvs_y + 50
svg += L(jc_x, c1_top, jc_x, c1_top + 18)
# Capacitor plates
svg += L(jc_x - 10, c1_top + 18, jc_x + 10, c1_top + 18, w=2.5)
svg += f'<path d="M {jc_x-10} {c1_top+25} Q {jc_x} {c1_top+30} {jc_x+10} {c1_top+25}" fill="none" stroke="#222" stroke-width="2"/>\n'
svg += L(jc_x, c1_top + 25, jc_x, c1_bot)
# + sign
svg += T(jc_x + 14, c1_top + 14, "+", 12, "start", "#cc0000", "bold")
svg += T(jc_x - 15, c1_top + 32, "C1", 11, "end", "#222", "bold")
svg += T(jc_x - 15, c1_top + 45, "4.7µF", 10, "end", "#222")

# GND on C1 bottom
svg += gnd(jc_x, c1_bot)

# ── TSOP GND (pin 2) to GND ──────────────────────────────────────────────
# Wire from TSOP GND pin down, then to GND
tgnd_wire_x = tsopL - 25
svg += L(tgnd_wire_x, tgnd_y, tgnd_wire_x, tgnd_y + 35)
svg += gnd(tgnd_wire_x, tgnd_y + 35)

# ── TSOP OUT (pin 1) → long wire to MCU PB6 ──────────────────────────────
# Wire from TSOP OUT to MCU PB6
tout_wire_end_x = tsopL - 25
pb6_stub = mcuR + 30

# Route: go left from TSOP out, then down+left to MCU PB6 level, then left to PB6
wire_turn_x = tout_wire_end_x - 40
wire_turn_y = tout_y

svg += L(tout_wire_end_x, tout_y, wire_turn_x, tout_y)
# Go down to PB6 height
svg += L(wire_turn_x, tout_y, wire_turn_x, pb6_y)
# Go left to MCU PB6 stub
svg += L(wire_turn_x, pb6_y, pb6_stub, pb6_y)

# Label on wire
svg += T((wire_turn_x + pb6_stub)//2, pb6_y - 10, "TSOP OUT → PB6 (IR input signal)", 10, "middle", "#0066aa")

# ═══════════════════════════════════════════════════════════════════════════
# IR LED TRANSMITTER — lower right, connected by wire from PB7
# ═══════════════════════════════════════════════════════════════════════════

# The chain: PB7 → R3(1kΩ) → Q1 base ; Q1 collector ← LED cathode ← LED anode ← R2(47Ω) ← +5V
# Q1 emitter → GND

# Q1 center position
QX, QY = 950, 620

# ── Q1: 2N2222 NPN Transistor ────────────────────────────────────────────
# Draw NPN symbol
# Base at left (QX-30, QY)
# Collector at top (QX+15, QY-35)
# Emitter at bottom (QX+15, QY+35)

# Base input line
svg += L(QX - 50, QY, QX - 15, QY)
# Vertical bar
svg += L(QX - 15, QY - 20, QX - 15, QY + 20, w=3)
# Collector line (angled up-right)
svg += L(QX - 15, QY - 10, QX + 15, QY - 35)
svg += L(QX + 15, QY - 35, QX + 15, QY - 50)
# Emitter line (angled down-right) with arrow
svg += L(QX - 15, QY + 10, QX + 15, QY + 35)
svg += L(QX + 15, QY + 35, QX + 15, QY + 50)
# Arrow on emitter
svg += f'<polygon points="{QX+8},{QY+22} {QX+18},{QY+32} {QX+6},{QY+32}" fill="#222"/>\n'
# Circle around transistor
svg += f'<circle cx="{QX}" cy="{QY}" r="28" fill="none" stroke="#222" stroke-width="1.5"/>\n'

# Labels
svg += T(QX + 32, QY - 5, "Q1", 12, "start", "#222", "bold")
svg += T(QX + 32, QY + 10, "2N2222", 11, "start", "#222")
svg += T(QX + 20, QY - 42, "C", 9, "start", "#888")
svg += T(QX - 55, QY + 4, "B", 9, "end", "#888")
svg += T(QX + 20, QY + 45, "E", 9, "start", "#888")

# GND on emitter
svg += gnd(QX + 15, QY + 50)

# ── R3: 1kΩ from PB7 wire to Q1 base ─────────────────────────────────────
r3_left = QX - 50 - 55
r3_right = QX - 50
r3_y = QY

svg += zigzag_h(r3_left, r3_right, r3_y)
svg += T((r3_left + r3_right)//2, r3_y - 12, "R3", 11, "middle", "#222", "bold")
svg += T((r3_left + r3_right)//2, r3_y + 18, "1kΩ", 10, "middle", "#222")

# ── Wire from MCU PB7 → R3 ───────────────────────────────────────────────
pb7_stub = mcuR + 30
wire_pb7_turn_x = pb7_stub + 50

svg += L(pb7_stub, pb7_y, wire_pb7_turn_x, pb7_y)
svg += L(wire_pb7_turn_x, pb7_y, wire_pb7_turn_x, r3_y)
svg += L(wire_pb7_turn_x, r3_y, r3_left, r3_y)

svg += T((wire_pb7_turn_x + r3_left)//2, r3_y - 12, "PB7 → R3 → Q1 base (PWM drive)", 10, "middle", "#0066aa")

# ── LED: IR333-A above Q1 collector ───────────────────────────────────────
# LED vertical: anode at top, cathode at bottom
led_x = QX + 15
led_anode_y = QY - 90
led_cathode_y = QY - 50

# Wire from Q1 collector top to LED cathode
# (Q1 collector wire already goes to QY-50)

# LED triangle (pointing down = current flows down)
svg += f'<polygon points="{led_x - 12},{led_anode_y+5} {led_x + 12},{led_anode_y+5} {led_x},{led_cathode_y-5}" fill="none" stroke="#222" stroke-width="1.5"/>\n'
# Cathode bar
svg += L(led_x - 12, led_cathode_y - 5, led_x + 12, led_cathode_y - 5, w=2.5)
# Wires
svg += L(led_x, led_anode_y - 15, led_x, led_anode_y + 5)
svg += L(led_x, led_cathode_y - 5, led_x, led_cathode_y)  # to collector wire

# IR emission arrows
svg += L(led_x + 14, led_anode_y + 8, led_x + 24, led_anode_y, "#cc0000")
svg += f'<polygon points="{led_x+22},{led_anode_y-3} {led_x+26},{led_anode_y+3} {led_x+20},{led_anode_y+1}" fill="#cc0000"/>\n'
svg += L(led_x + 16, led_anode_y + 16, led_x + 26, led_anode_y + 8, "#cc0000")
svg += f'<polygon points="{led_x+24},{led_anode_y+5} {led_x+28},{led_anode_y+11} {led_x+22},{led_anode_y+9}" fill="#cc0000"/>\n'

svg += T(led_x - 18, (led_anode_y + led_cathode_y)//2 - 4, "D1", 11, "end", "#222", "bold")
svg += T(led_x - 18, (led_anode_y + led_cathode_y)//2 + 10, "IR333-A", 10, "end", "#222")
svg += T(led_x + 30, (led_anode_y + led_cathode_y)//2 + 4, "IR LED", 9, "start", "#888")
svg += T(led_x + 30, (led_anode_y + led_cathode_y)//2 + 16, "940nm", 9, "start", "#888")

# Anode label, Cathode label
svg += T(led_x + 8, led_anode_y - 2, "A", 8, "start", "#888")
svg += T(led_x + 16, led_cathode_y + 4, "K", 8, "start", "#888")

# ── R2: 47Ω above LED ────────────────────────────────────────────────────
r2_x = led_x
r2_top = led_anode_y - 70
r2_bot = led_anode_y - 15

svg += zigzag_v(r2_x, r2_top, r2_bot)
svg += T(r2_x + 14, (r2_top + r2_bot)//2 - 5, "R2", 11, "start", "#222", "bold")
svg += T(r2_x + 14, (r2_top + r2_bot)//2 + 9, "47Ω", 10, "start", "#222")

# +5V above R2
svg += L(r2_x, r2_top - 15, r2_x, r2_top)
svg += pwr5v(r2_x, r2_top - 27)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION LABELS with dashed boxes
# ═══════════════════════════════════════════════════════════════════════════
# IR Receiver section box
svg += f'<rect x="780" y="100" width="280" height="230" fill="none" stroke="#0066aa" stroke-width="1" stroke-dasharray="6,4" rx="8"/>\n'
svg += T(920, 118, "IR RECEIVER", 12, "middle", "#0066aa", "bold")

# IR Transmitter section box
svg += f'<rect x="780" y="420" width="280" height="290" fill="none" stroke="#cc6600" stroke-width="1" stroke-dasharray="6,4" rx="8"/>\n'
svg += T(920, 438, "IR LED TRANSMITTER", 12, "middle", "#cc6600", "bold")

# ═══════════════════════════════════════════════════════════════════════════
# CURRENT FLOW & CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════
svg += T(r2_x + 50, r2_top + 10, "I = (5 - 1.2 - 0.2) / 47", 9, "start", "#888")
svg += T(r2_x + 50, r2_top + 22, "≈ 76 mA (peak)", 9, "start", "#888")

svg += T(r3_left - 5, r3_y + 30, "I_base = (3.3 - 0.7) / 1k", 9, "end", "#888")
svg += T(r3_left - 5, r3_y + 42, "≈ 2.6 mA", 9, "end", "#888")

# ═══════════════════════════════════════════════════════════════════════════
# WIRING TABLE — bottom
# ═══════════════════════════════════════════════════════════════════════════
tbl_x = 30
tbl_y = 750

svg += f'<rect x="{tbl_x}" y="{tbl_y}" width="650" height="220" fill="#fafaf0" stroke="#222" stroke-width="1" rx="3"/>\n'
svg += T(tbl_x + 325, tbl_y + 20, "CONNECTION TABLE", 14, "middle", "#222", "bold")

# Table header
thy = tbl_y + 40
svg += L(tbl_x + 10, thy + 5, tbl_x + 640, thy + 5, w=1)
svg += T(tbl_x + 20, thy, "FROM", 10, "start", "#222", "bold")
svg += T(tbl_x + 180, thy, "TO", 10, "start", "#222", "bold")
svg += T(tbl_x + 400, thy, "WIRE/NOTE", 10, "start", "#222", "bold")

rows = [
    ("PB6 (J2 pin 7)", "TSOP13438 pin 1 (OUT)",   "Direct wire — IR input signal"),
    ("PB7 (J2 pin 6)", "R3 (1kΩ) → Q1 Base",      "38kHz PWM output to transistor"),
    ("+5V (J3 pin 1)", "R1 (100Ω) → TSOP pin 3 (VS)", "Filtered supply for receiver"),
    ("+5V (J3 pin 1)", "R2 (47Ω) → D1 Anode",      "LED supply (through current limiter)"),
    ("TSOP pin 2 (GND)", "GND (J3 pin 2)",          "Receiver ground"),
    ("Q1 Emitter",     "GND (J3 pin 2)",            "Transistor ground"),
    ("C1+ (4.7µF)",    "TSOP VS rail (after R1)",   "Bypass capacitor, + side"),
    ("C1− (4.7µF)",    "GND (TSOP pin 2 rail)",     "Bypass capacitor, − side"),
    ("D1 Cathode",     "Q1 Collector",               "LED driven by transistor switch"),
    ("PA0, PA1",       "USB (built-in on LaunchPad)", "UART0 — serial terminal 115200 baud"),
]

for i, (fr, to, note) in enumerate(rows):
    ry = thy + 20 + i * 17
    svg += T(tbl_x + 20, ry, fr, 10, "start", "#333")
    svg += T(tbl_x + 180, ry, to, 10, "start", "#333")
    svg += T(tbl_x + 400, ry, note, 9, "start", "#666")

# ═══════════════════════════════════════════════════════════════════════════
# COMPONENT LIST — bottom right
# ═══════════════════════════════════════════════════════════════════════════
bom_x = 720
bom_y = 750

svg += f'<rect x="{bom_x}" y="{bom_y}" width="350" height="220" fill="#fafaf0" stroke="#222" stroke-width="1" rx="3"/>\n'
svg += T(bom_x + 175, bom_y + 20, "BILL OF MATERIALS", 14, "middle", "#222", "bold")

bom = [
    ("U1", "TM4C123GXL LaunchPad"),
    ("U2", "TSOP13438  (38kHz IR receiver)"),
    ("D1", "IR333-A    (940nm IR LED)"),
    ("Q1", "2N2222     (NPN transistor, TO-92)"),
    ("R1", "100Ω  ¼W  (TSOP supply filter)"),
    ("R2", "47Ω   ¼W  (LED current limiter)"),
    ("R3", "1kΩ   ¼W  (Base drive resistor)"),
    ("C1", "4.7µF 16V  (Electrolytic, polarized)"),
]

svg += L(bom_x + 10, bom_y + 30, bom_x + 340, bom_y + 30, w=1)
for i, (ref, desc) in enumerate(bom):
    ry = bom_y + 47 + i * 20
    svg += T(bom_x + 20, ry, ref, 11, "start", "#0066aa", "bold")
    svg += T(bom_x + 60, ry, desc, 10, "start", "#333")

# ═══════════════════════════════════════════════════════════════════════════
# PINOUT NOTES
# ═══════════════════════════════════════════════════════════════════════════
# 2N2222 pinout diagram
svg += T(1100, 580, "2N2222 Pinout (TO-92)", 10, "middle", "#222", "bold")
svg += T(1100, 594, "flat side facing you:", 9, "middle", "#666")
svg += f'<rect x="1060" y="600" width="80" height="30" fill="#f0f0f0" stroke="#222" stroke-width="1" rx="2 2 10 10"/>\n'
svg += T(1075, 618, "E", 10, "middle", "#222", "bold")
svg += T(1100, 618, "B", 10, "middle", "#222", "bold")
svg += T(1125, 618, "C", 10, "middle", "#222", "bold")
svg += L(1075, 630, 1075, 640)
svg += L(1100, 630, 1100, 640)
svg += L(1125, 630, 1125, 640)

# TSOP pinout
svg += T(1100, 670, "TSOP13438 Pinout", 10, "middle", "#222", "bold")
svg += T(1100, 684, "(dome facing you):", 9, "middle", "#666")
svg += f'<rect x="1065" y="690" width="70" height="25" fill="#f0f0f0" stroke="#222" stroke-width="1" rx="0 0 8 8"/>\n'
svg += T(1082, 707, "1", 9, "middle", "#222")
svg += T(1100, 707, "2", 9, "middle", "#222")
svg += T(1118, 707, "3", 9, "middle", "#222")
svg += L(1082, 715, 1082, 725)
svg += L(1100, 715, 1100, 725)
svg += L(1118, 715, 1118, 725)
svg += T(1082, 737, "OUT", 8, "middle", "#222")
svg += T(1100, 737, "GND", 8, "middle", "#222")
svg += T(1118, 737, "VS", 8, "middle", "#222")

# IR333-A LED note
svg += T(1100, 460, "IR333-A LED:", 10, "middle", "#222", "bold")
svg += T(1100, 474, "Long lead = Anode (+)", 9, "middle", "#666")
svg += T(1100, 488, "Short lead = Cathode (−)", 9, "middle", "#666")

svg += '</svg>\n'

# Write
out = os.path.join("/home/rupert/Desktop/embedded Projecy/plan", "ir_remote_circuit.svg")
with open(out, 'w') as f:
    f.write(svg)
print(f"Written: {out}")
print(f"Size: {os.path.getsize(out)} bytes")
print("Open in Firefox/Chrome to view")
