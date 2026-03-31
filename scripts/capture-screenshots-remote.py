#!/usr/bin/env python3
"""
FLUXION Screenshot Capture Script
Captures 18+ screenshots from iMac via SSH with realistic demo data

Usage:
  python3 scripts/capture-screenshots-remote.py

Configuration:
  - Connects to iMac at 192.168.1.2
  - Tauri dev server running at http://localhost:1420
  - Outputs to landing/screenshots/
"""

import subprocess
import time
import sys
from pathlib import Path
from typing import List, Tuple

class FluxionScreenshotCapturer:
    def __init__(self, imac_host: str = "imac", local_output_dir: str = "landing/screenshots"):
        self.imac_host = imac_host
        self.local_output_dir = local_output_dir
        self.imac_output_dir = "/tmp/fluxion_screenshots"
        self.vite_url = "http://localhost:1420/index.html"

        # Routes to capture: (hash_route, filename, description)
        self.routes: List[Tuple[str, str, str]] = [
            ("#/", "01-dashboard.png", "Dashboard con fatturato e appuntamenti"),
            ("#/calendario", "02-calendario.png", "Calendario giornata piena"),
            ("#/clienti", "03-clienti.png", "Lista clienti con fedeltà"),
            ("#/servizi", "04-servizi.png", "Servizi con prezzi"),
            ("#/operatori", "05-operatori.png", "Profili operatori"),
            ("#/fatture", "06-fatture.png", "Fatture emesse"),
            ("#/cassa", "07-cassa.png", "Incassi giornata"),
            ("#/voice-agent", "08-voice.png", "Voice Agent Sara"),
            ("#/fornitori", "09-fornitori.png", "Lista fornitori"),
            ("#/analytics", "10-analytics.png", "Grafici fatturato"),
            ("#/impostazioni", "11-impostazioni.png", "Impostazioni sidebar"),
            ("#/impostazioni?tab=pacchetti", "12-pacchetti.png", "Pacchetti e promozioni"),
            ("#/impostazioni?tab=loyalty", "13-fedelta.png", "Programma fedeltà VIP"),
        ]

    def create_swift_capture_script(self) -> str:
        """Returns Swift code for capturing window"""
        return """import Quartz
import AppKit
import Foundation

// Find FLUXION/Tauri window
guard let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] else {
    print("ERROR: Could not get windows")
    exit(1)
}

var fluxionWid: CGWindowID? = nil

// First pass: look for Tauri window specifically
for window in windows {
    let name = window["kCGWindowOwnerName"] as? String ?? ""
    if name.lowercased().contains("tauri") {
        if let wid = window["kCGWindowNumber"] as? CGWindowID {
            fluxionWid = wid
            break
        }
    }
}

// Fallback: find largest window
if fluxionWid == nil {
    var maxHeight: Int = 600

    for window in windows {
        let name = window["kCGWindowOwnerName"] as? String ?? ""

        if name.contains("Dock") || name.contains("Menu") || name.contains("Finder") {
            continue
        }

        let bounds = window["kCGWindowBounds"] as? [String: Any]
        let height = bounds?["Height"] as? Int ?? 0

        if height > maxHeight {
            maxHeight = height
            if let wid = window["kCGWindowNumber"] as? CGWindowID {
                fluxionWid = wid
            }
        }
    }
}

guard let wid = fluxionWid else {
    print("ERROR: Could not find FLUXION window")
    exit(1)
}

// Capture
guard let image = CGWindowListCreateImage(.null, .optionIncludingWindow, wid, [.bestResolution]) else {
    print("ERROR: Capture failed")
    exit(1)
}

// Get output path from arguments
guard CommandLine.arguments.count > 1 else {
    print("ERROR: No output path")
    exit(1)
}

let outputPath = CommandLine.arguments[1]

// Convert and save
let nsImage = NSImage(cgImage: image, size: NSZeroSize)
guard let tiffData = nsImage.tiffRepresentation else {
    print("ERROR: TIFF conversion failed")
    exit(1)
}

guard let bitmapImage = NSBitmapImageRep(data: tiffData) else {
    print("ERROR: Bitmap creation failed")
    exit(1)
}

guard let pngData = bitmapImage.representation(using: NSBitmapImageRep.FileType.png, properties: [:]) else {
    print("ERROR: PNG conversion failed")
    exit(1)
}

do {
    try pngData.write(to: URL(fileURLWithPath: outputPath), options: NSData.WritingOptions.atomic)
    print("CAPTURED: \\(outputPath)")
} catch {
    print("ERROR: Write failed - \\(error)")
    exit(1)
}
"""

    def run_on_imac(self, command: str) -> Tuple[int, str, str]:
        """Run command on iMac via SSH"""
        try:
            result = subprocess.run(
                ["ssh", self.imac_host, command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Timeout"
        except Exception as e:
            return 1, "", str(e)

    def navigate_to_route(self, route: str) -> bool:
        """Navigate to route using AppleScript + clipboard"""
        full_url = f"{self.vite_url}{route}"

        # Use pbcopy + Cmd+V to avoid osascript typing issues
        commands = [
            f'echo -n "{full_url}" | pbcopy',
            'osascript -e \'tell application "System Events" to key code 37 using command down\'',
            'sleep 0.3',
            'osascript -e \'tell application "System Events" to key code 9 using command down\'',
            'sleep 0.3',
            'osascript -e \'tell application "System Events" to key code 36\'',
            'sleep 2',
        ]

        bash_script = " && ".join(commands)
        returncode, stdout, stderr = self.run_on_imac(bash_script)

        return returncode == 0

    def capture_window(self, output_filename: str) -> bool:
        """Capture current window to file"""
        swift_code = self.create_swift_capture_script()
        output_path = f"{self.imac_output_dir}/{output_filename}"

        # Create a temporary Swift file with the code and run it
        import tempfile
        import os

        # Write script to temp file locally, then scp to iMac
        with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
            f.write(swift_code)
            temp_local_file = f.name

        try:
            temp_imac_file = f"/tmp/cap_{int(time.time())}.swift"

            # Copy Swift script to iMac
            try:
                subprocess.run(
                    ["scp", temp_local_file, f"{self.imac_host}:{temp_imac_file}"],
                    capture_output=True,
                    timeout=10
                )
            except Exception as e:
                print(f"      ❌ Failed to copy Swift script: {e}")
                return False

            # Run Swift capture on iMac
            capture_cmd = f'swift {temp_imac_file} "{output_path}"'
            rc, stdout, stderr = self.run_on_imac(capture_cmd)

            # Clean up on iMac
            self.run_on_imac(f'rm -f {temp_imac_file}')

            if rc == 0 and "CAPTURED" in stdout:
                return True
            else:
                if stderr:
                    print(f"        stderr: {stderr[:100]}")

        finally:
            # Clean up local temp file
            try:
                os.unlink(temp_local_file)
            except:
                pass

        return False

    def copy_screenshots_to_macbook(self) -> int:
        """Copy captured screenshots from iMac to MacBook"""
        Path(self.local_output_dir).mkdir(parents=True, exist_ok=True)

        print(f"\n[*] Copying screenshots to MacBook...")
        print(f"    From: {self.imac_host}:{self.imac_output_dir}")
        print(f"    To: {self.local_output_dir}")

        try:
            result = subprocess.run(
                ["scp", f"{self.imac_host}:{self.imac_output_dir}/*.png", self.local_output_dir],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Count copied files
                copied = len(list(Path(self.local_output_dir).glob("*.png")))
                print(f"    ✅ Copied {copied} screenshots")
                return copied
            else:
                print(f"    ⚠️ scp warning: {result.stderr[:100]}")
                return 0

        except Exception as e:
            print(f"    ❌ Error: {e}")
            return 0

    def verify_screenshots(self) -> int:
        """Verify captured screenshots"""
        screenshots = list(Path(self.local_output_dir).glob("*.png"))
        screenshots.sort()

        print(f"\n[+] Captured Screenshots ({len(screenshots)}):")
        for screenshot in screenshots:
            size_mb = screenshot.stat().st_size / (1024 * 1024)
            print(f"    {screenshot.name:30} ({size_mb:.2f} MB)")

        return len(screenshots)

    def run(self) -> bool:
        """Main execution flow"""
        print("[*] FLUXION Screenshot Capture — Remote SSH")
        print(f"[*] iMac host: {self.imac_host}")
        print(f"[*] Output directory: {self.local_output_dir}")

        # Test SSH connection
        print("\n[*] Testing SSH connection...")
        rc, _, _ = self.run_on_imac("echo 'OK'")
        if rc != 0:
            print(f"[!] ERROR: Cannot connect to {self.imac_host}")
            return False

        print("[+] SSH connection OK")

        # Create output directory on iMac
        print(f"\n[*] Creating output directory on iMac: {self.imac_output_dir}")
        self.run_on_imac(f"mkdir -p {self.imac_output_dir}")

        # Capture each route
        print(f"\n[*] Capturing {len(self.routes)} screenshots...")
        success_count = 0

        for route, filename, description in self.routes:
            print(f"\n[→] {filename}")
            print(f"    Route: {route}")
            print(f"    Description: {description}")

            try:
                # Navigate
                print(f"    [1/3] Navigating...")
                if not self.navigate_to_route(route):
                    print(f"    [1/3] ⚠️ Navigation may have failed (non-critical)")

                # Wait for page load
                time.sleep(1.5)

                # Capture
                print(f"    [2/3] Capturing...")
                if self.capture_window(filename):
                    print(f"    [3/3] ✅ Captured")
                    success_count += 1
                else:
                    print(f"    [3/3] ❌ Capture failed")

            except Exception as e:
                print(f"    ❌ Error: {e}")

            # Small delay between captures to avoid overwhelming the app
            time.sleep(0.5)

        print(f"\n[+] Capture phase complete: {success_count}/{len(self.routes)} successful")

        # Copy to MacBook
        copied = self.copy_screenshots_to_macbook()

        # Verify
        verified = self.verify_screenshots()

        print(f"\n[✅] COMPLETE")
        print(f"    Captured on iMac: {success_count}")
        print(f"    Copied to MacBook: {copied}")
        print(f"    Verified locally: {verified}")

        return verified > 0


def main():
    capturer = FluxionScreenshotCapturer(
        imac_host="imac",
        local_output_dir="landing/screenshots"
    )

    success = capturer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
