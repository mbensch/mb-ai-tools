# Manual Worktrees

A Factory plugin that provides on-demand git worktree creation and cleanup via slash commands.

## Installation

### From Marketplace (Recommended)

```bash
# Add the marketplace
droid plugin marketplace add https://github.com/mbensch/mbensch-droid-plugins

# Install the plugin
droid plugin install manual-worktrees@mbensch-droid-plugins
```

Or use the interactive UI: `/plugins` → Marketplaces → Add marketplace → enter URL

### From Local Directory (Development)

```bash
droid plugin marketplace add /path/to/mbensch-droid-plugins
droid plugin install manual-worktrees@mbensch-droid-plugins
```

## Commands

### `/worktree`

Creates a git worktree for the current session:

1. Detects the repository name and current branch
2. Creates a worktree at `{project}/../droid-worktrees/{repo}-{session-id}/`
3. Creates a new branch `droid/{session-id}` based on the current branch
4. Reports the worktree location for Droid to work in

**Usage:**
```
/worktree
```

### `/clean-worktrees`

Lists all droid worktrees and lets you select which to remove:

1. Lists all worktrees in `../droid-worktrees/` matching the current repo
2. Shows each with: directory name, branch, last modified date, age
3. Prompts you to select one, multiple, or all to remove
4. Removes selected worktrees and their `droid/*` branches

**Usage:**
```
/clean-worktrees
```

## Benefits

- **On-Demand Control**: Create worktrees only when you need them
- **Interactive Cleanup**: Choose exactly which worktrees to remove
- **Session Isolation**: Each worktree has its own branch for clean history
- **Flexible**: Use alongside or instead of automatic worktree creation

## Plugin Structure

```
manual-worktrees/
├── .factory-plugin/
│   └── plugin.json
├── commands/
│   ├── worktree.md
│   └── clean-worktrees.md
└── README.md
```

## Requirements

- Git 2.5+ (for worktree support)
- Works on macOS and Linux

## See Also

For automatic worktree creation on session start, see the `auto-worktrees` plugin.

## License

MIT
