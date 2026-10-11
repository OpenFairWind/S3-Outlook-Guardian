"""Circuit definition of the Outlook Guardian board.

Single source for the schematic generator (gen_sch.py). Every part lists its
symbol, value, footprint, position on the schematic sheet and the net of each
pin. A pin mapped to NC gets a no-connect flag.
"""

NC = None

R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
L0805 = "Inductor_SMD:L_0805_2012Metric"
PHOENIX2 = "Connector_Phoenix_MC:PhoenixContact_MCV_1,5_2-G-3.81_1x02_P3.81mm_Vertical"
PHOENIX4 = "Connector_Phoenix_MC:PhoenixContact_MCV_1,5_4-G-3.81_1x04_P3.81mm_Vertical"
ESD = ("Device:D_TVS", "ESD5451N", "Diode_SMD:D_0402_1005Metric")

PARTS = []
BLOCKS = []


def part(ref, sym, value, fp, x, y, pins, mpn="", rot=None):
    PARTS.append(dict(ref=ref, sym=sym, value=value, fp=fp, x=x, y=y, pins=pins, mpn=mpn, rot=rot))


def two(ref, sym, value, fp, x, y, n1, n2, mpn=""):
    part(ref, sym, value, fp, x, y, {"1": n1, "2": n2}, mpn)


def column(x, y, rows, dy=7.62):
    """Stack two-pin parts: rows of (ref, sym, value, fp, net1, net2[, mpn])."""
    for i, row in enumerate(rows):
        two(row[0], row[1], row[2], row[3], x, y + i * dy, row[4], row[5], row[6] if len(row) > 6 else "")


def block(title, x0, y0, x1, y1):
    BLOCKS.append((title, x0, y0, x1, y1))


R, C, CP, L, FB, D, DS, LED, PF = (
    "Device:R", "Device:C", "Device:C_Polarized", "Device:L", "Device:FerriteBead",
    "Device:D_TVS", "Device:D_Schottky", "Device:LED", "Device:Polyfuse",
)

# ----------------------------------------------------------------------------
block("Power input 9 to 32 V and 5 V buck converter", 12, 14, 298, 88)
part("J1", "Connector_Generic:Conn_01x04", "NMEA 2000 / power", PHOENIX4, 40, 45,
     {"1": "GND", "2": "VIN_RAW", "3": "CAN_H", "4": "CAN_L"}, "Phoenix MCV 1,5/4-G-3,81")
column(95, 30, [
    ("F1", PF, "1.1A/33V PTC", "Fuse:Fuse_1812_4532Metric", "VIN_RAW", "VIN_FUSED", "1812L110/33MR"),
    ("D1", D, "SMBJ33CA", "Diode_SMD:D_SMB", "VIN_FUSED", "GND", "SMBJ33CA"),
    ("D2", DS, "SS34", "Diode_SMD:D_SMA", "VIN_PROT", "VIN_FUSED", "SS34"),
    ("C1", C, "10uF/50V", C1206, "VIN_PROT", "GND"),
    ("L1", L, "10uH/1.5A", "Inductor_SMD:L_Bourns-SRN4018", "VIN_PROT", "VIN_BUCK", "SRN4018-100M"),
])
column(150, 30, [
    ("C2", C, "10uF/50V", C1206, "VIN_BUCK", "GND"),
    ("C3", C, "10uF/50V", C1206, "VIN_BUCK", "GND"),
    ("C4", C, "100nF/50V", C0603, "VIN_BUCK", "GND"),
    ("C5", CP, "220uF/50V", "Capacitor_SMD:CP_Elec_10x10.5", "VIN_BUCK", "GND"),
])
part("U1", "Regulator_Switching:XL1509-5.0", "XL1509-5.0E1", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 205, 42,
     {"1": "VIN_BUCK", "2": "SW", "3": "+5V", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND"},
     "XL1509-5.0E1")
column(262, 30, [
    ("D3", DS, "SS34", "Diode_SMD:D_SMA", "SW", "GND", "SS34"),
    ("L2", L, "47uH/3A", "Inductor_SMD:L_Bourns_SRR1260", "SW", "+5V", "SRR1260-470M"),
    ("C6", C, "47uF/10V", C1206, "+5V", "GND"),
    ("C7", C, "47uF/10V", C1206, "+5V", "GND"),
    ("C8", CP, "220uF/10V", "Capacitor_SMD:CP_Elec_6.3x7.7", "+5V", "GND"),
])

# ----------------------------------------------------------------------------
block("USB (native ESP32-S3 USB, bench power)", 12, 93, 150, 165)
part("J2", "Connector:USB_B_Micro", "USB Micro-B", "Connector_USB:USB_Micro-B_Wuerth_614105150721_Vertical",
     32, 122, {"1": "USB_VBUS", "2": "USB_DM", "3": "USB_DP", "4": NC, "5": "GND", "SH": "GND"},
     "Wuerth 614105150721")
part("U3", "Power_Protection:USBLC6-2SC6", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", 85, 122,
     {"1": "USB_DM", "6": "USB_DM", "3": "USB_DP", "4": "USB_DP", "5": "USB_VBUS", "2": "GND"}, "USBLC6-2SC6")
column(118, 145, [
    ("F2", PF, "1A/6V PTC", "Fuse:Fuse_1206_3216Metric", "USB_VBUS", "USB_5V", "BSMD1206-100-6V"),
    ("D4", DS, "B5819W", "Diode_SMD:D_SOD-123", "+5V", "USB_5V", "B5819W"),
])

# ----------------------------------------------------------------------------
block("3.3 V regulator and status LEDs", 155, 93, 298, 165)
part("U2", "Regulator_Linear:AZ1117-3.3", "AZ1117C-3.3", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", 185, 112,
     {"3": "+5V", "2": "+3V3", "1": "GND"}, "AZ1117CH-3.3TRG1")
column(185, 135, [
    ("C9", C, "10uF/16V", C0805, "+5V", "GND"),
    ("C10", C, "22uF/10V", C0805, "+3V3", "GND"),
    ("C11", C, "100nF", C0603, "+3V3", "GND"),
])
column(245, 135, [
    ("R1", R, "2k", R0603, "+3V3", "PWR_LED_A"),
    ("D7", LED, "Green", "LED_SMD:LED_0603_1608Metric", "GND", "PWR_LED_A"),
    ("C15", C, "100nF", C0603, "+3V3", "GND"),
])
part("D6", "LED:SK6812MINI", "SK6812MINI", "LED_SMD:LED_SK6812MINI_PLCC4_3.5x3.5mm_P1.75mm", 250, 112,
     {"4": "+3V3", "2": "GND", "3": "RGB_DIN", "1": NC}, "SK6812MINI")

# ----------------------------------------------------------------------------
block("I2S audio amplifier", 303, 14, 408, 165)
part("U5", "Audio:MAX98357A", "MAX98357AETE+T", "Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm",
     352, 48,
     {"1": "I2S_DIN", "16": "I2S_BCLK", "14": "I2S_LRC", "2": NC, "4": "AMP_SD",
      "7": "+5V", "8": "+5V", "3": "GND", "11": "GND", "15": "GND", "17": "GND",
      "9": "AMP_OUTP", "10": "AMP_OUTN", "5": NC, "6": NC, "12": NC, "13": NC},
     "MAX98357AETE+T")
column(355, 82, [
    ("R3", R, "1M", R0603, "+5V", "AMP_SD"),
    ("C16", C, "10uF/16V", C0805, "+5V", "GND"),
    ("C17", C, "100nF", C0603, "+5V", "GND"),
    ("FB1", FB, "220R/2A", L0805, "AMP_OUTP", "SPK_P", "BLM21PG221SN1D"),
    ("FB2", FB, "220R/2A", L0805, "AMP_OUTN", "SPK_N", "BLM21PG221SN1D"),
    ("C18", C, "220pF", C0603, "SPK_P", "GND"),
    ("C19", C, "220pF", C0603, "SPK_N", "GND"),
])
part("J4", "Connector_Generic:Conn_01x02", "Speaker", PHOENIX2, 352, 147,
     {"1": "SPK_P", "2": "SPK_N"}, "Phoenix MCV 1,5/2-G-3,81")

# ----------------------------------------------------------------------------
block("ESP32-S3-WROOM-1-N16R8", 12, 170, 150, 285)
part("U4", "RF_Module:ESP32-S3-WROOM-1", "ESP32-S3-WROOM-1-N16R8", "OutlookGuardian:ESP32-S3-WROOM-1_EdgeAntenna", 52, 224,
     {"1": "GND", "40": "GND", "41": "GND", "2": "+3V3", "3": "EN",
      "4": "I2S_LRC", "5": "I2S_BCLK", "6": "I2S_DIN", "7": "IO7",
      "8": "BTN_ACK", "9": "BTN_SNOOZE", "10": "CAN_TX", "11": "CAN_RX",
      "12": "SDA", "17": "SCL", "13": "USB_DM", "14": "USB_DP",
      "15": NC, "16": NC, "18": "IO10", "19": "IO11", "20": "IO12", "21": "IO13", "22": "IO14",
      "23": "IO21", "24": NC, "25": "RGB_DIN", "26": NC, "27": "IO0",
      "28": NC, "29": NC, "30": NC, "31": NC,
      "32": "MTCK", "33": "MTDO", "34": "MTDI", "35": "MTMS",
      "36": "RXD0", "37": "TXD0", "38": "IO2", "39": "IO1"},
     "ESP32-S3-WROOM-1-N16R8")
column(120, 182, [
    ("C12", C, "22uF/10V", C0805, "+3V3", "GND"),
    ("C13", C, "100nF", C0603, "+3V3", "GND"),
    ("R2", R, "10k", R0603, "+3V3", "EN"),
    ("C14", C, "1uF", C0603, "EN", "GND"),
    ("SW1", "Switch:SW_Push", "BOOT", "Button_Switch_SMD:SW_SPST_TL3342", "GND", "IO0", "TL3342F160QG"),
    ("SW2", "Switch:SW_Push", "RESET", "Button_Switch_SMD:SW_SPST_TL3342", "GND", "EN", "TL3342F160QG"),
])
part("J6", "Connector_Generic:Conn_01x02", "EN / IO0", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
     120, 236, {"1": "EN", "2": "IO0"})
TP = "TestPoint:TestPoint_Pad_D1.5mm"
for i, (name, net) in enumerate([("TXD0", "TXD0"), ("RXD0", "RXD0"), ("+5V", "+5V"), ("+3V3", "+3V3"), ("GND", "GND")]):
    part("TP%d" % (i + 1), "Connector:TestPoint", name, TP, 100 + i * 10, 262, {"1": net})

# ----------------------------------------------------------------------------
block("GPIO header", 153, 170, 205, 285)
part("J3", "Connector_Generic:Conn_02x10_Odd_Even", "GPIO", "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical",
     178, 215,
     {"1": "+3V3", "2": "IO21", "3": "GND", "4": "IO1", "5": "IO11", "6": "IO2", "7": "IO12", "8": "IO7",
      "9": "IO13", "10": "IO10", "11": "IO14", "12": "GND", "13": "MTDI", "14": "GND", "15": "MTDO",
      "16": "GND", "17": "MTCK", "18": "GND", "19": "MTMS", "20": "+3V3"})
part("H1", "Mechanical:MountingHole", "M3 slot", "OutlookGuardian:MountingSlot_3.2mm_M3_Unplated", 168, 262, {})
part("H2", "Mechanical:MountingHole", "M3 slot", "OutlookGuardian:MountingSlot_3.2mm_M3_Unplated", 190, 262, {})

# ----------------------------------------------------------------------------
block("NMEA 2000 transceiver", 268, 170, 335, 250)
part("U6", "Interface_CAN_LIN:SN65HVD230", "SN65HVD230DR", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 290, 195,
     {"1": "CAN_TX", "4": "CAN_RX", "5": NC, "8": "CAN_RS", "3": "+3V3", "2": "GND", "7": "CAN_H", "6": "CAN_L"},
     "SN65HVD230DR")
column(288, 220, [
    ("C20", C, "100nF", C0603, "+3V3", "GND"),
    ("R4", R, "10k", R0603, "CAN_RS", "GND"),
    ("R5", R, "10k", R0603, "+3V3", "CAN_TX"),
])
part("D5", "Power_Protection:NUP2105L", "SM24CANB", "Package_TO_SOT_SMD:SOT-23", 322, 228,
     {"1": "CAN_H", "2": "CAN_L", "3": "GND"}, "SM24CANB-02HTG")

# ----------------------------------------------------------------------------
block("Display socket", 208, 170, 265, 285)
block("Button inputs", 338, 170, 408, 250)
part("J5", "Connector_Generic:Conn_01x04", "Display", "Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical",
     238, 185, {"1": "GND", "2": "DISP_3V3", "3": "DISP_SCL", "4": "DISP_SDA"})
part("J7", "Connector_Generic:Conn_01x02", "Acknowledge", PHOENIX2, 358, 183,
     {"1": "ACK_IN", "2": "GND"}, "Phoenix MCV 1,5/2-G-3,81")
part("J8", "Connector_Generic:Conn_01x02", "Snooze", PHOENIX2, 393, 183,
     {"1": "SNOOZE_IN", "2": "GND"}, "Phoenix MCV 1,5/2-G-3,81")
column(237, 202, [
    ("FB3", FB, "600R", L0805, "+3V3", "DISP_3V3", "GZ2012D601TF"),
    ("FB4", FB, "100R", L0805, "SDA", "DISP_SDA", "GZ2012D101TF"),
    ("FB5", FB, "100R", L0805, "SCL", "DISP_SCL", "GZ2012D101TF"),
    ("C21", C, "10uF/16V", C0805, "DISP_3V3", "GND"),
    ("C22", C, "33pF", C0603, "DISP_SDA", "GND"),
    ("C23", C, "33pF", C0603, "DISP_SCL", "GND"),
    ("R6", R, "4.7k", R0603, "+3V3", "SDA"),
    ("R7", R, "4.7k", R0603, "+3V3", "SCL"),
    ("D8", ESD[0], ESD[1], ESD[2], "DISP_SDA", "GND", ESD[1]),
    ("D9", ESD[0], ESD[1], ESD[2], "DISP_SCL", "GND", ESD[1]),
])
column(373, 194, [
    ("R8", R, "10k", R0603, "+3V3", "ACK_IN"),
    ("R9", R, "1k", R0603, "ACK_IN", "BTN_ACK"),
    ("C24", C, "100nF", C0603, "BTN_ACK", "GND"),
    ("D10", ESD[0], ESD[1], ESD[2], "ACK_IN", "GND", ESD[1]),
    ("R10", R, "10k", R0603, "+3V3", "SNOOZE_IN"),
    ("R11", R, "1k", R0603, "SNOOZE_IN", "BTN_SNOOZE"),
    ("C25", C, "100nF", C0603, "BTN_SNOOZE", "GND"),
    ("D11", ESD[0], ESD[1], ESD[2], "SNOOZE_IN", "GND", ESD[1]),
])

# Nets that need a PWR_FLAG to tell ERC they are driven: (net, x, y)
PWR_FLAGS = [("VIN_BUCK", 150, 66), ("+5V", 262, 74)]

POWER_NETS = {"GND": "power:GND", "+5V": "power:+5V", "+3V3": "power:+3V3"}

DATE = "2026-10-11"
REV = "0.1"
NOTES = [
    "GAIN open: 9 dB. SD_MODE through 1M: (L+R)/2.",
    "No CAN termination: the backbone is terminated.",
    "IO35, IO36, IO37 are used by the octal PSRAM.",
    "IO0, IO3, IO45, IO46 are strapping pins.",
]
