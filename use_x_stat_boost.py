# ==================================================================
# DISCLAIMER / READ BEFORE RUNNING
# ==================================================================
# This script simulates keyboard input only. It does NOT read game memory,
# detect screen state, or validate menus. It sends repeated confirm inputs
# based on the current in-game cursor position.
#
# If the game/menu state is not EXACTLY as expected, inputs may desynchronize
# and cause unintended item usage.
#
# By executing this script, you accept full responsibility for the outcome.
# If you are not comfortable reviewing and modifying Python code, do not use it.
# ==================================================================

# ==================================================================
# REQUIRED SETUP (before running)
# ==================================================================
# Purpose:
# Rapidly use a stat-boosting item (e.g., HP Up) multiple times on a character.
#
# Starting state assumptions:
# 1) Open the Item menu.
# 2) Select the desired stat-boost item (e.g., HP Up).
# 3) Highlight the character you want to apply the item to.
# 4) Leave the cursor positioned on "Use" / Confirm.
#
# Each item use requires TWO confirm presses:
#   - Confirm character
#   - Confirm item usage
# ==================================================================

import time
import pydirectinput as pdi

# Remove built-in delay
pdi.PAUSE = 0.00000000001

# Ask user how many items to use
try:
    uses = int(input("How many items would you like to use? "))
    if uses <= 0 or uses > 150:
        raise ValueError
except ValueError:
    print("Please enter a valid positive integer.")
    exit()

# Each item use requires 2 confirm presses
total_presses = uses * 2

print(f"\nUsing item {uses} time(s)...")
print("Switch to FF8 window now.")

# Give yourself time to click back into FF8
time.sleep(5)

# Send confirm inputs
for i in range(total_presses):
    pdi.press('enter')

print("Done.")