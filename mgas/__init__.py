"""MGAS (Multi-GitHub Account Switcher) package."""

from .accounts import Account, AccountStore, SettingsManager, DEFAULT_SETTINGS
from .gh_cli import GitHubCLI, RepoBootstrapper
from .ui import AccountSwitcherApp

__all__ = [
    "Account",
    "AccountStore",
    "SettingsManager",
    "DEFAULT_SETTINGS",
    "GitHubCLI",
    "RepoBootstrapper",
    "AccountSwitcherApp",
]
