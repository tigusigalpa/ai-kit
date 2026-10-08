# Optional runtime guards

The installer does not apply these global/runtime security settings.
claude-settings.deny-git.json illustrates command denies, not a complete prohibition: aliases, git -C, wrappers, SDKs, and other tools require separate controls.
Merge it only after reviewing the actual client's current settings. An individually authorized Git operation needs a deliberate supported exception.
Core remains the instruction owner; do not claim a guard active without testing the actual client.
