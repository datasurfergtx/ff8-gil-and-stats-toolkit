# FF8 Gil & Stat Automation Toolkit (PC / Remastered)

A lightweight Python automation toolkit for *Final Fantasy VIII (PC / Remastered)* that streamlines repetitive menu workflows such as:

- Gil farming via the Tent/Cottage → Mega Potion profit loop  
- Stat refinement automation (HP Up and related items)

This project **simulates keyboard input only**.  
It does **not** read or modify game memory.

---

## ⚠️ Important Notice

These scripts perform deterministic, hard-coded menu navigation.  
They assume exact menu positioning and predictable item ordering.

If your in-game state does not precisely match the expected layout,  
inputs will desynchronize and may result in unintended purchases, item loss, or menu misnavigation.

These scripts:

- Run in continuous `while` loops  
- **Do not auto-terminate**  
- Do not validate game state  
- Do not perform safety checks  

You are fully responsible for:

- Ensuring correct in-game setup before execution  
- Monitoring script behavior while running  
- Stopping execution manually (CTRL + C or terminating the process)  
- Modifying timing values or keybinds if necessary  

This project assumes a working knowledge of:

- Python execution from the command line  
- Installing and managing Python packages  
- Editing source code safely  

> **If you are not comfortable reviewing and modifying Python code, this tool is not recommended for you.**

> **Use at your own discretion.**

---

# Requirements

## System

- Windows 10 / 11
- Final Fantasy VIII (Steam PC or Remastered)
- Game set to **Borderless Windowed** (recommended)
    - Exclusive fullscreen may block simulated input.

---

## Python

- Python 3.9+
- Required package:

```bash
pip install pydirectinput
```