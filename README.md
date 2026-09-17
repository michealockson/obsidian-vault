# Obsidian Vault Bot

> 🚧 WORK IN PROGRESS

AI-powered auto-organizer for an Obsidian vault: enriches new notes with
better titles, consistent tags (drawn from a maintained taxonomy), and
semantic links to related notes. Runs locally on a ThinkCentre M710q
(16GB RAM, CPU-only) via Ollama. Companion project to `perso_assistant`,
sharing the same box but kept as a separate repo.

## Status

| Phase | Status |
|---|---|
| Phase 0 — Foundation (folders, git, GitHub) | In progress |
| Phase 1 — File watcher | Planned |
| Phase 2 — Chunked ingestion pipeline | Planned |
| Phase 3 — Embeddings & semantic linking | Planned |
| Phase 4 — Tag taxonomy engine | Planned |
| Phase 5 — Review & apply workflow | Planned |
| Phase 6 — Orchestration | Planned |
| Phase 7 — Hardening | Planned |
| Phase 8 — Discord integration (appendix) | Planned |

## Architecture

```text
Laptop (Obsidian + Web Clipper)
      ↓  saves to raw/
Syncthing
      ↓
ThinkCentre raw/  →  archived copy  →  chunked ingestion (Ollama)
      ↓
Tag taxonomy (tag_bank.yaml) + embeddings (LanceDB)
      ↓
processed/  →  review window (~20 min)  →  Syncthing  →  back to laptop
```

## Setup

```bash
cp .env.example .env
# edit .env if values differ from your setup
```

Requires: Ollama running locally with `qwen2.5:7b-instruct` and
`nomic-embed-text` pulled; Syncthing configured between this machine
and the laptop for `raw/` and `processed/`.
