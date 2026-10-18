"""Design tokens shared by the app.

Adapted from the Session 3 gold stock-transfer monitor. The same three fixed
mappings are kept everywhere:
  entity -> hue                    (one colour per country on every panel)
  epistemic status -> line style   (solid = reported, dashed = estimated)
  data class -> mark               (lines = levels / cumulative totals,
                                    bars = period changes)
"""

PAPER = "#fbfbf8"
INK   = "#1c1c18"
FAINT = "#8c8c84"
GHOST = "#d9d9d2"
GOLD  = "#a3780a"   # reserved for the price of gold itself
SELL  = "#9a9a92"   # net selling months (neutral, not alarm-red)

# One colour per central bank. The five largest movers get strong hues;
# everyone else shares a muted set so the big stories stand out.
HUES = {
    "China":       "#b3392e",
    "Poland":      "#c25e00",
    "Turkey":      "#8e4a8b",
    "India":       "#c98a1b",
    "Russia":      "#2e5fa3",
    "Iraq":        "#3f8a7a",
    "Kazakhstan":  "#6b8e3d",
    "Uzbekistan":  "#4f7f9e",
    "Czechia":     "#9e6b4f",
    "Singapore":   "#7a6aa8",
    "Thailand":    "#a85a6a",
    "Qatar":       "#5a8a5a",
    "Hungary":     "#8a7a4f",
    "Serbia":      "#6a6a8a",
    "Philippines": "#5b6b7a",
}
REST = "#b9b9b0"

def hue(entity: str) -> str:
    return HUES.get(entity, REST)

DASH = "dash"   # estimated / inferred series

# Political demand shocks, drawn as vertical rules on every time axis
EVENTS = [
    ("2022-02-28", "reserve freeze"),
    ("2022-06-26", "G7 ban"),
    ("2025-06-13", "Iran war"),
    ("2025-11-01", "CBR sells"),
    ("2026-05-15", "escalation"),
]
