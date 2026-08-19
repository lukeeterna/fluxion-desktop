from pathlib import Path
import runpy

here = Path(__file__).resolve().parent
body = here / "finalize_live_transfer_mac_body.py"
repair = here / "repair_live_transfer_patcher.py"
current = Path(__file__).resolve()

# Restore the original deterministic patcher body, structurally repair its one
# fragile function replacement, then execute the repaired body in this process.
current.write_text(body.read_text(encoding="utf-8"), encoding="utf-8")
runpy.run_path(str(repair), run_name="__main__")
runpy.run_path(str(current), run_name="__main__")
