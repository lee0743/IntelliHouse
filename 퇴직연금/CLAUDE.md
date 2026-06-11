# CLAUDE.md — 퇴직연금 볼트

This file provides guidance to Claude Code when working inside the `퇴직연금/` folder.
This folder is a standalone Obsidian vault for studying 퇴직연금 (retirement pension).

## Important

The `old/` directory at the repository root contains archived files. **Do not modify or reference those files.**

## Vault Structure

| Folder | Purpose |
|--------|---------|
| `Home/` | Dashboard and entry point |
| `Inbox/` | Quick capture — unprocessed notes and quiz answer files |
| `Notes/` | Permanent notes (one concept per note) |
| `Topics/` | Map of Content (MOC) file |
| `Resources/` | Source notes, learning profile |
| `Templates/` | Note and MOC templates for Obsidian |
| `scripts/` | Automation scripts (quiz, grading, agents) |
| `.obsidian/` | Obsidian configuration — do not edit manually |

New notes default to `Inbox/`. Processed notes move to `Notes/`.

## Scripts

Run from inside `퇴직연금/` (or set `VAULT_PATH` env var):

```bash
# 퇴직연금 문제지 생성
python scripts/quiz_session.py --template 기본

# 답안 채점
python scripts/quiz_session.py --grade "Inbox/퇴직연금 답안 (기본) YYYY-MM-DD.md"

# 채점 + 학습 프로파일 업데이트
python scripts/quiz_session.py --grade "..." --save-memory
```
