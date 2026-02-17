# Droid Receipts

A Factory plugin that generates visual receipts (SVG) for Droid sessions when they end.

Inspired by [claude-receipts](https://github.com/chrishutchinson/claude-receipts).

## Installation

### From Local Directory

```bash
# Enable the plugin in your settings
droid plugins add /path/to/droid-receipts/.factory/plugins/droid-receipts
```

Or manually add to `~/.factory/settings.json`:

```json
{
  "enabledPlugins": {
    "droid-receipts@local": true
  }
}
```

## How It Works

1. **SessionEnd Hook**: When a Droid session ends, the plugin is triggered
2. **Data Collection**: Reads session settings and transcript for token counts, model info, and timestamps
3. **Receipt Generation**: Creates an SVG receipt with thermal printer styling
4. **Output**: Saves to `~/.factory/receipts/{session-id}.svg` and opens in browser (macOS)

## Receipt Contents

- Factory logo
- Session title
- Project location
- Date/time
- Duration
- Model used
- Token breakdown:
  - Input tokens
  - Output tokens
  - Cache write tokens
  - Cache read tokens
- Estimated cost ($1 per 1M tokens)

## Configuration

Optional config file at `~/.factory/droid-receipts.json`:

```json
{
  "output_dir": "~/.factory/receipts",
  "auto_open": true
}
```

## Example Output

```
================================
       [FACTORY LOGO]
         FACTORY
      DROID RECEIPT
================================

Location....................my-project
Session.....................Fix auth bug
Date........................2026-02-16 22:31:45
Duration....................2m 15s

================================
ITEM                    QTY    PRICE
----------------------------------------
Claude Opus 4.6
  Input tokens        113,575      $0.11
  Output tokens         2,287      $0.00
  Cache write          96,562      $0.10
  Cache read          578,832      $0.58
----------------------------------------
TOTAL                               $0.12
================================

CASHIER: Claude Opus 4.6

Thank you for building!

----------------------------------------
github.com/Factory-AI/factory
================================
```

## License

MIT
