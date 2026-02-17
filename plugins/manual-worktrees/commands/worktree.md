---
description: Create a git worktree for the current session
disable-model-invocation: true
---

Create a git worktree for this session. Follow these steps exactly:

1. Check if this is a git repository. If not, report that worktrees require a git repo and stop.

2. Get the repo name:
   ```bash
   basename "$(git rev-parse --show-toplevel)"
   ```

3. Get the current branch:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```

4. Get the session ID from the current session context (it's available in the session metadata).

5. Construct the worktree path:
   - Directory: `{project_dir}/../droid-worktrees/{repo_name}-{session_id}/`
   - Branch name: `droid/{session_id}`

6. Check if the worktree already exists:
   ```bash
   [ -d "{worktree_dir}" ]
   ```
   If it exists, report: "Worktree already exists at: {path} on branch: {branch}. Work in this worktree."

7. Create the worktree:
   ```bash
   git worktree add -b "droid/{session_id}" "{worktree_dir}" "{current_branch}"
   ```

8. Report success:
   "Git worktree created at: {worktree_dir} on branch: droid/{session_id} (based on {current_branch}). Work in this worktree."

After creating the worktree, you should perform your work in that directory rather than the main project directory.
