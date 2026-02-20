# ============================================================
# DISCLAIMER / READ BEFORE RUNNING
# ============================================================
# This script simulates keyboard inputs only. It does NOT read game memory,
# detect screen state, or verify menus. It will blindly press keys based on
# hard-coded assumptions.
#
# If the game/menu state is not EXACTLY as expected, inputs can desync and may
# cause unintended purchases, item loss, or other unwanted actions.
#
# This script runs for a calculated number of cycles based on your current Gil.
# You must keep FF8 focused while it runs (do not alt-tab).
#
# By running this script, you accept full responsibility for the outcome.
# If you are not comfortable reviewing and modifying Python code, do not use it.
# ============================================================

# ============================================================
# REQUIRED SETUP (before running)
# ============================================================
# 1) Item menu: Page 1 must be COMPLETELY empty (keeps item ordering consistent).
# 2) Open: Call Shop → Esthar Shop!!! → Buy menu.
# 3) In the Buy list, place the cursor on "Potion".
# 4) Keep FF8 focused while running (do not alt-tab). Borderless Windowed is recommended.
# ============================================================

import time
import math
import re
from datetime import datetime, timedelta

import pydirectinput as pdi

# ----------------------------
# CONFIG
# ----------------------------
MAX_GIL = 99_999_999
PROFIT_PER_CYCLE = 352_500
SECONDS_PER_CYCLE = 17

FOCUS_GRACE_SECONDS = 5  # time to click back into FF8 after starting script

MIN_START_GIL = 210_000  # required to buy 100x Cottages + 100x Tents per cycle

# ----------------------------
# LOGGING HELPERS (alignment)
# ----------------------------
label_w = 26  # one place to control alignment

def log_line(label: str, value: str = "") -> None:
    print(f"{label:<{label_w}} {value}")

def format_eta_error(td) -> str:
    """
    Always-positive error in M:SS.ffffff plus "early"/"late"/"on time".
    Examples:
      5:02.230000 early
      0:07.615904 late
      0:00.000000 on time
    """
    total = td.total_seconds()

    if total == 0:
        return "0:00.000000 on time"

    status = "late" if total > 0 else "early"

    secs = abs(total)
    minutes = int(secs // 60)
    rem = secs - (minutes * 60)  # remaining seconds (with fractional part)

    whole_seconds = int(rem)
    micro = int(round((rem - whole_seconds) * 1_000_000))

    # handle rare rounding case where micro becomes 1_000_000
    if micro == 1_000_000:
        whole_seconds += 1
        micro = 0
        if whole_seconds == 60:
            minutes += 1
            whole_seconds = 0

    return f"{minutes}:{whole_seconds:02d}.{micro:06d} {status}"

# ----------------------------
# HELPERS (input parsing)
# ----------------------------
def parse_gil_input(s: str) -> int:
    """
    Accepts:
      - "210000", "210,000"
      - "210k", "210K"
      - "0.21m", "30m", "30M"
    Returns gil as int (not yet rounded).
    """
    s = s.strip().lower().replace(",", "")
    m = re.fullmatch(r"(\d+(\.\d+)?)([km]?)", s)
    if not m:
        raise ValueError("Invalid format")

    value = float(m.group(1))
    suffix = m.group(3)

    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000

    return int(value)

def round_up_safe(gil: int) -> int:
    """
    Round UP to a step based on magnitude (safe: won't cause overshoot).
    """
    if gil < 1_000_000:
        step = 10_000        # 10k precision for small amounts
    elif gil < 10_000_000:
        step = 100_000       # 100k precision mid-range
    else:
        step = 1_000_000     # 1M precision for large amounts

    return int(math.ceil(gil / step) * step)

def get_current_gil_raw(max_gil: int) -> int:
    """
    Returns the raw parsed gil (clamped to max_gil), with NO rounding.
    This prevents the 205k -> 210k rounding bug from bypassing min gil checks.
    """
    while True:
        raw = input("Current gil? (examples: 210000, 210k, 0.21m, 30m): ")
        try:
            gil = parse_gil_input(raw)
            if gil < 0:
                print("Enter a non-negative amount.")
                continue
            return min(gil, max_gil)
        except ValueError:
            print("Invalid input. Examples: 210000, 210k, 0.21m, 30m")

# ----------------------------
# START LOGGING
# ----------------------------
start_time = datetime.now().astimezone()
print("==========================================")
print("Mega Potion Farming Script Started")
log_line("Start Time:", start_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
print("==========================================")

# ----------------------------
# INPUT + VALIDATION + CYCLE CALC
# ----------------------------
entered_gil = get_current_gil_raw(MAX_GIL)

# Validate BEFORE rounding (prevents the 205k -> 210k bug)
if entered_gil < MIN_START_GIL:
    raise ValueError(
        f"Insufficient gil: You entered {entered_gil:,} gil. "
        f"You need at least {MIN_START_GIL:,} gil to purchase 100x Cottages and 100x Tents."
    )

# Now apply safe rounding for cycle math (prevents overshoot)
current_gil = min(round_up_safe(entered_gil), MAX_GIL)

remaining = MAX_GIL - current_gil
cycles = remaining // PROFIT_PER_CYCLE  # floor division => rounds DOWN (no extra cycles)

estimated_duration = timedelta(seconds=cycles * SECONDS_PER_CYCLE)
estimated_finish_time = start_time + estimated_duration

estimated_end_gil = current_gil + cycles * PROFIT_PER_CYCLE
estimated_end_gil = min(estimated_end_gil, MAX_GIL)
potential_short = MAX_GIL - estimated_end_gil

print("------------------------------------------")
log_line("Input (rounded up safely):", f"{current_gil:,} gil")
log_line("Remaining to cap:", f"{remaining:,} gil")
log_line("Profit per cycle:", f"{PROFIT_PER_CYCLE:,} gil")
log_line("Cycles to run (floor):", str(cycles))
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish time:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Estimated end gil:", f"{estimated_end_gil:,} gil")
log_line("Potential short of cap:", f"{potential_short:,} gil")
print("------------------------------------------")

if cycles <= 0:
    print("No cycles needed (you're at or too close to the gil cap). Exiting.")
    raise SystemExit

print(f"Click into FF8 now. Starting in {FOCUS_GRACE_SECONDS} seconds...")
time.sleep(FOCUS_GRACE_SECONDS)

# ============================================================
# MAIN LOOP — RUN CALCULATED CYCLES
# ============================================================
for i in range(cycles):
    # Optional progress log
    log_line("Cycle:", f"{i+1}/{cycles}")

    # # ============================================================
    # # PHASE 1 — BUY TENTS & COTTAGES
    # # ============================================================

    # # Navigate to Tents & Cottages
    # pdi.press('right')
    # pdi.press('up')
    # pdi.press('up')
    # pdi.press('enter')

    # # Buy 100 Cottages
    # pdi.keyDown('up')
    # time.sleep(1.01)
    # pdi.keyUp('up')
    # pdi.press('enter')
    # pdi.press('up')
    # pdi.press('enter')

    # # Buy 100 Tents
    # pdi.keyDown('up')
    # time.sleep(1.01)
    # pdi.keyUp('up')
    # pdi.press('enter')

    # # Exit Buy menu
    # pdi.press('c')
    # pdi.press('c')
    # time.sleep(0.4)

    # # ============================================================
    # # PHASE 2 — REFINE ITEMS → MEGA POTIONS
    # # ============================================================

    # # Navigate to Recov Med-RF
    # pdi.press('c')
    # pdi.press('right')
    # pdi.press('up')
    # pdi.press('enter')
    # time.sleep(0.4)
    # pdi.press('enter')

    # # Refine Tents → 25x Mega Potions
    # pdi.keyDown('down')
    # time.sleep(0.3)
    # pdi.keyUp('down')
    # pdi.press('enter')
    # pdi.press('down')
    # pdi.press('enter')

    # # Refine Cottages → 75x Mega Potions
    # pdi.keyDown('down')
    # time.sleep(0.5)
    # pdi.keyUp('down')
    # pdi.press('enter')

    # # Exit Recov Med-RF
    # pdi.press('c')
    # time.sleep(0.4)

    # # ============================================================
    # # PHASE 3 — SELL MEGA POTIONS
    # # ============================================================

    # # Navigate to Call Shop → Esthar Shop!!!
    # pdi.press('left')
    # pdi.press('down')
    # pdi.press('enter')
    # pdi.press('enter')
    # time.sleep(0.4)

    # # Move to Mega Potions
    # pdi.press('right')
    # pdi.press('enter')
    # pdi.press('down')
    # pdi.press('down')
    # pdi.press('enter')

    # # Sell 75x Mega Potions
    # pdi.keyDown('up')
    # time.sleep(0.8)
    # pdi.keyUp('up')
    # pdi.press('enter')

    # # Exit Sell
    # pdi.press('c')
    # pdi.press('left')
    # pdi.press('enter')

# ----------------------------
# FINISH LOGGING
# ----------------------------
end_time = datetime.now().astimezone()
actual_duration = end_time - start_time
delta = end_time - estimated_finish_time  # + = finished later than ETA; - = earlier

print("==========================================")
print("Mega Potion Farming Script Finished")
log_line("Finish Time:", end_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Actual duration:", str(actual_duration))
print("------------------------------------------")
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish time:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Estimate error:", format_eta_error(delta))
print("==========================================")