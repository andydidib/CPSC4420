"""
Pull the LiDAR scans out of an Unreal Engine log file into one clean CSV.

Usage (run from your project folder, next to the .uproject file):
    python extract_lidar.py                       # uses the newest .log in Saved/Logs
    python extract_lidar.py path/to/Test.log
    python extract_lidar.py path/to/Test.log lidar_scans.csv

Output: lidar_scans.csv with one row per LiDAR hit point:
    scan, log_time, drone_x, drone_y, drone_z, drone_roll, drone_pitch, drone_yaw,
    point_x, point_y, point_z
Positions are in Unreal units (centimeters), rotations in degrees.

Works with both log formats BP_Lidar has used:
    new:  scan=5;pos=120,-40,250;rot=0,0,90;X=812.4 Y=-30.2 Z=95.0;X=...
    old:  scan=22;pos=0,0,226;rot=0,0,0;[[59.87,0.0,-16.04],[59.83,2.08,-16.04],...
"""

import csv
import glob
import os
import re
import sys

NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
HEADER_RE = re.compile(
    r"scan=(\d+);pos=(" + NUM + r"),(" + NUM + r"),(" + NUM + r");rot=("
    + NUM + r"),(" + NUM + r"),(" + NUM + r")"
)
TIME_RE = re.compile(r"^\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\]")
POINT_NEW_RE = re.compile(r"X=(" + NUM + r")\s+Y=(" + NUM + r")\s+Z=(" + NUM + r")")
POINT_OLD_RE = re.compile(r"\[(" + NUM + r"),(" + NUM + r"),(" + NUM + r")\]")

COLUMNS = ["scan", "log_time", "drone_x", "drone_y", "drone_z",
           "drone_roll", "drone_pitch", "drone_yaw", "point_x", "point_y", "point_z"]


def find_newest_log():
    logs = glob.glob(os.path.join("Saved", "Logs", "*.log"))
    if not logs:
        sys.exit("No .log files found in Saved/Logs. Run this from your project folder, "
                 "or pass the log file path as an argument.")
    return max(logs, key=os.path.getmtime)


def read_entries(log_path):
    """Yield (log_time, text) for each log entry. Entries can span several physical lines."""
    time, parts = None, []
    with open(log_path, encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\r\n")
            m = TIME_RE.match(line)
            if m:
                if parts:
                    yield time, "".join(parts)
                time, parts = m.group(1), [line]
            elif parts:
                parts.append(line)
    if parts:
        yield time, "".join(parts)


def main():
    log_path = sys.argv[1] if len(sys.argv) > 1 else find_newest_log()
    out_path = sys.argv[2] if len(sys.argv) > 2 else "lidar_scans.csv"

    scans = points = 0
    with open(out_path, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(COLUMNS)
        for log_time, text in read_entries(log_path):
            if "BP_Lidar" not in text:
                continue
            header = HEADER_RE.search(text)
            if not header:
                continue
            scan_info = list(header.groups())
            rest = text[header.end():]
            hits = POINT_NEW_RE.findall(rest) or POINT_OLD_RE.findall(rest)
            scans += 1
            for x, y, z in hits:
                writer.writerow([scan_info[0], log_time] + scan_info[1:] + [x, y, z])
                points += 1

    if scans == 0:
        os.remove(out_path)
        sys.exit(f"No LiDAR scans found in {log_path}. Press Play so the drone scans, then try again.")
    print(f"Wrote {points} points from {scans} scans ({log_path}) to {out_path}")


if __name__ == "__main__":
    main()
