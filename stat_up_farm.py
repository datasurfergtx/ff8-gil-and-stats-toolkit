# ==================================================================
# DISCLAIMER / READ BEFORE RUNNING
# ==================================================================
# This script simulates keyboard inputs only. It does NOT read game memory,
# detect screen state, or verify menus. It will blindly press keys based on
# hard-coded assumptions.
#
# If the game/menu state is not EXACTLY as expected, inputs can desync and may
# cause unintended purchases, item loss, or other unwanted actions.
#
# This script runs a fixed number of shop cycles, then performs a final refine.
# You must monitor the script while running and stop it if it desynchronizes.
#
# Stop execution:
# - Press CTRL + C in the terminal, or
# - Close the terminal / end the Python process.
#
# By running this script, you accept full responsibility for the outcome.
# If you are not comfortable reviewing and modifying Python code, do not use it.
# ==================================================================

# ==================================================================
# REQUIRED SETUP (before running)
# ==================================================================
# 1) Item menu: Page 1 must be COMPLETELY empty (keeps item ordering consistent).
# 2) Open: Call Shop → Esthar Pet Shop → Buy menu.
# 3) In the Buy list, place the cursor on "G-Potion".
# 4) Keep FF8 focused while running (do not alt-tab). Borderless Windowed is recommended.
#
# Script structure:
# - Phase 1 (looped): Buy item → Refine into intermediate → Return to shop.
# - Phase 2 (once): Refine accumulated intermediates → Stat Up (Forbid Med-RF).
#
# Stat options (chosen at runtime):
#   HP  → Giant's Ring  → HP Up
#   Str → Power Wrist   → Str Up
#   Vit → Force Armlet  → Vit Up
#   Mag → Hypno Crown   → Mag Up
#
# NOTE: Phase 2 runs ONCE after the loop, which is useful for batching inputs.
# ==================================================================

import time
import re
from datetime import datetime, timedelta

import pydirectinput as pdi

# ----------------------------
# CONFIG
# ----------------------------
pdi.PAUSE = 0.02 # Remove built-in delay
FOCUS_GRACE_SECONDS = 5  # time to click back into FF8 after starting script
CYCLES = 10
ESTIMATED_DURATION_PER_RUN = timedelta(minutes=1, seconds=42)  # placeholder
TOTAL_COST = 15_000_000  # gil required to complete all cycles
MIN_GIL_REQUIRED = TOTAL_COST + 210_000  # reserve 210k for mega potion farm startup

STAT_OPTIONS = {
    "hp":  {"presses": 4, "item": "Giant's Ring",  "stat_up": "HP Up"},
    "str": {"presses": 5, "item": "Power Wrist",   "stat_up": "Str Up"},
    "vit": {"presses": 6, "item": "Force Armlet",  "stat_up": "Vit Up"},
    "mag": {"presses": 7, "item": "Hypno Crown",   "stat_up": "Mag Up"},
}

# ----------------------------
# LOGGING HELPERS (alignment)
# ----------------------------
LABEL_W = 26


def log_line(label: str, value: str = "") -> None:
    print(f"{label:<{LABEL_W}} {value}")


def format_elapsed(td: timedelta) -> str:
    total = td.total_seconds()
    if total < 0:
        total = 0.0

    hours = int(total // 3600)
    rem = total - hours * 3600
    minutes = int(rem // 60)
    rem = rem - minutes * 60

    whole_seconds = int(rem)
    micro = int(round((rem - whole_seconds) * 1_000_000))

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


def format_eta_error(td) -> str:
    total = td.total_seconds()

    if total == 0:
        return "0:00.000000 on time"

    status = "late" if total > 0 else "early"

    secs = abs(total)
    minutes = int(secs // 60)
    rem = secs - (minutes * 60)

    whole_seconds = int(rem)
    micro = int(round((rem - whole_seconds) * 1_000_000))

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


# ----------------------------
# STAT SELECTION
# ----------------------------
print("------------------------------------------")
print("Which stat do you want to farm?")
print("Options: HP, Str, Vit, Mag")
print("------------------------------------------")

while True:
    stat_choice = input("Stat: ").strip().lower()
    if stat_choice in STAT_OPTIONS:
        break
    print("Invalid choice. Enter one of: HP, Str, Vit, Mag")

stat = STAT_OPTIONS[stat_choice]

# ----------------------------
# GIL CHECK (optional)
# ----------------------------
outer_loops = 1

print("------------------------------------------")
print(f"This script requires {TOTAL_COST:,} gil per run (+ 210k reserved).")
print("Press Enter to skip the gil check (runs once).")
print("------------------------------------------")

while True:
    raw = input("Current gil? (examples: 15000000, 15m, 15000k): ").strip()
    if raw == "":
        print("Gil check skipped. Running 1 loop.")
        break
    try:
        current_gil = parse_gil_input(raw)
        if current_gil < 0:
            print("Enter a non-negative amount.")
            continue
        if current_gil < MIN_GIL_REQUIRED:
            raise ValueError(
                f"Insufficient gil: You entered {current_gil:,} gil. "
                f"You need at least {MIN_GIL_REQUIRED:,} gil."
            )
        outer_loops = (current_gil - 210_000) // TOTAL_COST
        total_cost = outer_loops * TOTAL_COST
        remaining_gil = current_gil - total_cost
        log_line("Input:", f"{current_gil:,} gil")
        log_line("Runs:", str(outer_loops))
        log_line("Total cost:", f"{total_cost:,} gil")
        log_line("Gil remaining after:", f"{remaining_gil:,} gil")
        break
    except ValueError as e:
        print(e)

# ----------------------------
# START LOGGING
# ----------------------------
start_time = datetime.now().astimezone()
estimated_duration = ESTIMATED_DURATION_PER_RUN * outer_loops
estimated_finish_time = start_time + estimated_duration

print("==========================================")
print(f"{stat['stat_up']} Farming Script Started")
log_line("Farming:", f"{stat['item']} → {stat['stat_up']}")
log_line("Start Time:", start_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
print("------------------------------------------")
log_line("Runs:", str(outer_loops))
log_line("Cycles per run:", str(CYCLES))
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish time:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
print("==========================================")

print(f"Click into FF8 now. Starting in {FOCUS_GRACE_SECONDS} seconds...")
time.sleep(FOCUS_GRACE_SECONDS)

run_start_monotonic = time.perf_counter()

for run in range(outer_loops):
    if outer_loops > 1:
        print(f"--- Run {run + 1}/{outer_loops} ---")

    # ============================================================
    # PHASE 1 — SHOP + MED-RF LOOP (run 10 cycles)
    # Goal: repeatedly buy Entry Item and convert them into Mid Tier Refinement.
    # ============================================================

    for cycle in range(1, CYCLES + 1):
        cycle_start = time.perf_counter()
        # ------------------------------------------------------------
        # PHASE 1.0 — BUY ITEM
        # Starting state (assumed): Esthar Pet Shop → Buy menu, cursor on "G-Potion"
        # ------------------------------------------------------------

        pdi.press('right')
        time.sleep(0.25)
        for i in range(stat["presses"]):
            pdi.press('down')
        pdi.press('enter')
        time.sleep(0.15)
        for i in range(12):
            pdi.press('up')
        pdi.press('enter')

        # Exit back out of shop menus
        pdi.press('c')
        time.sleep(0.4)
        pdi.press('c')
        time.sleep(0.65)
        pdi.press('c')
        time.sleep(0.4)

        # ------------------------------------------------------------
        # PHASE 1.2 — REFINE ITEM → Mid Tier Refinement (GFAbl Med-RF)
        # ------------------------------------------------------------

        pdi.press('right')
        time.sleep(0.25)
        for i in range(5):
            pdi.press('down')
        pdi.press('enter')
        time.sleep(0.65)
        if run > 0:
            pdi.press('down')
        pdi.press('enter')
        time.sleep(0.15)
        pdi.press('down')
        pdi.press('enter')
        time.sleep(0.15)

        # ------------------------------------------------------------
        # PHASE 1.3 — RETURN TO ESTHAR PET SHOP
        # ------------------------------------------------------------

        pdi.press('c')
        time.sleep(0.65)
        if cycle == CYCLES: #end loop at final cycle to get to phase 2
            break
        pdi.press('left')
        time.sleep(0.25)
        for i in range(5):
            pdi.press('up')
        pdi.press('enter')
        time.sleep(0.4)
        pdi.press('enter')
        time.sleep(0.65)
        pdi.press('enter')
        time.sleep(0.4)

        # ----------------------------
        # PER-CYCLE LOGGING (one line)
        # ----------------------------
        cycle_end = time.perf_counter()
        cycle_seconds = cycle_end - cycle_start
        elapsed = timedelta(seconds=(cycle_end - run_start_monotonic))

        run_prefix = f"Run: {run + 1}/{outer_loops} | " if outer_loops > 1 else ""
        print(
            f"{run_prefix}"
            f"Cycle: {cycle}/{CYCLES} ({cycle_seconds:.2f}s) | "
            f"Elapsed: {format_elapsed(elapsed)}"
        )

    # ============================================================
    # PHASE 2 — FINAL REFINE (run once after batching)
    # Goal: refine accumulated Mid Tier Refinement into Stat Up (Forbid Med-RF).
    # ============================================================

    # Navigate to Forbid Med-RF
    for i in range(2):
        pdi.press('up')
    pdi.press('enter')
    time.sleep(0.65)

    # Refine to Stat Up
    pdi.press('down')
    if run > 0:
        pdi.press('down')
    pdi.press('enter')
    for i in range(10):
        pdi.press('down')
    pdi.press('enter')

    # ============================================================
    # PHASE 3 — RETURN TO PHASE 1 START
    # Starting state: Forbid Med-RF refine menu
    # Target state:   Esthar Pet Shop → Buy menu, cursor on "G-Potion"
    # ============================================================
    if run < outer_loops - 1:
        pdi.press('c')
        time.sleep(0.65)
        pdi.press('left')
        time.sleep(0.25)
        for i in range(3):
            pdi.press('up')
        pdi.press('enter')
        time.sleep(0.4)
        pdi.press('enter')
        time.sleep(0.65)
        pdi.press('enter')
        time.sleep(0.4)

# ----------------------------
# FINISH LOGGING
# ----------------------------
end_time = datetime.now().astimezone()
actual_duration = end_time - start_time
delta = end_time - estimated_finish_time

print("==========================================")
print(f"{stat['stat_up']} Farming Script Finished")
log_line("Finish Time:", end_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Actual duration:", str(actual_duration))
print("------------------------------------------")
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish time:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Estimate error:", format_eta_error(delta))
print("==========================================")
