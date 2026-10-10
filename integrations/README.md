# Optional runtime guards

The installer applies these client rules only for the opt-in --with-guards extra, and only for entries it owns inside the client settings file.
claude-settings.git-ask.json makes Claude Code ask before Git commit/push commands. Core allows these operations only on an explicit user request, so ask matches the policy: an authorized commit stays possible and an unrequested one needs your confirmation.
These are command-prefix rules, not a complete prohibition: aliases, git -C, wrappers, SDKs, and other tools require separate controls.
Core remains the instruction owner; do not claim a guard active without testing the actual client.
