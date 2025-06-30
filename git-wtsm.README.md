# git-wtsm: Git WorkTree (with) SubModules

A Python utility that provides safe `git worktree` operations for repositories containing submodules, addressing the limitations and experimental nature of Git's built-in submodule support with worktrees.

## The Problem

Git's official documentation warns: *"Multiple checkout in general is still experimental, and the support for submodules is incomplete. It is NOT recommended to make multiple checkouts of a superproject."*

When working with repositories that contain submodules (especially recursive submodules in "superrepository" setups), standard `git worktree` commands face several critical issues:

- **Incomplete submodule state management**: Submodules may not be properly initialized or updated in new worktrees
- **Shared repository corruption**: Incorrect HEAD movements can corrupt the main worktree's submodule state
- **Configuration file corruption**: Switching branches can incorrectly modify submodule configuration files
- **Movement restrictions**: Worktrees containing submodules cannot be moved using `git worktree move`
- **Complex cleanup**: Force removal is often required, with manual intervention needed

## The Solution

`git-wtsm` provides a safe wrapper around Git worktree operations with built-in safety checks and submodule-aware handling:

- **Pre-flight safety checks**: Ensures clean working directories before operations
- **Recursive submodule awareness**: Handles nested submodules correctly
- **Safe removal**: Implements proper cleanup procedures for submodule-containing worktrees
- **Status overview**: Shows both worktree and submodule status in one command

## Installation

### Manual Installation

1. Clone or download the `git-wtsm` script
2. Make it executable: `chmod +x git-wtsm`
3. Place it in your PATH (e.g., `~/.local/bin/`, `/usr/local/bin/`)

```bash
# Example installation to ~/.local/bin
curl -o ~/.local/bin/git-wtsm https://raw.githubusercontent.com/shibuido/git-wtsm/master/git-wtsm
chmod +x ~/.local/bin/git-wtsm

# Ensure ~/.local/bin is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```bash
git-wtsm help
```

## Usage

### Basic Commands

```bash
# Add a new worktree
git-wtsm add <path> [branch]

# Remove a worktree (with safety checks)
git-wtsm remove <path> [--force]

# Show status of all worktrees and submodules
git-wtsm status

# Show help
git-wtsm help
```

### Examples

#### Working with a Superrepository

Consider a project structure like this:

```
my-project/           # Main repository
├── .gitmodules
├── lib/
│   └── utils/        # Submodule: git@github.com:org/utils.git
└── vendor/
    └── framework/    # Submodule: git@github.com:org/framework.git
        └── plugins/  # Nested submodule
```

#### Example 1: Creating a Feature Branch Worktree

```bash
# In your main repository
cd my-project

# Create a new worktree for feature development
git-wtsm add ../my-project-feature feature/new-api

# This safely:
# 1. Checks that main repo has no uncommitted changes
# 2. Creates the worktree at ../my-project-feature
# 3. Handles submodule initialization properly
```

#### Example 2: Working with Different Versions

```bash
# Create worktree for bug fix on release branch
git-wtsm add ../my-project-v1.2-hotfix release/v1.2

# Create worktree for experimental branch
git-wtsm add ../my-project-experimental experiment/new-arch
```

#### Example 3: Safe Removal

```bash
# Check current status
git-wtsm status

# Remove worktree (with safety checks)
git-wtsm remove ../my-project-feature

# Force removal if needed (with confirmation prompt)
git-wtsm remove ../my-project-experimental --force
```

## Safety Features

### Pre-operation Checks

- **Clean state verification**: Ensures no uncommitted changes in main repository
- **Recursive submodule checking**: Verifies all submodules are in clean state
- **Git repository validation**: Confirms operation is run from a Git repository root

### Safe Removal Process

- **Confirmation prompts**: Requires explicit "yes" confirmation for force operations
- **Status reporting**: Shows what will be affected before removal
- **Proper cleanup**: Handles Git's worktree cleanup correctly

## Comparison with Standard Git Worktree

| Operation | Standard Git | git-wtsm |
|-----------|-------------|----------|
| `git worktree add` | ⚠️ May corrupt submodules | ✅ Safe submodule handling |
| `git worktree remove` | ⚠️ Often requires --force | ✅ Smart safety checks |
| Status checking | Separate commands needed | ✅ Unified status view |
| Submodule awareness | ❌ None | ✅ Full recursive support |

## Technical Details

### Requirements

- Python 3.7+
- Git 2.15+ (recommended: 2.25+ for better submodule support)
- Works on Linux, macOS, and Windows

### Implementation

- **Single-file utility**: No external dependencies beyond Python standard library
- **Safe subprocess handling**: Proper error handling and command echoing
- **Atomic operations**: Operations either complete successfully or are safely aborted

## Limitations

- **Experimental nature**: While safer than raw Git commands, worktrees with submodules remain experimental
- **Performance**: Additional safety checks add minor overhead
- **Git version dependencies**: Some edge cases may still occur with older Git versions

## Related Resources

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Git Submodules Documentation](https://git-scm.com/docs/git-submodule)
- [Git Submodules Book Chapter](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Stack Overflow: Git Worktree with Submodules Issues](https://stackoverflow.com/questions/31871888/what-goes-wrong-when-using-git-worktree-with-git-submodules)

## Contributing

This tool is part of the [shibuido](https://github.com/shibuido) organization's collection of subtle, unobtrusive utilities. Contributions are welcome for:

- Additional safety checks
- Better error messages
- Platform-specific improvements
- Documentation enhancements

## License

MIT License - see the repository for full license text.