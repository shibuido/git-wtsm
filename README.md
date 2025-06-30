# git-wtsm

> **Git WorkTree (with) SubModules** - Safe worktree operations for repositories with submodules

## Why git-wtsm?

Git's built-in worktree support has [experimental and incomplete submodule support](https://git-scm.com/docs/git-worktree). Working with superrepositories (repos with recursive submodules) using standard `git worktree` commands can lead to:

- Repository corruption
- Broken submodule states  
- Configuration file corruption
- Complex cleanup requirements

## What it does

`git-wtsm` wraps Git worktree operations with safety checks and submodule-aware handling:

- ✅ **Safe worktree creation** with proper submodule initialization
- ✅ **Clean removal** with recursive submodule state checking  
- ✅ **Unified status** showing both worktrees and submodules
- ✅ **Pre-flight safety checks** preventing repository corruption

## Quick Start

```bash
# Install (add to PATH)
curl -o ~/.local/bin/git-wtsm https://raw.githubusercontent.com/shibuido/git-wtsm/master/git-wtsm
chmod +x ~/.local/bin/git-wtsm

# Use like git worktree, but safer
git-wtsm add ../my-project-feature feature/new-api
git-wtsm status
git-wtsm remove ../my-project-feature
```

## Who needs this?

- **Monorepo maintainers** working with submodules
- **Library developers** managing dependencies as submodules
- **Teams using superrepository patterns** with recursive submodules
- **Anyone** who's hit Git worktree + submodule issues

## Learn More

📖 **[Read the full documentation](git-wtsm.README.md)** for installation, examples, and technical details.

---

*Part of [shibuido](https://github.com/shibuido): The way of subtle, unobtrusive beauty in utility.*