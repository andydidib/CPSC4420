"""
Extract drone position log lines from an Unreal Engine log file into a CSV.

Usage (from the project folder):
    python extract_poslog.py                      # uses the newest .log in Saved/Logs
    python extract_poslog.py path/to/MyProject.log
    python extract_poslog.py path/to/MyProject.log output.csv

Each log line written by the drone looks like:
    ...LogBlueprintUserMessages: [BP_DronePawn_C_0] POSLOG,12.50,A,8.42,-3.10,2.75
and becomes a CSV row:
    12.50,A,8.42,-3.10,2.75
"""

import csv
import glob
import os
import sys

MARKER = "POSLOG,"
HEADER = ["time_s", "waypoint", "x_m", "y_m", "z_m"]


def find_newest_log():
    logs = glob.glob(os.path.join("Saved", "Logs", "*.log"))
    if not logs:
        sys.exit("No .log files found in Saved/Logs. Run this from your project folder, "
                 "or pass the log file path as an argument.")
    return max(logs, key=os.path.getmtime)


def main():
    log_path = sys.argv[1] if len(sys.argv) > 1 else find_newest_log()
    out_path = sys.argv[2] if len(sys.argv) > 2 else "position_log.csv"

    rows = []
    with open(log_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            idx = line.find(MARKER)
            if idx == -1:
                continue
            values = line[idx + len(MARKER):].strip().split(",")
            if len(values) == 5:
                rows.append(values)

    if not rows:
        sys.exit(f"No POSLOG lines found in {log_path}. Run a mission with P first.")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows from {log_path} to {out_path}")


if __name__ == "__main__":
    main()
