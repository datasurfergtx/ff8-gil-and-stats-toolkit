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
# This script runs indefinitely (while True). You must manually stop it:
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
# ============================================================

import time
import pydirectinput as pdi

# Give yourself time to click back into FF8
time.sleep(5)

while True:

    # ============================================================
    # PHASE 1 — BUY TENTS & COTTAGES 
    # ============================================================

    # Navigate to Tents & Cottages
    pdi.press('right')
    pdi.press('up')
    pdi.press('up')
    pdi.press('enter')

    # Buy 100 Cottages
    pdi.keyDown('up')
    time.sleep(1.01)
    pdi.keyUp('up')
    pdi.press('enter')
    pdi.press('up')
    pdi.press('enter')

    # Buy 100 Tents
    pdi.keyDown('up')
    time.sleep(1.01)
    pdi.keyUp('up')
    pdi.press('enter')

    # Exit Buy menu
    pdi.press('c')
    pdi.press('c')
    time.sleep(0.4)

    # ============================================================
    # PHASE 2 — REFINE ITEMS → MEGA POTIONS
    # ============================================================

    # Navigate to Recov Med-RF
    pdi.press('c')
    pdi.press('right')
    pdi.press('up')
    pdi.press('enter')
    time.sleep(0.4)
    pdi.press('enter')

    # Refine Tents → 25x Mega Potions
    pdi.keyDown('down')
    time.sleep(0.3)
    pdi.keyUp('down')
    pdi.press('enter')
    pdi.press('down')
    pdi.press('enter')

    # Refine Cottages → 75x Mega Potions
    pdi.keyDown('down')
    time.sleep(0.5)
    pdi.keyUp('down')
    pdi.press('enter')

    # Exit Recov Med-RF
    pdi.press('c')
    time.sleep(0.4)

    # ============================================================
    # PHASE 3 — SELL MEGA POTIONS
    # ============================================================

    # Navigate to Call Shop → Esthar Shop!!!
    pdi.press('left')
    pdi.press('down')
    pdi.press('enter')
    pdi.press('enter')
    time.sleep(0.4)

    # Move to Mega Potions
    pdi.press('right')
    pdi.press('enter')
    pdi.press('down')
    pdi.press('down')
    pdi.press('enter')

    # Sell 75x Mega Potions
    pdi.keyDown('up')
    time.sleep(0.8)
    pdi.keyUp('up')
    pdi.press('enter')

    # Exit Sell
    pdi.press('c')
    pdi.press('left')
    pdi.press('enter')