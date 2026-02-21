# ============================================================
# gil_farm.py — v1.0 (2026-02-21)
# ============================================================

# ============================================================
# DISCLAIMER / READ BEFORE RUNNING
# ============================================================
# This script simulates keyboard inputs only. It does NOT read game memory,
# detect screen state, or verify menus. It will blindly press keys based on
# hard-coded assumptions.
#
# If the game/menu state is not EXACTLY as expected, inputs can desync and may
# cause unintended purchases, item loss, or other unwanted actions.
# You must monitor the script while running and stop it if it desynchronizes.
#
# Stop execution:
# - Press CTRL + C in the terminal, or
# - Close the terminal / end the Python process.
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
#
# Runtime prompts:
#   Gil — Enter current gil. The script calculates cycles to reach 99,999,999 gil:
#           cycles = ceil((99,999,999 - current_gil) / 352,500)
#         Minimum 210,000 gil required (cost of 100x Cottages + 100x Tents).
#
# Script structure (each cycle):
#   Phase 1: Buy 100x Cottages + 100x Tents from Esthar Shop!!!.
#   Phase 2: Refine via Recov Med-RF → 25x Mega Potions (Tents) + 75x Mega Potions (Cottages).
#   Phase 3: Sell 75x Mega Potions at Esthar Shop!!! (+352,500 gil profit per cycle).
# ============================================================

import time
import math
import re
from datetime import datetime, timedelta

import pydirectinput as pdi

# ----------------------------
# CONFIG
# ----------------------------
pdi.PAUSE = 0.025 # Remove built-in delay
MAX_GIL = 99_999_999
PROFIT_PER_CYCLE = 352_500
SECONDS_PER_CYCLE = 13.51
FOCUS_GRACE_SECONDS = 5  # time to click back into FF8 after starting script
MIN_START_GIL = 210_000  # required to buy 100x Cottages + 100x Tents per cycle

# ----------------------------
# LOGGING HELPERS (alignment)
# ----------------------------
LABEL_W = 26  # one place to control alignment


def log_line(label: str, value: str = "") -> None:
    print(f"{label:<{LABEL_W}} {value}")


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
    rem = secs - (minutes * 60)

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


def format_elapsed(td: timedelta) -> str:
    """
    Format elapsed time as H:MM:SS.ffffff
    """
    total = td.total_seconds()
    if total < 0:
        total = 0.0

    hours = int(total // 3600)
    rem = total - hours * 3600
    minutes = int(rem // 60)
    rem = rem - minutes * 60

    whole_seconds = int(rem)
    micro = int(round((rem - whole_seconds) * 1_000_000))

    # handle rare rounding case where micro becomes 1_000_000
    if micro == 1_000_000:
        whole_seconds += 1
        micro = 0
        if whole_seconds == 60:
            minutes += 1
            whole_seconds = 0
        if minutes == 60:
            hours += 1
            minutes = 0

    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{micro:06d}"


# ----------------------------
# HELPERS (input parsing)
# ----------------------------
def parse_gil_input(s: str) -> int:
    """
    Accepts:
      - "210000", "210,000"
      - "210k", "210K"
      - "0.21m", "30m", "30M"
    Returns gil as int.
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


def get_current_gil_raw(max_gil: int) -> int:
    """
    Returns the raw parsed gil (clamped to max_gil), with NO rounding.
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

if entered_gil < MIN_START_GIL:
    raise ValueError(
        f"Insufficient gil: You entered {entered_gil:,} gil. "
        f"You need at least {MIN_START_GIL:,} gil to purchase 100x Cottages and 100x Tents."
    )

current_gil = entered_gil
remaining = MAX_GIL - current_gil

# Round UP to the nearest whole cycle (overshoot is allowed)
cycles = math.ceil(remaining / PROFIT_PER_CYCLE)

estimated_duration = timedelta(seconds=cycles * SECONDS_PER_CYCLE)
estimated_finish_time = start_time + estimated_duration

estimated_end_gil = current_gil + cycles * PROFIT_PER_CYCLE
projected_over_cap = max(0, estimated_end_gil - MAX_GIL)

print("------------------------------------------")
log_line("Input:", f"{current_gil:,} gil")
log_line("Remaining to cap:", f"{remaining:,} gil")
log_line("Profit per cycle:", f"{PROFIT_PER_CYCLE:,} gil")
log_line("Cycles to run:", str(cycles))
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish time:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Projected end gil:", f"{estimated_end_gil:,} gil")
log_line("Projected over cap:", f"{projected_over_cap:,} gil")
print("------------------------------------------")

if cycles <= 0:
    print("No cycles needed (you're at or above the gil cap). Exiting.")
    raise SystemExit

print(f"Click into FF8 now. Starting in {FOCUS_GRACE_SECONDS} seconds...")
time.sleep(FOCUS_GRACE_SECONDS)

# ============================================================
# MAIN LOOP — RUN CALCULATED CYCLES
# ============================================================
run_start_monotonic = time.perf_counter()

for cycle_num in range(1, cycles + 1):
    cycle_start = time.perf_counter()

    # ============================================================
    # PHASE 1 — BUY TENTS & COTTAGES
    # ============================================================

    # Navigate to Tents & Cottages
    pdi.press("right")
    time.sleep(0.2)
    pdi.press("up")
    pdi.press("up")
    pdi.press("enter")
    time.sleep(0.15)

    # Buy 100 Cottages
    for i in range(10):
        pdi.press("up")
    pdi.press("enter")
    pdi.press("up")
    pdi.press("enter")
    time.sleep(0.15)

    # Buy 100 Tents
    for i in range(10):
        pdi.press("up")
    pdi.press("enter")

    # Exit Buy menu
    pdi.press("c")
    time.sleep(0.4)
    pdi.press("c")
    time.sleep(0.65)

    # ============================================================
    # PHASE 2 — REFINE ITEMS → MEGA POTIONS
    # ============================================================

    # Navigate to Recov Med-RF
    pdi.press("c")
    time.sleep(0.4)
    pdi.press("right")
    time.sleep(0.2)
    pdi.press("up")
    pdi.press("enter")
    time.sleep(0.65)
    pdi.press("enter")
    time.sleep(0.2)

    # Refine Tents → 25x Mega Potions
    for i in range(3):
        pdi.press("down")
    pdi.press("enter")
    time.sleep(0.1)
    pdi.press("down")
    pdi.press("enter")
    time.sleep(0.2)

    # Refine Cottages → 75x Mega Potions
    for i in range(5):
        pdi.press("down")
    pdi.press("enter")
    time.sleep(0.1)

    # Exit Recov Med-RF
    pdi.press("c")
    time.sleep(0.65)

    # ============================================================
    # PHASE 3 — SELL MEGA POTIONS
    # ============================================================

    # Navigate to Call Shop → Esthar Shop!!!
    pdi.press("left")
    time.sleep(0.2)
    pdi.press("down")
    pdi.press("enter")
    time.sleep(0.4)
    pdi.press("enter")
    time.sleep(0.65)

    # Move to Mega Potions
    pdi.press("right")
    pdi.press("enter")
    time.sleep(0.4)
    pdi.press("down")
    pdi.press("down")
    pdi.press("enter")
    time.sleep(0.2)

    # Sell 75x Mega Potions
    for i in range(8):
        pdi.press("up")
    pdi.press("enter")

    # Exit Sell
    pdi.press("c")
    time.sleep(0.4)
    pdi.press("left")
    pdi.press("enter")
    time.sleep(0.4)

    # ----------------------------
    # PER-CYCLE LOGGING (one line)
    # ----------------------------
    cycle_end = time.perf_counter()
    cycle_seconds = cycle_end - cycle_start
    elapsed = timedelta(seconds=(cycle_end - run_start_monotonic))

    print(
        f"Cycle: {cycle_num}/{cycles} ({cycle_seconds:.2f}s) | "
        f"Elapsed: {format_elapsed(elapsed)}"
    )

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