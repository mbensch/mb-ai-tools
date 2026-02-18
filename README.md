# MB AI Tools

A plugin marketplace for **Factory (Droid)** and **Claude Code** -- skills, commands, and hooks that work across both AI coding agents from a single repository.

## Overview

This marketplace provides plugins for Jira integration, git worktree management, PR workflows, and session tooling. Most plugins work on both platforms; a few use Droid-specific hooks and are noted as such below.

## Installation

### Factory (Droid)

```bash
droid plugin marketplace add https://github.com/mbensch/mb-ai-tools
droid plugin install pr-tools@mb-ai-tools
droid plugin install jira-tools@mb-ai-tools
droid plugin install manual-worktrees@mb-ai-tools
```

### Claude Code

```bash
/plugin marketplace add https://github.com/mbensch/mb-ai-tools
/plugin install pr-tools@mb-ai-tools
/plugin install jira-tools@mb-ai-tools
/plugin install manual-worktrees@mb-ai-tools
```

Browse all available plugins: `/plugins` (Droid) or `/plugin marketplace list` (Claude Code).

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

On-demand git worktree creation via a slash command.

**Features:**
- `/worktree` - Create a worktree for the current session on demand
- Session isolation with dedicated branches
- Flexible: use alongside or instead of automatic worktree creation

### worktrees-skill

A skill for systematic git worktree management with smart directory selection and safety verification.

**Features:**
- Auto-invoked skill for creating isolated worktrees
- Smart directory selection (`.worktrees/`, `worktrees/`, or `../droid-worktrees/`)
- Safety verification to ensure directories are gitignored
- Auto-detection of project setup commands (npm, cargo, pip, go mod)
- Baseline test verification before starting work

### jira-tools

Jira skills for managing tickets, creating stories, and filing bugs via Atlassian MCP tools.

**Skills:**
- `manage-jira` - General-purpose ticket management (view, edit, search, transition, custom fields)
- `create-jira-story` - Structured Story creation with consistent formatting
- `create-jira-bug` - Structured Bug creation with diagnostic formatting

**Requires:** [Atlassian MCP integration](https://app.factory.ai/settings/integrations) configured in Factory settings.

### pr-tools

Skills for safe and consistent pull request workflows.

**Skills:**
- `safe-pr-workflow` - Checks branch state before git push and PR creation to avoid silently pushing to dead PRs
- `create-pr` - Creates PRs with consistent formatting, Jira-aware branch naming, and repo template support

## Platform Compatibility

| Plugin | Factory (Droid) | Claude Code |
|--------|:-:|:-:|
| droid-receipts | Yes | No (Droid-only hooks) |
| auto-worktrees | Yes | No (Droid-only hooks) |
| manual-worktrees | Yes | Yes |
| worktrees-skill | Yes | Yes |
| jira-tools | Yes | Yes |
| pr-tools | Yes | Yes |

Plugins that rely on Droid-specific lifecycle hooks (`SessionStart`, `SessionEnd`) and environment variables are not available on Claude Code. Plugins using skills and commands work identically on both platforms.

## Author's Notes

### Choosing a Worktree Plugin

**Do not install both `auto-worktrees` and `manual-worktrees`.** They serve the same purpose with different approaches - pick one based on your workflow:

- **auto-worktrees** - Best if you want every Droid session to automatically get its own isolated worktree. Great for "set it and forget it" workflows where you always want session isolation.

- **manual-worktrees** - Best if you prefer control over when worktrees are created. Use `/worktree` when you need isolation. Start here if you're unsure.

### Recommended Setup

```bash
# Option A: Automatic worktrees + skill
droid plugin install auto-worktrees@mb-ai-tools
droid plugin install worktrees-skill@mb-ai-tools

# Option B: Manual worktrees + skill (recommended if unsure)
droid plugin install manual-worktrees@mb-ai-tools
droid plugin install worktrees-skill@mb-ai-tools
```

The `worktrees-skill` plugin complements either choice by giving Droid a deeper understanding of worktree best practices for complex implementation tasks.

## Adding New Plugins

To add a new plugin to this marketplace:

1. Create a new directory under `plugins/your-plugin-name/`
2. Add a `.factory-plugin/plugin.json` manifest
3. If the plugin is compatible with Claude Code, also add `.claude-plugin/plugin.json`
4. Add your plugin files (hooks.json, skills/, hooks/, etc.)
5. Update `.factory-plugin/marketplace.json` to register the plugin
6. If Claude Code compatible, also update `.claude-plugin/marketplace.json`
7. Commit and push

**Example structure:**
```
plugins/
└── your-plugin/
    ├── .factory-plugin/
    │   └── plugin.json
    ├── .claude-plugin/        # Add for Claude Code compatibility
    │   └── plugin.json
    ├── skills/
    ├── commands/
    └── README.md
```

The `skills/` and `commands/` directories are shared between both platforms. Hooks and droids/agents use different formats per platform.

## Contributing

Contributions welcome! To contribute:

1. Fork this repository
2. Add your plugin under `plugins/`
3. Update the marketplace.json
4. Submit a pull request

## License

Plugins in this marketplace are available under the MIT License.
