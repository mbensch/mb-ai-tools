# Worktrees

A Factory plugin that provides a skill for systematic git worktree management with smart directory selection and safety verification.

## Installation

### From Marketplace (Recommended)

```bash
# Add the marketplace
droid plugin marketplace add https://github.com/mbensch/mbensch-droid-plugins

# Install the plugin
droid plugin install worktrees@mbensch-droid-plugins
```

Or use the interactive UI: `/plugins` → Marketplaces → Add marketplace → enter URL

### From Local Directory (Development)

```bash
droid plugin marketplace add /path/to/mbensch-droid-plugins
droid plugin install worktrees@mbensch-droid-plugins
```

## Skills

### `using-worktrees`

A Droid-invocable skill for creating isolated git worktrees. Droid will automatically use this skill when:

- Starting feature work that needs isolation from the current workspace
- Before executing implementation plans
- When setting up parallel development environments

**Features:**
- Smart directory selection (`.worktrees/`, `worktrees/`, or `../droid-worktrees/`)
- Safety verification to ensure worktree directories are gitignored
- Auto-detection of project setup commands (npm, cargo, pip, go mod)
- Baseline test verification before starting work

**Manual invocation:**
```
Use the using-worktrees skill to set up an isolated workspace.
```

## Plugin Structure

```
worktrees/
├── .factory-plugin/
│   └── plugin.json
├── skills/
│   └── using-worktrees/
│       └── SKILL.md
└── README.md
```

## Related Plugins

- **auto-worktrees** - Automatically creates worktrees on session start via hooks
- **manual-worktrees** - On-demand `/worktree` and `/clean-worktrees` commands

## License

MIT
