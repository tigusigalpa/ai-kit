# New-project start prompt

Give the following English prompt to an agent with the AI-KIT distribution and target repository available:

~~~text
Analyze this repository and install or adapt the attached AI-KIT.
Read template/ai-kit/BOOTSTRAP.md from the distribution, then inspect the target's current instructions and manifests.
Use scripts/install.py for a preview and apply only a compatible, reviewed plan; preserve existing files and decisions.
Keep the supplied defaults unless I explicitly change them.
After installation read the target AGENTS.md, ai-kit/CORE.md, and current PROJECT_CONTEXT.md.
Enable only confirmed stack profiles and record module paths, evidence, and actual check commands.
Run relevant checks, review the changes, and update project context, continuity pointers, and CHANGELOG.
Report what changed, conflicts, and checks that remain unavailable.
~~~

For a file-access-limited chat, attach the relevant template files and current project evidence. An agent must not claim filesystem installation without access.
