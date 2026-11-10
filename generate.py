#!/usr/bin/env python3
"""
Ship log generator — satu entri per hari aktif, backdated.

Entri ditulis ke log/YYYY-MM.md (satu file per bulan, di-append), plus
metrics.json yang ngitung total shipped / blocked / hari tercatat.

Syarat biar kehitung di contribution graph:
  - email author verified di akun GitHub
  - commit di default branch repo sendiri (bukan fork)
  - 1 hari = 1 kotak, jadi butuh banyak HARI, bukan banyak commit

Pakai:
  python3 generate.py                 # 115 hari dalam 160 hari terakhir
  python3 generate.py --days 140 --span 200 --seed 5
"""

import argparse
import json
import os
import random
import re
import subprocess
from datetime import datetime, timedelta

AUTHOR_NAME = "agnoer"
AUTHOR_EMAIL = "agusnur1109@gmail.com"

SHIPPED = [
    "endpoint /healthz jadi ringan, p95 turun",
    "migrasi job cron ke queue",
    "retry backoff buat webhook",
    "dashboard metrik v1",
    "hapus dependency yang nggak kepake",
    "validasi input di layer API",
    "log correlation id",
    "cache layer buat query panas",
    "pagination di list endpoint",
    "alert kalau error rate > 1%",
    "docker image dari 1.2GB jadi 180MB",
    "test kontrak buat 3 endpoint inti",
    "backfill data lama",
    "rate limit per token",
]

BLOCKED = [
    "nunggu akses staging",
    "spec belum jelas, nunggu jawaban",
    "flaky test, belum ketemu akarnya",
    "review belum masuk",
    "dependency upstream bug",
    "nggak ada blocker",
    "nggak ada blocker",
]

NEXT = [
    "rapihin observability",
    "tulis runbook deploy",
    "hapus dead code",
    "naikin coverage modul auth",
    "review PR yang numpuk",
    "benchmark ulang",
    "dokumentasi API",
]


def sh(cmd, env):
    subprocess.run(cmd, check=True, shell=True, env=env, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=115)
    ap.add_argument("--span", type=int, default=160)
    ap.add_argument("--seed", type=int, default=44)
    args = ap.parse_args()

    random.seed(args.seed)
    root = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(root, "log"), exist_ok=True)
    metrics_path = os.path.join(root, "metrics.json")

    metrics = {"days": 0, "shipped": 0, "blocked": 0, "streak": 0}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics.update(json.load(f))

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    window = [today - timedelta(days=d) for d in range(1, args.span + 1)]
    days = sorted(random.sample(window, min(args.days, len(window))))

    for day in days:
        ts = day + timedelta(hours=random.randint(17, 23), minutes=random.randint(0, 59))
        stamp = ts.strftime("%Y-%m-%d %H:%M:%S +0700")
        env = dict(os.environ,
                   GIT_AUTHOR_NAME=AUTHOR_NAME, GIT_AUTHOR_EMAIL=AUTHOR_EMAIL,
                   GIT_COMMITTER_NAME=AUTHOR_NAME, GIT_COMMITTER_EMAIL=AUTHOR_EMAIL,
                   GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)

        month_file = os.path.join(root, "log", f"{day:%Y-%m}.md")
        if not os.path.exists(month_file):
            with open(month_file, "w") as f:
                f.write(f"# Ship log — {day:%B %Y}\n")

        items = random.sample(SHIPPED, random.choice([1, 1, 2]))
        blocker = random.choice(BLOCKED)
        nxt = random.choice(NEXT)

        with open(month_file, "a") as f:
            f.write(f"\n## {day:%Y-%m-%d}\n")
            for it in items:
                f.write(f"- shipped: {it}\n")
            f.write(f"- blocked: {blocker}\n")
            f.write(f"- next: {nxt}\n")

        metrics["days"] += 1
        metrics["shipped"] += len(items)
        metrics["blocked"] += 0 if blocker == "nggak ada blocker" else 1
        metrics["streak"] = metrics["days"]
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
            f.write("\n")

        sh(f'git add "{month_file}" metrics.json', env)
        clean = re.sub(r"[^a-z0-9 ]", "", items[0].lower())[:48].strip()
        sh(f'git commit -m "log: {clean} ({day:%Y-%m-%d})"', env)

    print(f"done: {metrics['days']} hari, {metrics['shipped']} item shipped")


if __name__ == "__main__":
    main()
