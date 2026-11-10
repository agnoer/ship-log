# ship-log

Catatan apa yang **kelar** tiap hari. Bukan to-do list — to-do list itu harapan,
file ini cuma nyatet yang beneran selesai.

```
log/YYYY-MM.md   # entri harian per bulan
metrics.json     # total hari, item shipped, blocked
```

Format satu entri:

```md
## 2026-06-04
- shipped: retry backoff buat webhook
- blocked: review belum masuk
- next: rapihin observability
```

## Isi repo

| File | Fungsi |
|---|---|
| `log/*.md` | entri harian, satu file per bulan |
| `metrics.json` | rekap shipped / blocked / hari |
| `generate.py` | backfill hari kosong |
| `daily-log.sh` | entri hari ini + commit, buat cron |

## Pakai

```bash
python3 generate.py --days 115 --span 160   # backfill
./daily-log.sh                              # entri hari ini
```

Cron:

```bash
crontab -e
0 22 * * * /path/ke/ship-log/daily-log.sh
```
