# FF8 Gil & Stat Automation Toolkit (PC / Remastered)

A lightweight Python automation toolkit for *Final Fantasy VIII (PC / Remastered)* that streamlines repetitive menu workflows such as:

- **Gil farming** via the Tent/Cottage → Mega Potion profit loop
- **Stat-up item farming** (HP Up, Str Up, Vit Up, Mag Up) via shop purchases and GF ability refinement
- **Full stat maxing** — end-to-end automated workflow combining gil farming, stat-up farming, and item usage
- **Rapid stat-up item usage** on a selected character

This project **simulates keyboard input only**.
It does **not** read or modify game memory.

---

## Demo

https://github.com/user-attachments/assets/7c762880-ba03-4371-848c-aebf53ddaa39

---

## Scripts

| Script | Purpose | Starting Location |
|--------|---------|-------------------|
| `gil_farm.py` | Farm gil via Mega Potion buy/refine/sell loop | Esthar Shop!!! → Buy, cursor on "Potion" |
| `stat_up_farm.py` | Farm stat-up items (HP/Str/Vit/Mag Up) | Esthar Pet Shop → Buy, cursor on "G-Potion" |
| `max_stat_farm.py` | Fully max a stat on one character (gil farm → stat farm → item use, repeated) | Depends on current gil (see below) |
| `use_x_stat_boost.py` | Rapidly use stat-up items on a character | Item menu, stat-up selected, character highlighted |

---

## Requirements

### System

- Windows 10 / 11
- Final Fantasy VIII (Steam PC or Remastered)
- Game set to **Borderless Windowed** (recommended)
  - Exclusive fullscreen may block simulated input.

### Python

- Python 3.9+
- Required package:

```bash
pip install pydirectinput
```

---

## Keyboard Control Configuration

This toolkit assumes specific keyboard bindings inside Final Fantasy VIII.

If your controls differ, you must either:
- Rebind your in-game controls to match below, **or**
- Modify the script to match your layout.

### Required Keybinds

| Script Key | In-Game Function       |
|------------|------------------------|
| `Enter`    | Confirm / Select       |
| `C`        | Cancel / Back          |
| `Up`       | Menu Navigation Up     |
| `Down`     | Menu Navigation Down   |
| `Left`     | Menu Navigation Left   |
| `Right`    | Menu Navigation Right  |

---

## Script Details

### `gil_farm.py` — Gil Farming

Automates the Tent/Cottage → Mega Potion profit loop at Esthar Shop!!!

**Per cycle:** +352,500 gil profit

| Phase | Action |
|-------|--------|
| 1 | Buy 100 Cottages + 100 Tents |
| 2 | Refine via Recov Med-RF → 25 + 75 Mega Potions |
| 3 | Sell 75 Mega Potions |

**Prompts:** Current gil (e.g. `210000`, `210k`, `0.21m`, `30m`)
**Minimum gil:** 210,000
**Runs until:** 99,999,999 gil

**Setup:**
1. Item menu Page 1 must be completely empty.
2. Open Call Shop → Esthar Shop!!! → Buy menu.
3. Place cursor on "Potion".

---

### `stat_up_farm.py` — Stat-Up Item Farming

Buys items at Esthar Pet Shop and refines them through GFAbl Med-RF and Forbid Med-RF into stat-up items.

**Cost:** 15,000,000 gil per run (+210k reserved)

| Stat | Buy Item | Mid Refine | Final Item | Yield per Run |
|------|----------|------------|------------|---------------|
| HP | Giant's Ring | Gaea's Ring | HP Up | 100 |
| Str | Power Wrist | Hyper Wrist | Str Up | 10 |
| Vit | Force Armlet | Magic Armlet | Vit Up | 10 |
| Mag | Hypno Crown | Royal Crown | Mag Up | 10 |

**Prompts:** Stat choice (HP/Str/Vit/Mag), optional current gil to calculate affordable runs

**Setup:**
1. Item menu Page 1 must be completely empty.
2. Open Call Shop → Esthar Pet Shop → Buy menu.
3. Place cursor on "G-Potion".

---

### `max_stat_farm.py` — Full Stat Maxing

Orchestrates the complete stat maxing workflow for a single character by chaining gil farming, stat-up farming, and item usage in a loop until the chosen stat reaches its maximum.

**Workflow per iteration:**
1. **Gil Farm** — Farm to 99,999,999 gil (skipped if already at max)
2. **Stat Farm** — Buy + refine stat-up items
3. **Item Use** — Apply stat-up items to the target character
4. **Repeat** until stat is maxed

**Supported stats:**

| Stat | Max | Gain per Item | Items per Full Iteration |
|------|-----|---------------|--------------------------|
| HP | 9,999 | +30 | 100 (1 run × 10 cycles) |
| Str | 255 | +1 | 60 (6 runs × 10 cycles) |
| Vit | 255 | +1 | 60 (6 runs × 10 cycles) |
| Mag | 255 | +1 | 60 (6 runs × 10 cycles) |

**Supported characters:** Squall, Zell, Irvine, Quistis, Rinoa, Selphie

**Prompts:** Character, stat, current base stat, current gil

**Setup:**
1. Item menu Page 1 must be completely empty.
2. Starting state depends on current gil:
   - **Max gil (99,999,999):** Call Shop → Esthar Pet Shop → Buy, cursor on "G-Potion"
   - **Not max gil:** Call Shop → Esthar Shop!!! → Buy, cursor on "Potion"

The script builds an execution plan, estimates total duration, and refines its ETA as it runs.

---

### `use_x_stat_boost.py` — Rapid Stat-Up Item Usage

Sends repeated Enter presses to quickly use stat-up items on a character.

**Prompts:** Number of items to use (1–150)
**Per item:** 2 confirm presses (confirm character + confirm usage)

**Setup:**
1. Open the Item menu.
2. Select the desired stat-boost item (e.g. HP Up).
3. Highlight the target character.
4. Leave cursor on "Use" / Confirm.

---

## Operational Notice

These scripts perform **deterministic, hard-coded menu navigation**.
They assume exact menu positioning and predictable item ordering.

If your in-game state does not precisely match the expected layout, inputs will desynchronize and may result in unintended purchases, item loss, or menu misnavigation.

These scripts:

- Run a **finite number of cycles** (based on your input)
- **Auto-terminate** after completing the calculated number of cycles
- Do not validate game state
- Do not read game memory
- Do not perform safety checks against desync

**You are responsible for:**

- Ensuring correct in-game setup before execution
- Monitoring script behavior while running
- Stopping execution manually if needed (`Ctrl+C` or terminating the process)
- Modifying timing values or keybinds if necessary

This project assumes working knowledge of:

- Python execution from the command line
- Installing and managing Python packages
- Editing source code safely

**If you are not comfortable reviewing and modifying Python code, this tool is not recommended for you.**

**Use at your own discretion.**
