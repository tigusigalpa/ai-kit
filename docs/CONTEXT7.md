# Context7 integration record

The project-facing [contract](../template/ai-kit/CONTEXT7.md) owns usage and setup. AI-KIT authors its own short `context7-docs` skill; no upstream skill/runtime code is vendored. `--with-context7` is an independent persistent opt-in outside presets. Normal skill discovery remains enabled; availability does not authorize server setup.

## Source verification

Reviewed on 2026-10-12: [upstream repository](https://github.com/upstash/context7/tree/33414e6e3fc157c936348ca8ddba25e50dacaeee), revision `33414e6e3fc157c936348ca8ddba25e50dacaeee` (MIT), [client/authentication docs](https://context7.com/docs/resources/all-clients), and official [Codex](https://developers.openai.com/codex/mcp/), [Claude](https://code.claude.com/docs/en/mcp), and [Cursor](https://cursor.com/docs/context/mcp) schemas. The revision identifies documentation research, not a pin of the hosted endpoint/backend or an installed package.

The upstream contract exposes `resolve-library-id` and `query-docs`. The workflow narrows questions to public library/version facts, checks version coverage, treats results as reference data, and falls back to official documentation when unavailable. Client setup uses reviewed HTTP examples with environment-based credentials or separately selected OAuth. The installer runs no external processes/network and changes no native MCP configuration.

## Maintainer checks

Keep the optional entry-point mapping, settings flag, source/native copies, skill registry, guide and WIKI synchronized. Check default/preset absence, independent persistence, offline/process-free apply, user configuration preservation, upgrades/conflicts, client retirement, linked paths, and private/team visibility. Package the guide and entry point in the wheel; test a fresh installation and rerun.

Recheck primary sources before changing endpoint/authentication/tool names or client examples. Keep native activation, library retrieval, hosted availability and cost claims separate from installer tests. No live connection or documentation query is established by a generated file.

## Verification

Windows/Python 3.12.14:

- Full discovery: 293 tests in 1239.036 seconds; 289 passed, four skipped (POSIX hook execution, symlink creation and two junction fixtures unavailable).
- Eight new Context7 tests passed: default/preset absence, preview-only CLI, independent persistent selections, process/network-free apply, unchanged native MCP configuration, source/Claude copies, local edits/conflicts, retained deselection, invalid settings and blocked parents. Existing installer/checker/security tests also passed.
- Kit validation: zero errors/warnings, including actual Git visibility. Additional synthetic projects with all 11 client selections passed private/team visibility, installed links and stable reruns. These are file checks, not native activation tests.
- Both JSON examples and the TOML example parsed; changed Python files passed Python 3.10 grammar checks. The bundled skill validator passed in local Ubuntu/PyYAML; Windows runtime has no PyYAML. Python 3.10 execution remains unverified.
- Offline wheel build and fresh-environment smoke passed: default installation, combined Context7/security-audit/Strix installation, doctor checks and stable rerun. Context7 resources were present with exact source bytes; private journals/caches were absent. Final documentation updates require only content/link checks; executable behavior is unchanged.

No Context7 package/server was installed or started, and no account/key was provisioned. Native client activation, authentication, hosted availability, version coverage and live documentation retrieval remain unverified. No full security audit, Strix scan or OpenRouter call was run.

## Release labeling

Prepared v1.2.0 at the owner's request on 2026-10-12. The 293-test run above preceded labeling; executable logic was unchanged. After labeling, eight CLI tests, the literal CLI version, clean kit validation, 1.2.0 wheel metadata and fresh-environment offline smoke passed. Default and combined Context7/security-audit/Strix installations had clean doctor reports and stable reruns.

A synthetic upgrade from the pre-label 1.1.0 reference copy preserved application facts/project.json bytes, settings values and unknown fields, selected extras, a modified Context7 skill, existing MCP configuration and both security pins. Installed VERSION/state advanced to 1.2.0; links, doctor errors and rerun stability passed. This fixture does not establish a published source revision or live client activation. Publication/tagging remains separate.
