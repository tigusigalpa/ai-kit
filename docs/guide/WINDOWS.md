# Windows: installation and troubleshooting

Use **Windows PowerShell 5.1 or PowerShell 7** with Python **3.10+**. The examples below are PowerShell commands: copy the command itself, without a `PS C:\>` prompt. Run them in your application's folder when a target of `.` is shown.

AI-KIT creates project instructions, memory scaffolding and selected client resources. In an empty project, tell your coding agent which application and stack you want during bootstrap; stack detection needs actual project files. A source checkout of AI-KIT and your application are separate folders.

The general installation, defaults and update guide is [Install AI-KIT and set up a project](INSTALL.md); every installer option is listed in [Installer flags and options](INSTALLER_FLAGS.md). With pipx available, `pipx install ai-kit-python` is an alternative to the steps below.

## Windows quick start: an empty project

**1. Check Python and install the package.** Use the same `python` for installation and execution:

~~~powershell
python --version
python -m pip --version
python -m pip install --upgrade ai-kit-python
python -m aikit.aikit_cli --version
~~~

The package is **`ai-kit-python`** (never `pip install aikit`), its short executable is **`aikit.exe`**, and its module entry point is **`python -m aikit.aikit_cli`**. The module entry point works even when Windows cannot find `aikit.exe` through PATH. A successful installation can still print a Scripts/PATH warning; see [the error guide](#windows-error-guide).

**2. Choose a project directory and preview.** Change `my-app` to your project name. This example uses a directory owned by your Windows user and also works when its path contains spaces:

~~~powershell
$projectPath = Join-Path $env:USERPROFILE 'Projects\my-app'
New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
Set-Location -LiteralPath $projectPath
python -m aikit.aikit_cli install . --agent codex --mode private
~~~

Review the proposed files and detected settings. Preview writes nothing to the project. If you already have a folder, set `$projectPath` to that folder instead. A Git repository can be initialized there separately with `git init` when wanted.

**3. Apply the reviewed plan and check it.** Keep the same agent, sharing mode and optional-module flags:

~~~powershell
python -m aikit.aikit_cli install . --agent codex --mode private --apply --check
~~~

`--apply` writes the installation; `--check` runs the project doctor afterward. Existing project documents and local edits follow the normal preservation/conflict rules. Private mode selects local instruction visibility; it does not encrypt files. Chat replies default to Russian and Laravel conventions default to the owner's opinionated profile; add `--chat-language English --conventions standard` to both commands to change that ([defaults](INSTALL.md#choose-your-defaults)).

**4. Bootstrap in the coding client.** Open this application folder in Codex, then send `$ai-kit-bootstrap` in the **Codex chat**. This is a skill invocation in the client, not a PowerShell command. For Claude Code use `--agent claude` in both installer commands and `/ai-kit-bootstrap` in its chat; repeat `--agent` to configure both clients.

Tell the agent what you are building, the intended stack and your constraints. If the client has not discovered the installed skill, confirm that it opened the target project, and ask it to read the target's `AGENTS.md` and `ai-kit/BOOTSTRAP.md`. Installing files and actual client activation are separate steps.

Optional features stay explicit. For example, add `--with-web-design` to **both** preview and apply when you want the [Web Design module](WEB_DESIGN.md). The [orchestration module](ORCHESTRATION.md) has its own configuration and limits.

## Windows isolated CLI: no activation required

For a reusable CLI environment outside your application, use a user-owned folder. This avoids installing into a system Python and avoids the `Activate.ps1` execution-policy problem:

~~~powershell
$cliEnv = Join-Path $env:LOCALAPPDATA 'AI-KIT\venv'
python -m venv "$cliEnv"
& "$cliEnv\Scripts\python.exe" -m pip install --upgrade ai-kit-python
& "$cliEnv\Scripts\aikit.exe" --version
~~~

From the application folder, preview and then apply separately:

~~~powershell
& "$cliEnv\Scripts\aikit.exe" install . --agent codex --mode private
~~~

~~~powershell
& "$cliEnv\Scripts\aikit.exe" install . --agent codex --mode private --apply --check
~~~

The leading `&` executes a quoted path in PowerShell. Keep using this environment's executables for its installs and updates. Python documents that [environment activation is optional](https://docs.python.org/3/library/venv.html#how-venvs-work); using explicit paths is enough. A new PowerShell window needs the `$cliEnv` assignment again, while the environment files remain on disk.

## Why installing the package may not enable the aikit command

There are three separate states:

| State | What it means | How to check |
| --- | --- | --- |
| Installed Python package | One particular interpreter can import AI-KIT. | `python -m pip show ai-kit-python` and `python -m aikit.aikit_cli --version` |
| Saved user PATH | A Scripts directory is persisted for your Windows account. | `[Environment]::GetEnvironmentVariable('Path', 'User')` |
| Current process PATH | This terminal has a current copy of the directories used to find executables. | `$env:Path` and `Get-Command aikit -ErrorAction SilentlyContinue` |

PowerShell processes inherit their environment from their parent. Saving a user PATH entry does not rewrite the environment of every already-running terminal or editor. A new tab or shell opened by an older Windows Terminal, VS Code or Codex process can still inherit its old PATH. See Microsoft's [environment-variable scope and inheritance documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables).

This explains the common sequence: pip reports `Successfully installed`, the Scripts directory is saved in user PATH, but the current terminal still reports `CommandNotFoundException`.

## Fix PATH in the current PowerShell window

The quickest route is to keep using `python -m aikit.aikit_cli`. To make the short command available, import missing saved user-PATH entries into **the same PowerShell window that reports the error**, preserving its existing entries:

~~~powershell
$savedUserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
foreach ($entry in ($savedUserPath -split ';')) {
    if ([string]::IsNullOrWhiteSpace($entry)) { continue }
    $expandedEntry = [Environment]::ExpandEnvironmentVariables($entry.Trim().Trim('"'))
    $processEntries = @($env:Path -split ';' | ForEach-Object { $_.Trim().Trim('"').TrimEnd('\') })
    if ($processEntries -notcontains $expandedEntry.TrimEnd('\')) {
        $env:Path = $env:Path.TrimEnd(';') + ';' + $expandedEntry
    }
}
Get-Command aikit -CommandType Application
aikit --version
~~~

This refresh changes only the current process. If the Scripts directory has not been saved yet, use the permanent setup below. For future sessions, completely exit and reopen the **hosting terminal/editor application**; opening another tab can preserve the old parent environment. Save ongoing work before restarting an editor. A check in a separately refreshed process establishes that process's PATH, not the state of an older interactive window.

## Add the correct Scripts directory to user PATH permanently

Python layouts vary. For example, a Python 3.14 installation may use `%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts`; older installations may use a different directory. Discover the location for the interpreter that already runs AI-KIT, rather than copying another user's path. Python exposes these paths through [sysconfig installation schemes](https://docs.python.org/3/library/sysconfig.html#installation-path-functions).

Run this block with a **regular Python installation** where `python -m aikit.aikit_cli --version` already succeeds. For the isolated CLI above, continue using explicit paths or activate that environment; its Scripts directory should not become a permanent global shortcut.

~~~powershell
& {
    $ErrorActionPreference = 'Stop'
    $inVirtualEnv = python -c "import sys; print(sys.prefix != sys.base_prefix)"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the selected Python.' }
    if ($inVirtualEnv -eq 'True') { throw 'Use the virtual environment executable directly.' }

    $scriptDirectories = @(python -c "import sysconfig; print(sysconfig.get_path('scripts')); print(sysconfig.get_path('scripts', 'nt_user'))")
    if ($LASTEXITCODE -ne 0) { throw 'Cannot locate Python Scripts directories.' }
    $aikitScriptsPath = $scriptDirectories |
        Where-Object { Test-Path -LiteralPath (Join-Path $_ 'aikit.exe') -PathType Leaf } |
        Select-Object -First 1
    if (-not $aikitScriptsPath) { throw 'Install ai-kit-python with this Python first.' }

    $userPathValue = [Environment]::GetEnvironmentVariable('Path', 'User')
    $userEntries = @($userPathValue -split ';' | ForEach-Object {
        [Environment]::ExpandEnvironmentVariables($_.Trim().Trim('"')).TrimEnd('\')
    })
    if ($userEntries -notcontains $aikitScriptsPath.TrimEnd('\')) {
        $updatedUserPath = if ([string]::IsNullOrWhiteSpace($userPathValue)) {
            $aikitScriptsPath
        } else {
            $userPathValue.TrimEnd(';') + ';' + $aikitScriptsPath
        }
        [Environment]::SetEnvironmentVariable('Path', $updatedUserPath, 'User')
    }

    $processEntries = @($env:Path -split ';' | ForEach-Object { $_.Trim().Trim('"').TrimEnd('\') })
    if ($processEntries -notcontains $aikitScriptsPath.TrimEnd('\')) {
        $env:Path = $env:Path.TrimEnd(';') + ';' + $aikitScriptsPath
    }
    Get-Command aikit -CommandType Application
    aikit --version
}
~~~

The block preserves existing entries, avoids adding the same directory again and writes only the **User** scope. It also updates the current window. The [.NET API](https://learn.microsoft.com/en-us/dotnet/api/system.environment.setenvironmentvariable) documents persistence by scope. Reopen the hosting application before testing future sessions. Never replace saved user PATH with the whole current process PATH: the latter may contain machine, virtual-environment and temporary entries.

For a graphical setup, search Windows for **Edit environment variables for your account**, edit **Path** under user variables, add the discovered Scripts directory as a new entry and save. Preserve the other entries. Avoid using `setx PATH "$env:PATH;..."` as a repair shortcut.

## Windows error guide

| Message or symptom | Cause to check | Resolution |
| --- | --- | --- |
| `The term 'aikit' is not recognized` / `CommandNotFoundException` | The current shell cannot find `aikit.exe`. | Use `python -m aikit.aikit_cli`; then check saved versus process PATH and use the refresh/permanent steps above. |
| `WARNING: The script aikit.exe is installed in ... which is not on PATH` | Pip installed the package, but the launcher directory is absent from that process's PATH. | Follow the exact directory in the warning or discover it with `sysconfig`. A successful module launch verifies the selected interpreter's package. |
| The user PATH entry exists, but another tab still cannot find `aikit` | A running parent terminal/editor still has its earlier environment. | Refresh the failing window or restart the hosting application completely. |
| `No module named aikit` | This `python` differs from the interpreter used by pip, or its environment lacks the package. | Bind installation and execution to the same interpreter as shown below. |
| `python` is not recognized, or Windows opens the Store | No usable Python is selected, or an application alias resolves instead of the intended interpreter. | Follow the official Windows setup guide and inspect `Get-Command python -All`; an existing interpreter can be invoked by its full path with `&`. |
| `No module named pip` | The selected Python does not have pip. | For an installation that supports it, run `python -m ensurepip --upgrade`, then `python -m pip --version`. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy blocks the activation script. | Use the isolated environment's `python.exe` / `aikit.exe` directly. Activation is optional; no policy change is needed for this route. |
| `Access is denied`, `PermissionError` or `[WinError 5]` | The install destination or project is not writable, or a file is in use. | Use the user-owned isolated CLI and a writable project folder. Stop processes holding affected files before retrying; running the whole setup as administrator is unnecessary for a user-owned setup. |
| `No matching distribution found for ai-kit-python` | Unsupported Python, incorrect package spelling or an unavailable/configured package index. | Confirm Python 3.10+, the exact `ai-kit-python` name and the intended index. Check connectivity and the public project page. |
| TLS, certificate, proxy or timeout error during pip installation | Network settings, certificates or registry connectivity. | Check the system clock and approved proxy/CA configuration; use your organization's supported setup. Retrying PATH changes does not fix a failed download. |
| `Unexpected token` around a quoted executable path | A quoted path was supplied as a string without PowerShell's call operator. | Use `& "C:\path with spaces\Scripts\aikit.exe" --version`. |
| `Cannot install an application kit inside the reference distribution` | `.` points at the AI-KIT source folder or a child of it. | Switch to the separate application folder and rerun preview. |
| `Refusing a linked target root` or another linked-path refusal | A selected root/managed path is a symlink or junction. | Use the real application directory and inspect the reported path; preserve existing files and review layout conflicts. |
| Preview lists conflicts or `--check` reports a problem | Local customizations or an incomplete/incompatible project installation need review. | Review the candidates and run the doctor. Preserve local edits; `--accept-local` is for an explicitly reviewed merge. |
| `[notice] A new release of pip is available` | An informational pip update notice. | It does not invalidate a successful AI-KIT installation. Update pip separately when appropriate. |

### Resolve multiple Python installations

Inspect the interpreter and its package together:

~~~powershell
Get-Command python -All
python -c "import sys; print(sys.executable)"
python -m pip --version
python -m pip show ai-kit-python
python -m aikit.aikit_cli --version
~~~

If these refer to the wrong Python, use the intended executable explicitly. Replace the example path with your actual interpreter path:

~~~powershell
$pythonExe = 'C:\Path\To\Python\python.exe'
& $pythonExe -m pip install --upgrade ai-kit-python
& $pythonExe -m aikit.aikit_cli --version
& $pythonExe -m aikit.aikit_cli install . --agent codex --mode private
~~~

This binds pip and the CLI to the same runtime. A short `aikit` command can still select another installation earlier in PATH; `Get-Command aikit -All` shows its candidates. See [Python on Windows](https://docs.python.org/3/using/windows.html) for interpreter/alias setup and [pip's invocation guide](https://pip.pypa.io/en/stable/user_guide/#running-pip) for interpreter-bound installation.

### Check an installed project and update it later

After applying AI-KIT in the application directory:

~~~powershell
python -m aikit.aikit_cli doctor .
~~~

Updating the Python package updates the CLI. To update project instructions too, preview and apply against that application separately:

~~~powershell
python -m pip install --upgrade ai-kit-python
python -m aikit.aikit_cli install .
~~~

After reviewing the preview:

~~~powershell
python -m aikit.aikit_cli install . --apply --check
~~~

For the isolated CLI, use `& "$cliEnv\Scripts\python.exe" -m pip ...` and `& "$cliEnv\Scripts\aikit.exe" ...` instead. Existing saved agent/module/sharing selections are retained when omitted; pass selection flags only when intentionally changing them. See [project upgrades](INSTALL.md#update-an-application-project) for preservation and conflicts.
