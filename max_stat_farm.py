# ==================================================================
# max_stat_farm.py — v1.0 (2026-02-22)
# ==================================================================
# Automated stat maxing for a single FF8 character.
# Combines gil_farm.py and stat_up_farm.py into a single workflow:
#   1. Farm gil to 99,999,999 (if needed)
#   2. Farm stat-up items via shop + ability refines
#   3. Use stat-up items on target character
#   4. Repeat until stat is maxed
# ==================================================================

# ==================================================================
# DISCLAIMER / READ BEFORE RUNNING
# ==================================================================
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
# ==================================================================

# ==================================================================
# REQUIRED SETUP (before running)
# ==================================================================
# 1) Item menu: Page 1 must be COMPLETELY empty (keeps item ordering consistent).
# 2) Starting state depends on your current gil:
#    - If you have max gil (99,999,999):
#      Open Call Shop → Esthar Pet Shop → Buy menu, cursor on "G-Potion".
#    - If you do NOT have max gil:
#      Open Call Shop → Esthar Shop!!! → Buy menu, cursor on "Potion".
# 3) Keep FF8 focused while running (do not alt-tab). Borderless Windowed
#    is recommended.
# ==================================================================

import time
import math
import re
from datetime import datetime, timedelta

import pydirectinput as pdi

# ==================================================================
# CONFIG
# ==================================================================
pdi.PAUSE = 0.02
FOCUS_GRACE_SECONDS = 5
MAX_GIL = 99_999_999

# Gil farm
GIL_PROFIT_PER_CYCLE = 352_500
GIL_SECONDS_PER_CYCLE = 13.51
GIL_MIN_START = 210_000

# Stat farm
STAT_CYCLES = 10
STAT_COST_PER_RUN = 15_000_000

# Time estimates (seconds)
STAT_ESTIMATED_FIRST_RUN_S = 92
STAT_ESTIMATED_EXTRA_RUN_S = 98
ITEM_USE_SECONDS_PER_ITEM = 0.22
NAV_OVERHEAD_S = 10

CHARACTERS = {
    "squall": 1, "zell": 2, "irvine": 3,
    "quistis": 4, "rinoa": 5, "selphie": 6,
}

STAT_OPTIONS = {
    "hp": {
        "presses": 4, "item": "Giant's Ring", "stat_up": "HP Up",
        "max_stat": 9999, "gain_per_item": 30,
        "items_per_cycle": 10, "max_runs": 1,
    },
    "str": {
        "presses": 5, "item": "Power Wrist", "stat_up": "Str Up",
        "max_stat": 255, "gain_per_item": 1,
        "items_per_cycle": 1, "max_runs": 6,
    },
    "vit": {
        "presses": 6, "item": "Force Armlet", "stat_up": "Vit Up",
        "max_stat": 255, "gain_per_item": 1,
        "items_per_cycle": 1, "max_runs": 6,
    },
    "mag": {
        "presses": 7, "item": "Hypno Crown", "stat_up": "Mag Up",
        "max_stat": 255, "gain_per_item": 1,
        "items_per_cycle": 1, "max_runs": 6,
    },
}

# ==================================================================
# LOGGING HELPERS
# ==================================================================
LABEL_W = 30


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


# ==================================================================
# INPUT HELPERS
# ==================================================================
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


# ====================================================================
# GIL FARM
# ====================================================================
# Buy Cottages/Tents → Refine to Mega Potions → Sell for profit.
# Starting state: Esthar Shop!!! → Buy menu, cursor on "Potion"
# Ending state:   Esthar Shop!!! → Buy menu (after last sell cycle)
# ====================================================================
def run_gil_farm(current_gil, run_start_monotonic):
    remaining = MAX_GIL - current_gil
    cycles = math.ceil(remaining / GIL_PROFIT_PER_CYCLE)

    if cycles <= 0:
        print("  Gil already at max. Skipping gil farm.")
        return

    print(f"  Gil farm: {cycles} cycles ({current_gil:,} → {MAX_GIL:,} gil)")

    for cycle_num in range(1, cycles + 1):
        cycle_start = time.perf_counter()

        # PHASE 1 — BUY TENTS & COTTAGES
        pdi.press("right")
        time.sleep(0.2)
        pdi.press("up")
        pdi.press("up")
        pdi.press("enter")
        time.sleep(0.15)

        for i in range(10):
            pdi.press("up")
        pdi.press("enter")
        pdi.press("up")
        pdi.press("enter")
        time.sleep(0.15)

        for i in range(10):
            pdi.press("up")
        pdi.press("enter")

        pdi.press("c")
        time.sleep(0.4)
        pdi.press("c")
        time.sleep(0.65)

        # PHASE 2 — REFINE ITEMS → MEGA POTIONS
        pdi.press("c")
        time.sleep(0.4)
        pdi.press("right")
        time.sleep(0.2)
        pdi.press("up")
        pdi.press("enter")
        time.sleep(0.65)
        pdi.press("enter")
        time.sleep(0.2)

        for i in range(3):
            pdi.press("down")
        pdi.press("enter")
        time.sleep(0.1)
        pdi.press("down")
        pdi.press("enter")
        time.sleep(0.2)

        for i in range(5):
            pdi.press("down")
        pdi.press("enter")
        time.sleep(0.1)

        pdi.press("c")
        time.sleep(0.65)

        # PHASE 3 — SELL MEGA POTIONS
        pdi.press("left")
        time.sleep(0.2)
        pdi.press("down")
        pdi.press("enter")
        time.sleep(0.4)
        pdi.press("enter")
        time.sleep(0.65)

        pdi.press("right")
        pdi.press("enter")
        time.sleep(0.4)
        pdi.press("down")
        pdi.press("down")
        pdi.press("enter")
        time.sleep(0.2)

        for i in range(8):
            pdi.press("up")
        pdi.press("enter")

        pdi.press("c")
        time.sleep(0.4)
        pdi.press("left")
        pdi.press("enter")
        time.sleep(0.4)

        # PER-CYCLE LOGGING
        cycle_end = time.perf_counter()
        cycle_seconds = cycle_end - cycle_start
        elapsed = timedelta(seconds=(cycle_end - run_start_monotonic))

        print(
            f"  Gil Cycle: {cycle_num}/{cycles} ({cycle_seconds:.2f}s) | "
            f"Elapsed: {format_elapsed(elapsed)}"
        )


# ====================================================================
# STAT FARM
# ====================================================================
# Buy shop item → GFAbl Med-RF → Forbid Med-RF → Stat Up items.
# Starting state: Esthar Pet Shop → Buy menu, cursor on "G-Potion"
# Ending state:   Abilities menu, inside Forbid Med-RF (after final refine)
# ====================================================================
def run_stat_up_farm(stat_choice, stat, num_runs, run_start_monotonic, last_run_cycles=STAT_CYCLES):
    if last_run_cycles < STAT_CYCLES:
        print(
            f"  Stat farm: {stat['item']} → {stat['stat_up']} "
            f"({num_runs} run(s), last run: {last_run_cycles} cycle(s))"
        )
    else:
        print(f"  Stat farm: {stat['item']} → {stat['stat_up']} ({num_runs} run(s))")

    for run in range(num_runs):
        cycles_this_run = last_run_cycles if run == num_runs - 1 else STAT_CYCLES

        if num_runs > 1:
            print(f"  --- Stat Run {run + 1}/{num_runs} ({cycles_this_run} cycles) ---")

        # PHASE 1 — SHOP + GFAbl Med-RF LOOP
        for cycle in range(1, cycles_this_run + 1):
            cycle_start = time.perf_counter()

            # PHASE 1.0 — BUY ITEM
            pdi.press('right')
            time.sleep(0.3)
            for i in range(stat["presses"]):
                pdi.press('down')
            pdi.press('enter')
            time.sleep(0.2)
            for i in range(10):
                pdi.press('up')
            pdi.press('enter')

            pdi.press('c')
            time.sleep(0.4)
            pdi.press('c')
            time.sleep(0.65)
            pdi.press('c')
            time.sleep(0.4)

            # PHASE 1.2 — REFINE ITEM → Mid Tier (GFAbl Med-RF)
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

            # PHASE 1.3 — RETURN TO SHOP (or exit on final cycle)
            pdi.press('c')
            time.sleep(0.65)
            if cycle == cycles_this_run:
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

            # PER-CYCLE LOGGING
            cycle_end = time.perf_counter()
            cycle_seconds = cycle_end - cycle_start
            elapsed = timedelta(seconds=(cycle_end - run_start_monotonic))

            run_prefix = f"Run: {run + 1}/{num_runs} | " if num_runs > 1 else ""
            print(
                f"  {run_prefix}"
                f"Cycle: {cycle}/{cycles_this_run} ({cycle_seconds:.2f}s) | "
                f"Elapsed: {format_elapsed(elapsed)}"
            )

        # PHASE 2 — FINAL REFINE (Forbid Med-RF)
        phase2_start = time.perf_counter()

        for i in range(2):
            pdi.press('up')
        pdi.press('enter')
        time.sleep(0.65)

        pdi.press('down')
        if run > 0:
            pdi.press('down')
        pdi.press('enter')
        for i in range(10):
            pdi.press('down')
        pdi.press('enter')

        phase2_end = time.perf_counter()
        phase2_seconds = phase2_end - phase2_start
        elapsed = timedelta(seconds=(phase2_end - run_start_monotonic))

        run_prefix = f"Run: {run + 1}/{num_runs} | " if num_runs > 1 else ""
        print(
            f"  {run_prefix}"
            f"Stat Ref: 1/1 ({phase2_seconds:.2f}s) | "
            f"Elapsed: {format_elapsed(elapsed)}"
        )

        # PHASE 3 — RETURN TO SHOP (for next run, skipped on final run)
        if run < num_runs - 1:
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


# ====================================================================
# NAVIGATION
# ====================================================================
def navigate_gil_farm_to_stat_farm():
    """
    Navigate from gil farm end state to stat farm start state.
    Starting state: Esthar Shop!!! → Buy menu (after last sell cycle)
    Target state:   Esthar Pet Shop → Buy menu, cursor on "G-Potion"
    """
    pdi.press('c')
    time.sleep(0.4)
    pdi.press('c')
    time.sleep(0.65)
    for i in range(2):
        pdi.press('up')
    pdi.press('enter')
    time.sleep(0.65)
    pdi.press('enter')
    time.sleep(0.4)


def navigate_stat_farm_to_item_usage(character_position, stat_up_name, items_to_use):
    """
    Navigate from stat farm end state to item usage ready state.
    Starting state: Abilities menu, inside Forbid Med-RF (after final refine)
    Target state:   Item menu → stat-up item selected → target character
                    highlighted → cursor on "Use" / Confirm

    Use character_position (1-6) to select the correct character:
      Squall=1, Zell=2, Irvine=3, Quistis=4, Rinoa=5, Selphie=6
    The stat-up item to select is stat_up_name (e.g. "HP Up", "Str Up").
    """
    pdi.press('c')
    time.sleep(0.65)
    pdi.press('c')
    time.sleep(0.8)
    for i in range(4):
        pdi.press('up')
    pdi.press('enter')
    time.sleep(0.65)
    pdi.press('enter')
    time.sleep(0.2)
    for i in range(character_position-1):
        pdi.press('down')
    for i in range(items_to_use):
        pdi.press('enter')
        time.sleep(0.2)
        pdi.press('enter')


def navigate_item_usage_to_gil_farm():
    """
    Navigate from item usage end state to gil farm start state.
    Starting state: Item menu (after using all stat-up items)
    Target state:   Esthar Shop!!! → Buy menu, cursor on "Potion"
    """
    pdi.press('c')
    time.sleep(0.2)
    pdi.press('c')
    time.sleep(0.65)
    for i in range(4):
        pdi.press('down')
    pdi.press('enter')
    time.sleep(0.65)
    for i in range(3):
        pdi.press('down')
    pdi.press('enter')
    time.sleep(0.4)
    pdi.press('up')
    pdi.press('enter')
    time.sleep(0.65)
    pdi.press('enter')
    time.sleep(0.4)



# ====================================================================
# ITEM USAGE
# ====================================================================
# Use stat-up items on the selected character.
# Starting state: Item menu, stat-up item selected, target character
#                 highlighted, cursor on "Use" / Confirm.
# Each item use = 2 confirm presses (confirm character + confirm usage).
# ====================================================================
def use_stat_items(count):
    print(f"  Using {count}x stat-up items...")
    original_pause = pdi.PAUSE
    pdi.PAUSE = 0.00000000001
    for i in range(count):
        pdi.press('enter')
        pdi.press('enter')
    pdi.PAUSE = original_pause
    print(f"  Item usage complete ({count} used).")


# ====================================================================
# USER INPUT
# ====================================================================
print("==========================================")
print("FF8 Automated Stat Maxing Script")
print("==========================================")

# --- CHARACTER SELECTION ---
print("------------------------------------------")
print("Select character to max:")
print("  Squall, Zell, Irvine, Quistis, Rinoa, Selphie")
print("------------------------------------------")

while True:
    char_input = input("Character: ").strip().lower()
    if char_input in CHARACTERS:
        break
    print("Invalid. Enter one of: Squall, Zell, Irvine, Quistis, Rinoa, Selphie")

character_name = char_input.capitalize()
character_position = CHARACTERS[char_input]

# --- STAT SELECTION ---
print("------------------------------------------")
print("Which stat do you want to max?")
print("  Options: HP, Str, Vit, Mag")
print("------------------------------------------")

while True:
    stat_choice = input("Stat: ").strip().lower()
    if stat_choice in STAT_OPTIONS:
        break
    print("Invalid. Enter one of: HP, Str, Vit, Mag")

stat = STAT_OPTIONS[stat_choice]

# --- BASE STAT INPUT ---
stat_label = stat['stat_up'].replace(' Up', '')
print("------------------------------------------")
print(f"Enter {character_name}'s current base {stat_label} stat.")
print(f"  Max: {stat['max_stat']:,}")
print("------------------------------------------")

while True:
    try:
        base_stat = int(input(f"Current base {stat_label}: ").strip())
        if base_stat < 0:
            print("Enter a non-negative value.")
            continue
        if base_stat >= stat['max_stat']:
            print(f"Stat is already at or above max ({stat['max_stat']:,}). Nothing to do.")
            raise SystemExit
        break
    except ValueError:
        print("Enter a valid integer.")

# --- CALCULATE ITEMS & ITERATIONS ---
stat_deficit = stat['max_stat'] - base_stat
items_needed = math.ceil(stat_deficit / stat['gain_per_item'])
items_per_cycle = stat['items_per_cycle']
items_per_full_run = items_per_cycle * STAT_CYCLES
max_runs_per_exec = stat['max_runs']
max_items_per_exec = items_per_full_run * max_runs_per_exec
total_iterations = math.ceil(items_needed / max_items_per_exec)

# --- GIL INPUT ---
print("------------------------------------------")
print("How much gil do you currently have?")
print("  (examples: 210000, 210k, 0.21m, 99m, max)")
print("------------------------------------------")

while True:
    raw = input("Current gil: ").strip()
    if raw.lower() == "max":
        current_gil = MAX_GIL
        break
    try:
        current_gil = parse_gil_input(raw)
        if current_gil < 0:
            print("Enter a non-negative amount.")
            continue
        if current_gil > MAX_GIL:
            current_gil = MAX_GIL
        break
    except ValueError:
        print("Invalid input. Examples: 210000, 210k, 0.21m, 99m, max")

has_max_gil = current_gil >= MAX_GIL

# --- ESTIMATE TOTAL TIME ---
max_gil_cost_per_exec = max_runs_per_exec * STAT_COST_PER_RUN
stat_farm_est_s = STAT_ESTIMATED_FIRST_RUN_S + STAT_ESTIMATED_EXTRA_RUN_S * (max_runs_per_exec - 1)
item_use_est_s = max_items_per_exec * ITEM_USE_SECONDS_PER_ITEM
subsequent_gil_cycles = math.ceil(max_gil_cost_per_exec / GIL_PROFIT_PER_CYCLE)
subsequent_gil_est_s = subsequent_gil_cycles * GIL_SECONDS_PER_CYCLE
subsequent_iter_est_s = subsequent_gil_est_s + stat_farm_est_s + item_use_est_s + NAV_OVERHEAD_S

if has_max_gil:
    first_iter_est_s = stat_farm_est_s + item_use_est_s + NAV_OVERHEAD_S
else:
    first_gil_cycles = math.ceil((MAX_GIL - current_gil) / GIL_PROFIT_PER_CYCLE)
    first_iter_est_s = first_gil_cycles * GIL_SECONDS_PER_CYCLE + stat_farm_est_s + item_use_est_s + NAV_OVERHEAD_S

if total_iterations == 1:
    total_est_s = first_iter_est_s
else:
    total_est_s = first_iter_est_s + (total_iterations - 1) * subsequent_iter_est_s

estimated_duration = timedelta(seconds=total_est_s)

# --- CONFIGURATION SUMMARY ---
print("==========================================")
print("Configuration Summary")
print("------------------------------------------")
log_line("Character:", f"{character_name} (position {character_position})")
log_line("Stat:", stat['stat_up'])
log_line("Current base stat:", f"{base_stat:,}")
log_line("Target stat:", f"{stat['max_stat']:,}")
log_line("Stat deficit:", f"{stat_deficit:,}")
log_line(f"{stat['stat_up']}s needed:", f"{items_needed:,}")
log_line("Items per cycle:", str(items_per_cycle))
log_line("Items per full run:", str(items_per_full_run))
log_line("Max runs per execution:", str(max_runs_per_exec))
log_line("Max items per execution:", str(max_items_per_exec))
log_line("Max gil cost per exec:", f"{max_gil_cost_per_exec:,}")
log_line("Total iterations:", str(total_iterations))
log_line("Current gil:", f"{current_gil:,}")
log_line("Starting phase:", "Stat Farm" if has_max_gil else "Gil Farm")
print("------------------------------------------")
log_line("Estimated duration:", str(estimated_duration))
print("==========================================")

if has_max_gil:
    print("REQUIRED: Esthar Pet Shop → Buy menu, cursor on 'G-Potion'")
else:
    print("REQUIRED: Esthar Shop!!! → Buy menu, cursor on 'Potion'")

print(f"Click into FF8 now. Starting in {FOCUS_GRACE_SECONDS} seconds...")
time.sleep(FOCUS_GRACE_SECONDS)

# ====================================================================
# START LOGGING
# ====================================================================
start_time = datetime.now().astimezone()
estimated_finish_time = start_time + estimated_duration

print("==========================================")
print(f"{stat['stat_up']} Maxing Script Started")
log_line("Start time:", start_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
print("==========================================")

# ====================================================================
# MAIN LOOP
# ====================================================================
run_start_monotonic = time.perf_counter()
remaining_items = items_needed
iteration_times = []

for iteration in range(1, total_iterations + 1):
    iter_start_mono = time.perf_counter()

    # --- CALCULATE EXECUTION PLAN FOR THIS ITERATION ---
    total_cycles_needed = math.ceil(remaining_items / items_per_cycle)
    full_runs = total_cycles_needed // STAT_CYCLES
    leftover_cycles = total_cycles_needed % STAT_CYCLES
    total_runs_needed = full_runs + (1 if leftover_cycles > 0 else 0)

    runs_this_iter = min(total_runs_needed, max_runs_per_exec)
    if runs_this_iter == total_runs_needed and leftover_cycles > 0:
        last_run_cycles = leftover_cycles
        items_this_iter = (runs_this_iter - 1) * items_per_full_run + leftover_cycles * items_per_cycle
    else:
        last_run_cycles = STAT_CYCLES
        items_this_iter = runs_this_iter * items_per_full_run

    gil_cost_this_iter = runs_this_iter * STAT_COST_PER_RUN

    # --- ITERATION HEADER ---
    elapsed_so_far = timedelta(seconds=(iter_start_mono - run_start_monotonic))

    print("==========================================")
    print(f"Iteration {iteration}/{total_iterations} — {stat['stat_up']} → {character_name}")
    log_line("  Items this iteration:", str(items_this_iter))
    log_line("  Items remaining after:", str(remaining_items - items_this_iter))
    if last_run_cycles < STAT_CYCLES:
        log_line("  Runs:", f"{runs_this_iter} ({runs_this_iter - 1} full + 1×{last_run_cycles} cycles)")
    else:
        log_line("  Runs:", f"{runs_this_iter} (all full)")
    log_line("  Elapsed:", format_elapsed(elapsed_so_far))
    if iteration > 1:
        avg_iter_s = sum(iteration_times) / len(iteration_times)
        eta_remaining = timedelta(seconds=avg_iter_s * (total_iterations - iteration + 1))
        eta_finish = datetime.now().astimezone() + eta_remaining
        log_line("  ETA remaining:", str(eta_remaining))
        log_line("  ETA finish:", eta_finish.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("==========================================")

    # --- GIL FARM (if not at max gil) ---
    if current_gil < MAX_GIL:
        if current_gil < GIL_MIN_START:
            print(f"ERROR: Insufficient gil ({current_gil:,}). Need at least {GIL_MIN_START:,}.")
            raise SystemExit
        print("[Gil Farm] Farming to max gil...")
        run_gil_farm(current_gil, run_start_monotonic)
        current_gil = MAX_GIL

        print("[Navigate] Gil Farm → Stat Farm")
        navigate_gil_farm_to_stat_farm()

    # --- STAT FARM ---
    print("[Stat Farm] Farming stat-up items...")
    run_stat_up_farm(stat_choice, stat, runs_this_iter, run_start_monotonic, last_run_cycles)
    current_gil -= gil_cost_this_iter

    # --- ITEM USAGE ---
    print(f"[Navigate] Stat Farm → Item Usage ({stat['stat_up']} on {character_name})")
    navigate_stat_farm_to_item_usage(character_position, stat['stat_up'], items_this_iter)

    print(f"[Item Usage] Using {items_this_iter}x {stat['stat_up']} on {character_name}...")
    use_stat_items(items_this_iter)
    remaining_items -= items_this_iter

    # --- NAVIGATE BACK FOR NEXT ITERATION ---
    if remaining_items > 0:
        print("[Navigate] Item Usage → Gil Farm")
        navigate_item_usage_to_gil_farm()

    # --- ITERATION COMPLETE LOGGING ---
    iter_end_mono = time.perf_counter()
    iter_seconds = iter_end_mono - iter_start_mono
    iteration_times.append(iter_seconds)
    elapsed = timedelta(seconds=(iter_end_mono - run_start_monotonic))
    remaining_iters = total_iterations - iteration

    print("------------------------------------------")
    log_line(f"Iteration {iteration} complete:", f"{iter_seconds:.2f}s")
    log_line("  Elapsed:", format_elapsed(elapsed))
    if remaining_iters > 0:
        avg_iter_s = sum(iteration_times) / len(iteration_times)
        eta_remaining = timedelta(seconds=avg_iter_s * remaining_iters)
        eta_finish = datetime.now().astimezone() + eta_remaining
        log_line("  Remaining iterations:", str(remaining_iters))
        log_line("  ETA remaining:", str(eta_remaining))
        log_line("  ETA finish:", eta_finish.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("------------------------------------------")

# ====================================================================
# FINISH
# ====================================================================
end_time = datetime.now().astimezone()
actual_duration = end_time - start_time
delta = end_time - estimated_finish_time

print("==========================================")
print(f"{stat['stat_up']} Maxing Complete!")
print("------------------------------------------")
log_line("Character:", character_name)
log_line("Stat maxed:", f"{stat_label} → {stat['max_stat']:,}")
log_line("Total items used:", f"{items_needed:,}")
log_line("Total iterations:", str(total_iterations))
print("------------------------------------------")
log_line("Start time:", start_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Finish time:", end_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Actual duration:", str(actual_duration))
print("------------------------------------------")
log_line("Estimated duration:", str(estimated_duration))
log_line("Estimated finish:", estimated_finish_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
log_line("Estimate error:", format_eta_error(delta))
print("==========================================")
