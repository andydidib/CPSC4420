import re, json, sys

log_path = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) > 2 else "scans.jsonl"

line_re = re.compile(r"LogBlueprintUserMessages: \[BP_Lidar\] (.*)$")
prefix_re = re.compile(r"^scan=(\d+);pos=([-\d.eE+]+),([-\d.eE+]+),([-\d.eE+]+);(.*)$")

good = bad = 0
with open(log_path, encoding="utf-8", errors="replace") as f, open(out_path, "w") as out:
    for line in f:
        m = line_re.search(line.rstrip("\r\n"))
        if not m:
            continue
        body = m.group(1).strip()
        scan, pos = None, None
        p = prefix_re.match(body)
        if p:
            scan = int(p.group(1))
            pos = [float(p.group(2)), float(p.group(3)), float(p.group(4))]
            body = p.group(5)
        else:
            continue  # skip lines without the expected prefix
        body = body.rstrip(",") + "]"      # drop trailing comma, close the outer list
        try:
            points = json.loads(body)
        except json.JSONDecodeError:
            bad += 1                        # truncated or malformed line
            continue
        out.write(json.dumps({"scan": scan, "pos": pos, "points": points}) + "\n")
        good += 1

print(f"wrote {good} scans, skipped {bad} bad lines -> {out_path}")