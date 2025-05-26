#!/usr/bin/env python3
import re
import sys

# 1) Read your plugin list until Ctrl-D
print("Paste your plugin list below and then press Ctrl-D when you’re done:")
text = sys.stdin.read()

# 2) Extract plugin names
plugin_names = re.findall(r"Select\s+([^\t\n]+?)(?:\s{2,}|\t|$)", text)
if not plugin_names:
    print("No plugins found. Make sure your text includes lines like `Select Plugin Name`.")
    sys.exit(1)

# 3) Show the initial numbered list
print("\nPlugins found:")
for i, name in enumerate(plugin_names, start=1):
    print(f"{i}. {name.strip()}")

# 4) Re-open stdin so we can prompt interactively
try:
    sys.stdin = open("/dev/tty")
except Exception:
    pass

failed_idxs = set()

# 5) Loop: toggle failures, show numbered splits, until Ctrl-D
while True:
    try:
        line = input(
            "\nEnter numbers to toggle FAILED status (e.g. 2 5 7).\n"
            "Typing a number again moves it back to UPDATED.\n"
            "Press Ctrl-D on an empty prompt to finish: "
        )
    except EOFError:
        break  # exit loop on Ctrl-D

    # parse input
    parts = line.strip().split()
    toggles = {int(p) for p in parts if p.isdigit()}

    # toggle each index
    for idx in toggles:
        if idx in failed_idxs:
            failed_idxs.remove(idx)
        else:
            failed_idxs.add(idx)

    # split into updated vs failed, keeping original numbering
    updated = [(i, plugin_names[i - 1].strip()) for i in range(1, len(plugin_names) + 1) if i not in failed_idxs]
    failed = [(i, plugin_names[i - 1].strip()) for i in range(1, len(plugin_names) + 1) if i in failed_idxs]

    # print the current state, numbered
    print("\nUpdated plugins:")
    for i, name in updated:
        print(f"{i}. {name}")
    print("\nFailed updates:")
    for i, name in failed:
        print(f"{i}. {name}")

# 6) Final output in bullet form
print("\n✅ Updated:")
for _, name in updated:
    print(f"- {name}")

# Only show Failed section if there are any failures
if failed:
    print("\n❌ Failed:")
    for _, name in failed:
        print(f"- {name}")
