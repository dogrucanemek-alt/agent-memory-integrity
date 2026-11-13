# agmi: the print behind the two Verax memory rows
# SPDX-License-Identifier: MIT
"""Step 3 of docs/adding-a-row.md for the two Verax adapters, with what was measured.

Run from the repository root:

    AGMI_VERAX_DIR=<dir with @verax-ai/body installed by npm> PYTHONPATH=. python3 verax_row_print.py

It prints the Python and Node versions, the installed Verax packages, the
sha256 of the adapter file, the ten cut lines per row as step 3 prints them,
and then the same lines uncut.
"""
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path

import agmi.adapters.verax_memory as vm
from agmi.adapters.verax_memory import VeraxMemoryAdapter, VeraxMemoryHeadOutsideAdapter
from agmi.attacks.at_rest import AT_REST_ATTACKS_WITH_ERASE as X


def installed(name: str) -> str:
    path = Path(os.environ["AGMI_VERAX_DIR"]) / "node_modules" / name / "package.json"
    return json.loads(path.read_text(encoding="utf-8"))["version"]


print("python", platform.python_version(), flush=True)
print("node", subprocess.run([vm.node_binary(), "--version"], capture_output=True, text=True).stdout.strip(), flush=True)
for pkg in ("@verax-ai/body", "@verax-ai/proxy", "@verax-ai/inventory"):
    print(pkg, installed(pkg), flush=True)
print("adapter sha256", hashlib.sha256(Path(vm.__file__).read_bytes()).hexdigest(), flush=True)

full = []
for A in (VeraxMemoryAdapter, VeraxMemoryHeadOutsideAdapter):
    print(f"== {A.name}: {A.measured_on()}", flush=True)
    for c in X:
        r = c().run(A())
        text = r.guard or r.detail or r.error or ""
        print(f"{r.attack:20} {r.status:11} {text[:90]}", flush=True)
        full.append(f"{A.name} | {r.attack}@v{r.version} {r.status} | {text}")

print("== uncut", flush=True)
for line in full:
    print(line, flush=True)
