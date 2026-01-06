# Multi-GitHub Account Switcher Functionality Guide

This document deep-dives into every end-user workflow the Multi-GitHub Account Switcher currently supports. Use it as a reference for QA, onboarding, or planning new enhancements.

## 1. Account Management
- **Profile catalog:** Stores labeled profiles (label, username, full name, email) inside `~/.github_accounts.json`. Entries persist across launches and populate the main table on startup.
- **Add & authenticate:** The "Add & Authenticate Account" action validates inputs, sends the PAT to `gh auth login --with-token`, and saves the profile only if authentication succeeds. Tokens are never written to disk.
- **Removal flow:** Selecting a profile and clicking "Remove Selected Account" deletes it from the table and the JSON store after user confirmation.
- **Form reset:** Successful account creation clears the input controls and resets protocol to HTTPS to prevent accidental token reuse.

## 2. Authentication & Identity Switching
- **PAT-only login:** Supports HTTPS or SSH Git protocol selection, ensuring `gh auth login` aligns with a user's preferred transport.
- **Switch global authentication:** Re-uses the stored GitHub username to call `gh auth switch --user`, updating the global CLI identity across shells.
- **Git setup helper:** After login, the app attempts `gh auth setup-git` to make sure Git pulls/pushes honor the authenticated account (non-fatal if it fails).

## 3. Status Visibility
- **Active user banner:** `gh auth status` runs on load and anytime the user clicks "Refresh Active Status". The first line containing "Active account" renders in the UI so you always know which account `gh` currently references.
- **CLI fallback messaging:** If `gh` is missing or the status call fails, the banner shows a diagnostic hint instead of crashing the UI.

## 4. Repository Bootstrapper
- **Folder selection:** Leverages the OS directory picker so users can target any local folder (new or existing project) for initialization.
- **Repo metadata prompts:** Prompts for GitHub repository name and private/public visibility before doing any Git/GitHub work.
- **Safety checks:** Ensures the target folder is a git repo (initializes if needed) and aborts if a remote named `origin` already exists.
- **Authorship config:** Applies the selected profile's name/email via `git config user.name|user.email` to keep commits attributed correctly.
- **Commit workflow:** Stages all files, commits with the configurable default message, and tolerates "nothing to commit" situations unless Git returns a real error.
- **Repo creation & push:** Calls `gh repo create <name> --source <folder> --remote origin --push --confirm` with the chosen visibility, resulting in code + remote in one step.

## 5. Settings & Preferences
- **Default commit message:** The Settings dialog exposes the `initial_commit_message` preference stored in `~/.github_account_switcher_settings.json` with fallbacks defined in code.
- **Live persistence:** Saving immediately writes to disk and future bootstrap operations use the new message without restarting the app.

## 6. Error Handling & User Feedback
- **Dialog-driven errors:** Missing fields, invalid tokens, GitHub CLI issues, Git failures, and repo conflicts all surface via modal dialogs with actionable text.
- **Success notifications:** Key flows (account added, auth switched, repo pushed) display confirmation dialogs so users know the operation finished.

## 7. Platform & Dependency Requirements
- **Windows-only:** Path discovery and packaging assumptions currently target Windows 10/11. Cross-platform support would require additional testing and path strategies.
- **External tooling:** Relies on GitHub CLI (`gh`) and Git being installed locally; the UI helps detect when they are unavailable.
- **Python dependencies:** Requires Python 3.10+ with `customtkinter` installed (others use standard library modules).

## 8. Files & Modules Backing Each Feature
- `mgas/accounts.py`: Account persistence, dataclasses, and settings storage.
- `mgas/gh_cli.py`: GitHub CLI resolution, authentication helpers, repo creation, and the RepoBootstrapper.
- `mgas/ui.py`: Entire CustomTkinter interface, input validation, dialogs, and orchestration of the above modules.
- `github_account_switcher.py`: Thin entrypoint exposing `main()` to launch the UI.

Keep this guide updated whenever new controls, backend services, or support scripts land so downstream documentation stays in sync with the product experience.
