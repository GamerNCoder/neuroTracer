# Local blog dataset (1000-post target)

## Why 1000 in batches?

- **Wayback rate limits** — default 1.25s between requests (~20–30 min per 100 posts).
- **Resumable** — each batch appends to `manifest.jsonl`; safe to stop and continue.
- **Training** — larger corpus improves calibration stability vs 270 posts.

## Scrape in batches

```bash
cd arnav/neurotracer
source venv/bin/activate

# 100 posts per run until 1000 total (re-run ~10 times)
python3 scripts/scrape_batches.py --target 1000 --batch-size 100 --extended

# Or one batch at a time
python3 scripts/scrape_batches.py --target 1000 --batch-size 100 --extended --once
```

Flags:

| Flag | Default | Meaning |
|------|---------|---------|
| `--target` | 1000 | Stop when corpus has this many ok posts |
| `--batch-size` | 100 | Max **new** saves per invocation |
| `--extended` | off | 41 CDX patterns (20 base + 21 extra + LiveJournal) |
| `--delay` | 1.25 | Seconds between Wayback requests |

Logs: `data/human/blogs-pre2012/batches.jsonl`

## Build dataset for training

```bash
python3 scripts/build_local_dataset.py
```

Creates:

```
data/human/blogs-pre2012/dataset/
  dataset.jsonl    # full records (text + metadata, label=human)
  text/{id}.txt    # plain text per post
  stats.json
  splits.json      # train/val/test ids (90/5/5)
```

## Retrain calibration

```bash
make tune-blogs
```

Uses all posts in manifest (including new batches).

## Git

HTML and `dataset/` stay **local** (gitignored). Commit only code + `calibration.json` after tuning.
