from __future__ import annotations

import os
import shutil
import subprocess
from typing import Optional

from .accounts import Account

if os.name == "nt":
    _STARTUP_INFO = subprocess.STARTUPINFO()
    _STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _CREATION_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)
else:
    _STARTUP_INFO = None
    _CREATION_FLAGS = 0


def _apply_windowless_defaults(kwargs: dict) -> dict:
    """Ensure subprocess children stay headless on Windows builds."""
    if os.name == "nt":
        kwargs.setdefault("startupinfo", _STARTUP_INFO)
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | _CREATION_FLAGS
    return kwargs


def hidden_run(cmd, **kwargs):
    return subprocess.run(cmd, **_apply_windowless_defaults(kwargs))


def hidden_popen(cmd, **kwargs):
    return subprocess.Popen(cmd, **_apply_windowless_defaults(kwargs))


class GitHubCLI:
    def __init__(self):
        self._cached_path: Optional[str] = None

    def resolve(self) -> Optional[str]:
        if self._cached_path and os.path.exists(self._cached_path):
            return self._cached_path

        search_paths = [shutil.which("gh")]
        search_paths.extend(
            [
                os.path.join(os.environ.get("ProgramFiles", ""), "GitHub CLI", "gh.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "GitHub CLI", "gh.exe"),
                os.path.join(os.environ.get("LocalAppData", ""), "Microsoft", "WindowsApps", "gh.exe"),
            ]
        )

        for path in search_paths:
            if path and os.path.exists(path):
                self._cached_path = path
                return path
        return None

    def ensure(self) -> str:
        gh_path = self.resolve()
        if not gh_path:
            raise FileNotFoundError("GitHub CLI not found")
        return gh_path

    def auth_with_token(self, protocol: str, token: str) -> None:
        gh = self.ensure()
        cmd = [gh, "auth", "login", "--hostname", "github.com", "--git-protocol", protocol, "--with-token"]
        process = hidden_popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=token + "\n")
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)

    def setup_git(self) -> None:
        gh = self.ensure()
        hidden_run([gh, "auth", "setup-git"], check=True)

    def switch_user(self, username: str) -> None:
        gh = self.ensure()
        hidden_run([gh, "auth", "switch", "--user", username], check=True)

    def auth_status(self) -> str:
        gh = self.ensure()
        result = hidden_run([gh, "auth", "status"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "Active account" in line:
                return line.strip()
        return result.stdout.splitlines()[0] if result.stdout else "No active account"

    def repo_create(self, folder: str, repo_name: str, private: bool) -> None:
        gh = self.ensure()
        visibility_flag = "--private" if private else "--public"
        hidden_run(
            [
                gh,
                "repo",
                "create",
                repo_name,
                visibility_flag,
                "--source",
                folder,
                "--remote",
                "origin",
                "--push",
                "--confirm",
            ],
            check=True,
        )


class RepoBootstrapper:
    def __init__(self, gh_cli: GitHubCLI):
        self.gh_cli = gh_cli

    def _ensure_git_repo(self, folder: str) -> None:
        check = hidden_run(["git", "-C", folder, "rev-parse", "--is-inside-work-tree"], capture_output=True)
        if check.returncode != 0:
            hidden_run(["git", "-C", folder, "init"], check=True)

        remote_check = hidden_run(["git", "-C", folder, "remote", "get-url", "origin"], capture_output=True)
        if remote_check.returncode == 0:
            raise RuntimeError("This repository already has a remote named 'origin'.")

    def _configure_authorship(self, folder: str, account: Account) -> None:
        hidden_run(["git", "-C", folder, "config", "user.name", account.name], check=True)
        hidden_run(["git", "-C", folder, "config", "user.email", account.email], check=True)

    def _stage_and_commit(self, folder: str, commit_message: str) -> None:
        hidden_run(["git", "-C", folder, "add", "-A"], check=True)
        commit_proc = hidden_run(
            ["git", "-C", folder, "commit", "-m", commit_message],
            capture_output=True,
            text=True,
        )
        combined = (commit_proc.stdout or "") + (commit_proc.stderr or "")
        if commit_proc.returncode != 0 and "nothing to commit" not in combined.lower():
            raise subprocess.CalledProcessError(commit_proc.returncode, commit_proc.args, commit_proc.stdout, commit_proc.stderr)

    def initialize_and_push(self, folder: str, account: Account, repo_name: str, private: bool, commit_message: str) -> None:
        self.gh_cli.switch_user(account.username)
        self._ensure_git_repo(folder)
        self._configure_authorship(folder, account)
        self._stage_and_commit(folder, commit_message)
        self.gh_cli.repo_create(folder, repo_name, private)
