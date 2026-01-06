from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List

ACCOUNTS_FILE = os.path.expanduser("~/.github_accounts.json")
SETTINGS_FILE = os.path.expanduser("~/.github_account_switcher_settings.json")
DEFAULT_SETTINGS = {"initial_commit_message": "Initial commit from Multi-GitHub Account Switcher"}


def _ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


@dataclass
class Account:
    label: str
    username: str
    name: str
    email: str


class AccountStore:
    def __init__(self, path: str = ACCOUNTS_FILE):
        self.path = path
        self._accounts: Dict[str, Account] = self._load()

    def _load(self) -> Dict[str, Account]:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
                return {label: Account(label=label, **data) for label, data in raw.items()}
        return {}

    def _persist(self) -> None:
        payload = {
            label: {
                "username": account.username,
                "name": account.name,
                "email": account.email,
            }
            for label, account in self._accounts.items()
        }
        _ensure_dir(self.path)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=4)

    def all(self) -> List[Account]:
        return list(self._accounts.values())

    def get(self, label: str) -> Account | None:
        return self._accounts.get(label)

    def upsert(self, account: Account) -> None:
        self._accounts[account.label] = account
        self._persist()

    def remove(self, label: str) -> None:
        self._accounts.pop(label, None)
        self._persist()


class SettingsManager:
    def __init__(self, path: str = SETTINGS_FILE):
        self.path = path
        self._settings = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return {**DEFAULT_SETTINGS, **data}
        return DEFAULT_SETTINGS.copy()

    def save(self) -> None:
        _ensure_dir(self.path)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self._settings, fh, indent=4)

    def get_commit_message(self) -> str:
        return self._settings.get("initial_commit_message", DEFAULT_SETTINGS["initial_commit_message"])

    def set_commit_message(self, message: str) -> None:
        self._settings["initial_commit_message"] = message or DEFAULT_SETTINGS["initial_commit_message"]
        self.save()
