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
# - Phase 1 (looped): Buy Giant's Rings → Refine into Gaea's Rings → Return to shop.
# - Phase 2 (once): Refine accumulated Gaea's Rings → HP Up (Forbid Med-RF).
#
# NOTE: Phase 2 runs ONCE after the loop, which is useful for batching inputs.
# ==================================================================

import time
import pydirectinput as pdi

# ----------------------------
# CONFIG
# ----------------------------
FOCUS_GRACE_SECONDS = 5  # time to click back into FF8 after starting script
pdi.PAUSE = 0.02 # Remove built-in delay

print(f"Click into FF8 now. Starting in {FOCUS_GRACE_SECONDS} seconds...")
time.sleep(FOCUS_GRACE_SECONDS)

# ============================================================
# PHASE 1 — SHOP + MED-RF LOOP (run 10 cycles)
# Goal: repeatedly buy Giant's Rings and convert them into Gaea's Rings.
# ============================================================
for cycle in range(10):
    # ------------------------------------------------------------
    # PHASE 1.0 — BUY GIANT'S RINGS
    # Starting state (assumed): Esthar Pet Shop → Buy menu, cursor on "G-Potion"
    # ------------------------------------------------------------

    pdi.press('right')
    time.sleep(0.1)
    for i in range(4):
        pdi.press('down')
    pdi.press('enter')
    for i in range(10):
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
    # PHASE 1.2 — REFINE GIANT'S RINGS → GAEA'S RINGS (GFAbl Med-RF)
    # ------------------------------------------------------------

    pdi.press('right')
    time.sleep(0.1)
    for i in range(5):
        pdi.press('down')
    pdi.press('enter')
    time.sleep(0.65)
    pdi.press('enter')
    pdi.press('down')
    pdi.press('enter')

    # ------------------------------------------------------------
    # PHASE 1.3 — RETURN TO ESTHAR PET SHOP
    # ------------------------------------------------------------

    pdi.press('c')
    time.sleep(0.65)
    pdi.press('left')
    time.sleep(0.1)
    for i in range(5):
        pdi.press('up')
    pdi.press('enter')
    time.sleep(0.4)
    pdi.press('enter')
    time.sleep(0.65)
    pdi.press('enter')
    time.sleep(0.4)

# ============================================================
# PHASE 2 — FINAL REFINE (run once after batching)
# Goal: refine accumulated Gaea's Rings into HP Up (Forbid Med-RF).
# ============================================================

# Navigate to Forbid Med-RF
pdi.press('c')
time.sleep(0.4)
pdi.press('c')
time.sleep(0.65)
pdi.press('c')
time.sleep(0.4)
pdi.press('right')
time.sleep(0.1)
for i in range(3):
    pdi.press('down')
pdi.press('enter')
time.sleep(0.65)

# Refine to HP Up
pdi.press('down')
pdi.press('enter')
for i in range(10):
    pdi.press('down')
pdi.press('enter')
