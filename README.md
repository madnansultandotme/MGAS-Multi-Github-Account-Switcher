# Multi-GitHub Account Switcher

A desktop helper built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) that lets you store multiple GitHub identities, authenticate each account using a Personal Access Token (PAT), switch the active `gh` session, and bootstrap new repositories (git init ➜ first commit ➜ push) without touching the command line.

## Features
- Central list of labeled accounts (name, username, email) persisted under `~/.github_accounts.json`.
- PAT-only authentication flow that pipes your token straight into `gh auth login --with-token`.
- Quick actions panel to switch the global GitHub CLI user, remove saved profiles, refresh status, or initialize/push a repo with the selected identity.
- Repository bootstrapper that configures authorship, creates an initial commit, and calls `gh repo create … --push` for the folder you pick.
- Real-time display of the current `gh auth status` output so you always know which account is active.
- Responsive CustomTkinter layout with a Settings dialog to choose the default initial commit message before pushing new repositories.

For a detailed breakdown of every workflow, see `doc/FUNCTIONALITY.md`.

## Screenshots
Preview images of each UI screen live in the `screenshots/` folder so you can reference or embed the latest layout without launching the app.

## Prerequisites
- Windows 10/11 (the app is currently Windows-only because of GitHub CLI path discovery and packaging).
- Python 3.10+ (tested on 3.12).
- [Git](https://git-scm.com/download/win) 2.30+ for repository commands.
- [GitHub CLI](https://cli.github.com/) (`gh`) installed and accessible— the app can locate it even if it is not on `PATH`, but installing it system-wide is recommended.
- `pip install customtkinter` (or install from `requirements.txt` if you add one).
- Network access to GitHub.

### Installing prerequisites
1. **Python:** Download the Windows installer from [python.org](https://www.python.org/downloads/windows/) (3.10 or newer). During installation, check “Add python.exe to PATH”.
2. **Git:** Install from [git-scm.com](https://git-scm.com/download/win). Accept the defaults so `git` is available in PowerShell/Git Bash.
3. **GitHub CLI:** Install via the [official MSI](https://cli.github.com/) or `winget install GitHub.cli`. Run `gh auth login` once in PowerShell to ensure it works.
4. **Python deps:** Inside your project (or virtualenv), run `pip install customtkinter`.

## Setup
1. Clone or download this repository.
2. (Optional) Create and activate a virtual environment: `python -m venv venv && ./venv/Scripts/activate` (Windows) or `source venv/bin/activate` (macOS/Linux).
3. Install CustomTkinter: `pip install customtkinter`.
4. Launch the UI: `python github_account_switcher.py`.

### Project structure
```
mgas/
   __init__.py          # Package exports
   accounts.py          # Account storage + settings managers
   gh_cli.py            # GitHub CLI helpers + repo bootstrapper
   ui.py                # CustomTkinter interface (AccountSwitcherApp)
github_account_switcher.py  # Thin entrypoint calling AccountSwitcherApp
README.md
```

## Branding & Packaging
- The window/title-bar/taskbar icon now comes from `images/icon.ico`, while `images/logo.png` serves as a PNG fallback for environments where `.ico` loading fails. Replace these files (keep their names) to change the branding.
- Both assets are bundled automatically in the packaged app via [MGAS-Desktop.spec](MGAS-Desktop.spec), so the executable, window chrome, and taskbar all show the same icon.
- When you need a fresh build, run PyInstaller against the spec file to reuse the bundled data and icon configuration:
  ```bash
  pyinstaller MGAS-Desktop.spec --noconfirm --clean
  ```
- If you prefer the one-liner, keep the icon flag aligned with the source files: `pyinstaller --name MGAS-Desktop --windowed --onefile --noconsole --icon=images/icon.ico github_account_switcher.py`.
- After rebuilding, launch `dist/MGAS-Desktop.exe` to verify the icon renders correctly in the title bar and on the taskbar.

## Using the App
1. **Add an account**
   - Fill in *Label*, *GitHub Username*, *Full Name*, *Email*, and pick a Git protocol (HTTPS or SSH).
   - Paste a fine-grained PAT in the *Personal Access Token* field. The token is sent directly to `gh auth login --with-token` and never stored.
   - Click **Add & Authenticate Account**. On success, the profile is saved and becomes available for switching.
2. **Switch the active CLI user**
   - Select any row in the accounts table and click **Switch Global Authentication**. The `gh` session changes to that user, and the status label updates.
3. **Initialize a folder & push to GitHub**
   - With an account selected, click **Initialize Folder & Push to GitHub** and choose a local project folder.
   - The tool initializes git (if needed), configures the selected name/email, stages files, makes the first commit, prompts for a repo name + visibility, and runs `gh repo create … --push`.
4. **Remove an account**
   - Select the profile and click **Remove Selected Account**. Entries are deleted from both the UI and `~/.github_accounts.json`.
5. **Refresh status**
   - Click **Refresh Active Status** anytime to rerun `gh auth status` and update the banner.
6. **Adjust defaults**
   - Hit **Settings** to open a dialog where you can change the default initial commit message used by the repo bootstrapper.

## PAT Requirements
- Use a **fine-grained PAT** generated at <https://github.com/settings/personal-access-tokens>.
- Minimum scopes: `repo` (or specific repositories) and `admin:public_key` (needed when `gh` uploads SSH keys during login).
- Tokens are only used in-memory for the authentication call; they are not written to disk.

## Stored Data & Settings
- Profiles live in `~/.github_accounts.json`. Delete this file to reset the app or edit it manually (while the app is closed) to rename labels.
- UI preferences (currently just the default initial commit message) live in `~/.github_account_switcher_settings.json`.

## Maintainer & Contact
- **Email:** info.adnansultan@gmail.com
- **GitHub:** [madnansultandotme](https://github.com/madnansultandotme)
- **LinkedIn:** [dev-madnansultan](https://www.linkedin.com/in/dev-madnansultan)

## Troubleshooting
- **"GitHub CLI not found"**: Install `gh` from the official installer or add it to PATH. The app also looks in `Program Files/GitHub CLI/gh.exe` and `%LocalAppData%/Microsoft/WindowsApps/gh.exe`.
- **Repo already has `origin`**: The bootstrapper will stop if `git remote get-url origin` succeeds to avoid overwriting existing remotes. Remove or rename the remote before rerunning.
- **Nothing to commit**: If the target folder is clean, git reports "nothing to commit". The flow continues, but only new files will be pushed.
- **Token rejected**: Double-check that the PAT has not expired and that the selected git protocol matches how you plan to clone.

Feel free to adapt the UI layout or extend the workflow (e.g., add SSH key helpers or workspace-specific git configs) to match your team’s needs.
