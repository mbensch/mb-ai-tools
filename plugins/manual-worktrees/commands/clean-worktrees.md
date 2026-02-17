---
description: List and clean up droid worktrees interactively
disable-model-invocation: true
---

List all droid worktrees and help the user select which to clean up. Follow these steps exactly:

1. Check if this is a git repository. If not, report that worktrees require a git repo and stop.

2. Get the repo name:
   ```bash
   basename "$(git rev-parse --show-toplevel)"
   ```

3. Get the worktrees directory:
   ```bash
   git rev-parse --show-toplevel | xargs -I{} dirname {} | xargs -I{} echo "{}/droid-worktrees"
   ```

4. List all worktrees matching `{repo_name}-*`:
   ```bash
   ls -d "{worktrees_dir}/{repo_name}-*" 2>/dev/null
   ```

5. For each worktree found, gather information:
   - Directory name
   - Branch name: `git -C "{worktree_dir}" rev-parse --abbrev-ref HEAD`
   - Last modified: `stat -f "%Sm" "{worktree_dir}"` (macOS) or `stat -c "%y" "{worktree_dir}"` (Linux)
   - Age in days (calculate from last modified date)

6. Present the list to the user in a formatted table showing:
   | # | Directory | Branch | Last Modified | Age |
   Include an option to select "All" or "Cancel".

7. Use the AskUser tool to let the user select which worktrees to remove:
   - Allow selecting one, multiple, or all worktrees
   - Include a "Cancel" option

8. For each selected worktree, clean up:
   ```bash
   # Get the branch name first
   BRANCH=$(git -C "{worktree_dir}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
   
   # Remove the worktree
   git worktree remove --force "{worktree_dir}"
   
   # Delete the branch if it starts with droid/
   if [ -n "$BRANCH" ] && echo "$BRANCH" | grep -q '^droid/'; then
     git branch -D "$BRANCH"
   fi
   ```

9. Report what was cleaned up:
   "Cleaned up X worktrees: [list of directories]"
   "Deleted branches: [list of branches]"

If no worktrees exist, report: "No droid worktrees found for this repository."
