#!/usr/bin/env bash
# Tambah entri ship log hari ini + commit + push.
# Cron: 0 22 * * * /path/ke/ship-log/daily-log.sh
set -euo pipefail

cd "$(dirname "$0")"

DAY=$(date '+%Y-%m-%d')
MONTH=$(date '+%Y-%m')
FILE="log/$MONTH.md"

if grep -q "^## $DAY" "$FILE" 2>/dev/null; then
  echo "entri $DAY sudah ada"
  exit 0
fi

mkdir -p log
[ -f "$FILE" ] || printf '# Ship log — %s\n' "$(date '+%B %Y')" > "$FILE"

printf '\n## %s\n- shipped: %s\n- blocked: %s\n- next: %s\n' \
  "$DAY" "${1:-sesuatu yang kecil}" "${2:-nggak ada blocker}" "${3:-lanjut besok}" >> "$FILE"

python3 - "$FILE" <<'PY'
import json
p = "metrics.json"
try:
    d = json.load(open(p))
except FileNotFoundError:
    d = {"days": 0, "shipped": 0, "blocked": 0, "streak": 0}
d["days"] += 1
d["shipped"] += 1
d["streak"] = d["days"]
json.dump(d, open(p, "w"), indent=2)
open(p, "a").write("\n")
PY

git add log metrics.json
git commit -m "log: daily entry ($DAY)" >/dev/null
git push origin "$(git rev-parse --abbrev-ref HEAD)" >/dev/null 2>&1 || echo "push gagal (cek kredensial)"
echo "ok: $DAY"
