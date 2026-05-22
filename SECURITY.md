# Security — TraceNeuro

- Do not commit `.env`, API keys, or scraped corpus (`data/human/blogs-pre2012/` HTML/manifest).
- Production: set `CORS_ALLOW_ORIGINS` to your dashboard origin (comma-separated).
- Local path batch: only enable `NEUROTRACER_ALLOW_LOCAL_PATHS` on trusted dev hosts.

See `../SECURITY.md` in the arnav folder for portfolio-wide notes.
