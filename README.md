# Droid Plugins

My personal Factory plugin marketplace - a collection of plugins and tools I've built for Droid.

## Overview

This is my personal marketplace for distributing Droid plugins I've created. Built as a [Factory Enterprise Plugin Registry](https://docs.factory.ai/enterprise/enterprise-plugin-registry), it follows the Git-based marketplace format that Factory uses for plugin distribution.

## Installation

Add this marketplace to Factory:

```bash
droid plugin marketplace add https://github.com/mbensch/mbensch-droid-plugins
```

Then install plugins:

```bash
droid plugin install droid-receipts@mbensch-droid-plugins
droid plugin install auto-worktrees@mbensch-droid-plugins
droid plugin install manual-worktrees@mbensch-droid-plugins
droid plugin install worktrees@mbensch-droid-plugins
```

Or browse available plugins via the UI:

```bash
/plugins
```

## Available Plugins

### droid-receipts

Generate visual receipts for Droid sessions showing token usage and costs.

**Features:**
- Automatic receipt generation when sessions end (via SessionEnd hook)
- HTML and SVG output formats
- Factory Token Usage calculation with model multipliers
- Cache token discounting (billed at 1/10 rate)
- Star Wars-style droid cashier names
- Cost breakdown by token type

### auto-worktrees

Automatically create and manage git worktrees for Droid sessions, isolating each session on its own branch.

**Features:**
- Creates isolated worktree for each session on `droid/{session_id}` branch
- Worktrees created at `../droid-worktrees/{repo}-{session_id}/`
- Automatic cleanup of worktrees older than 14 days
- Prevents conflicts between concurrent Droid sessions
- Works on macOS and Linux

### manual-worktrees

On-demand git worktree creation and cleanup via slash commands.

**Features:**
- `/worktree` - Create a worktree for the current session on demand
- `/clean-worktrees` - Interactively list and clean up existing worktrees
- Session isolation with dedicated branches
- Flexible: use alongside or instead of automatic worktree creation

### worktrees

A skill for systematic git worktree management with smart directory selection and safety verification.

**Features:**
- Droid-invocable skill for creating isolated worktrees
- Smart directory selection (`.worktrees/`, `worktrees/`, or `../droid-worktrees/`)
- Safety verification to ensure directories are gitignored
- Auto-detection of project setup commands (npm, cargo, pip, go mod)
- Baseline test verification before starting work

## Adding New Plugins

To add a new plugin to this marketplace:

1. Create a new directory under `plugins/your-plugin-name/`
2. Add a `.factory-plugin/plugin.json` manifest
3. Add your plugin files (hooks.json, skills/, hooks/, etc.)
4. Update `.factory-plugin/marketplace.json` to register the plugin
5. Commit and push

**Example structure:**
```
plugins/
└── your-plugin/
    ├── .factory-plugin/
    │   └── plugin.json
    ├── hooks.json
    ├── hooks/
    └── README.md
```

**Update marketplace.json:**
```json
{
  "plugins": [
    {
      "name": "your-plugin",
      "description": "Plugin description",
      "source": "./plugins/your-plugin",
      "category": "productivity"
    }
  ]
}
```

## Contributing

Contributions welcome! To contribute:

1. Fork this repository
2. Add your plugin under `plugins/`
3. Update the marketplace.json
4. Submit a pull request

## License

Plugins in this marketplace are available under the MIT License.
