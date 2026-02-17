# Droid Receipts

Factory plugin that generates visual receipts for Droid sessions.

## Structure

```
.factory/plugins/droid-receipts/
├── plugin.json              # Plugin manifest with SessionEnd hook
├── hooks/
│   └── generate-receipt.py  # Main hook script
└── assets/                  # (optional) additional assets
```

## How It Works

1. SessionEnd hook triggers when a Droid session ends
2. Hook reads session data from:
   - stdin (session_id, transcript_path, cwd)
   - `{session-id}.settings.json` (token counts, model)
   - transcript JSONL (title, timestamps)
3. Generates SVG receipt with thermal printer styling
4. Saves to `~/.factory/receipts/{session-id}.svg`
5. Opens in browser (macOS)

## Testing

```bash
echo '{"session_id": "test", "transcript_path": "~/.factory/sessions/...", "cwd": "/path/to/project"}' | python3 .factory/plugins/droid-receipts/hooks/generate-receipt.py
```

## Development

- Edit `hooks/generate-receipt.py` for receipt logic
- Edit `plugin.json` for hook configuration
- Cost calculation: `$1 per 1M tokens`
