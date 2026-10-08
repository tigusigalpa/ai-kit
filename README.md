# AI-KIT v0.1

A starter instruction kit for projects developed with ChatGPT/Codex, with thin adapters for other agents. Copy **the contents of this folder** into a new repository root, then send the agent the text from [BOOTSTRAP_PROMPT.md](BOOTSTRAP_PROMPT.md). For an existing project, bootstrap first examines the files and merges instructions while preserving existing rules. [Kit intent and recovered context](ai-kit/INTENT.md).

All authored project files and artifacts use English, including `AGENTS.md`, `WIKI.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md`, `README.md`, skills, code/comments, documentation, UI text, errors/logs, reusable prompts, structured decisions, internal handoffs, Git messages, and saved reviews/reports. Chat with the user uses Russian for questions, plans, progress, explanations, and final reports. Project artifacts shown in chat retain English, with Russian explanations. See the [language policy](AGENTS.md#language).

Reviewable local changes are the default outcome. Agents must not create/amend commits or push changes unless the user explicitly requests the particular operation. See the [Git operations policy](AGENTS.md#git-operations).

```text
.gitignore                           general exclusions and local AI-KIT files
AGENTS.md                            primary agent instructions
CLAUDE.md / KIMI.md / MANUS.md        thin adapters for other agents
PROJECT_CONTEXT.md                   current verified project facts
WIKI.md                              concise knowledge and link map
BOOTSTRAP_PROMPT.md                  one starter prompt
.agents/skills/*/SKILL.md            context and skills for confirmed stacks
ai-kit/
  INTENT.md                          agreements and limits of available context
  ADAPTERS.md / SKILLS.md            adapters and skill registry
  MODELS.md                          adaptive model router and reusable prompt
  adr/0001-adaptive-model-routing.md  kit routing decision and consequences
  ENGINEERING.md                     tests, review, docs, security, migrations
  CONTAINERS.md                      Docker and microservices: Kubernetes-ready
  stacks/LARAVEL.md                  rules when Laravel is present
  stacks/GO.md                       rules when Go is present
  stacks/PYTHON.md                   rules when Python is present
  stacks/MOODLE.md                   rules when Moodle is present
docs/
  DECISIONS.md                       brief decision log
  adr/0000-template.md               template for significant decisions
CHANGELOG.md                         significant project and kit changes
```

## How to use

1. Copy the files into the project root. Merge existing `AGENTS.md`, context, and documentation by meaning rather than deleting them.
2. Run the bootstrap prompt. It inspects the repository, records only verified facts, and identifies gaps.
3. For each task, the agent reads `PROJECT_CONTEXT.md` and only the relevant links. After a task with file changes, it updates `CHANGELOG.md` to record what changed and why. When facts, procedures, or decisions change, it synchronizes context, the skill, and the decision log.

[`.gitignore`](.gitignore) excludes local AI-KIT files, build artifacts, and secrets. It keeps `README.md`, `CHANGELOG.md`, ordinary documentation, source code, migrations, CI, and lockfiles visible to Git. Local `docs/DECISIONS.md` and the ADR template are included in AI-KIT exclusions; completed project ADRs remain versioned. When installing into an existing repository, merge this template with the current `.gitignore` and check project-specific exclusions. Git continues to track files that were already committed: removing them from the index is a separate step that preserves local copies. Because AI-KIT is excluded from Git, a new checkout receives it through a separate installation or archive transfer.

`composer.lock` remains versioned by default: for applications, it fixes dependency versions across development, CI, and deployment. Composer allows reusable PHP libraries to omit the lockfile; in that case, uncomment `/composer.lock` in that project's `.gitignore`. Bootstrap must respect the project type and its existing policy.

`go.mod` and `go.sum` also remain versioned in all Go modules: the former describes the module and dependencies, and the latter records checksums. Only local Go caches, build output, and diagnostic files are excluded by `.gitignore`.

For Python, keep source code, tests, `pyproject.toml`, `requirements*.txt`, `.python-version`, and the project's lockfiles (`uv.lock`, `poetry.lock`, `Pipfile.lock`) versioned. `.gitignore` excludes virtual environments, test and analyzer caches, coverage output, and built packages. If a project intentionally versions built wheels, adjust the `*.whl` rule in its `.gitignore`.

`PROJECT_CONTEXT.md` is the single source of current project facts. `WIKI.md` provides the map and links, while `SKILL.md` provides the procedure for working with those facts; avoid copying detailed project descriptions into all three files. Mark unverified information as unknown.

All new Dockerfiles, containers, and microservices are [Kubernetes-ready](ai-kit/CONTAINERS.md) from the start, including when run locally with Docker Compose. The standard covers images, configuration, shutdown, health checks, data storage, and minimal manifests.

After Docker-based testing, [post-test cleanup](ai-kit/CONTAINERS.md#post-test-docker-cleanup) checks the combined size of the project's test volumes and build caches. Above 10 GB, the agent removes verified disposable test volumes and reclaimable test cache, then reports before/after usage. The rule preserves persistent, active, shared, and unrelated resources.

The [adaptive router](ai-kit/MODELS.md) optimizes total cost to a correct result: Luna for bounded work, Sol 6.1 for substantive engineering, Astra for justified escalation. It covers reasoning, service tiers, targeted context, caching, output budgets, conditional reviewers, and failure diagnosis. The same file can be supplied as a standalone router prompt; the bootstrap loads it when adapting the kit. Defaults are checked against official model documentation, while the runtime registry/configuration determines available controls. Automatic switching requires a supported integration and is not installed by these Markdown files. [Routing decision and consequences](ai-kit/adr/0001-adaptive-model-routing.md).

File placement follows the documentation for [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and [repository skills](https://learn.chatgpt.com/docs/build-skills).
