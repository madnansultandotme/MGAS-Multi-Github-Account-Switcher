from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import customtkinter as ctk
from tkinter import PhotoImage, filedialog, messagebox, ttk

from .accounts import Account, AccountStore, SettingsManager, DEFAULT_SETTINGS
from .gh_cli import GitHubCLI, RepoBootstrapper

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def resource_path(*relative_parts: str) -> Path:
    """Resolve resources both in source tree and within PyInstaller bundles."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base_path.joinpath(*relative_parts)


class AccountSwitcherApp:
    def __init__(self):
        self.account_store = AccountStore()
        self.settings = SettingsManager()
        self.gh_cli = GitHubCLI()
        self.repo_bootstrapper = RepoBootstrapper(self.gh_cli)
        self._icon_image: PhotoImage | None = None

        self.app = ctk.CTk()
        self.app.title("Multi-GitHub Account Switcher")
        self.app.geometry("920x680")
        self.app.grid_rowconfigure(2, weight=1)
        self.app.grid_columnconfigure(0, weight=1)

        self._apply_branding()
        self._build_layout()
        self.refresh_list()
        self.update_status()

    def _apply_branding(self):
        icon_path = resource_path("images", "icon.ico")
        logo_path = resource_path("images", "logo.png")

        if icon_path.exists():
            try:
                self.app.iconbitmap(str(icon_path))
            except Exception:
                pass

        if logo_path.exists():
            try:
                self._icon_image = PhotoImage(file=str(logo_path))
                self.app.iconphoto(True, self._icon_image)
            except Exception:
                pass

    # region UI construction
    def _build_layout(self):
        header = ctk.CTkLabel(
            self.app,
            text="Manage multiple GitHub identities with one click",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))

        sub = ctk.CTkLabel(
            self.app,
            text="Store profiles, authenticate via PAT, switch gh auth, and bootstrap repos without leaving this window.",
            wraplength=840,
        )
        sub.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.main_frame = ctk.CTkFrame(self.app)
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.main_frame.grid_rowconfigure(0, weight=6)
        self.main_frame.grid_rowconfigure(2, weight=4)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._build_account_table()
        self._build_status_label()
        self._build_controls()

    def _build_account_table(self):
        table_frame = ctk.CTkFrame(self.main_frame)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Status", "Label", "Username", "Name", "Email"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        self.tree.heading("Status", text="Active")
        self.tree.heading("Label", text="Label")
        self.tree.heading("Username", text="GitHub Username")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Email", text="Email")
        self.tree.column("Status", width=60, anchor="center", stretch=False)
        self.tree.column("Label", width=120, anchor="w", stretch=True)
        self.tree.column("Username", width=160, anchor="w", stretch=True)
        self.tree.column("Name", width=180, anchor="w", stretch=True)
        self.tree.column("Email", width=220, anchor="w", stretch=True)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_status_label(self):
        self.status_label = ctk.CTkLabel(self.main_frame, text="Current Active: Checking...", anchor="w")
        self.status_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

    def _build_controls(self):
        controls = ctk.CTkFrame(self.main_frame)
        controls.grid(row=2, column=0, sticky="nsew")
        controls.grid_columnconfigure(0, weight=3)
        controls.grid_columnconfigure(1, weight=1)

        self._build_form_section(controls)
        self._build_actions_section(controls)

    def _build_form_section(self, parent):
        form = ctk.CTkFrame(parent)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Add account via Personal Access Token", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 15)
        )

        self.label_entry = ctk.CTkEntry(form)
        self.username_entry = ctk.CTkEntry(form)
        self.name_entry = ctk.CTkEntry(form)
        self.email_entry = ctk.CTkEntry(form)
        self.protocol_var = ctk.StringVar(value="HTTPS")
        self.protocol_dropdown = ctk.CTkComboBox(form, values=["HTTPS", "SSH"], variable=self.protocol_var)
        self.token_entry = ctk.CTkEntry(form, show="*")

        rows = [
            ("Label", self.label_entry),
            ("GitHub Username", self.username_entry),
            ("Full Name", self.name_entry),
            ("Email", self.email_entry),
            ("Git Protocol", self.protocol_dropdown),
            ("Personal Access Token", self.token_entry),
        ]

        for idx, (text, widget) in enumerate(rows, start=1):
            ctk.CTkLabel(form, text=text).grid(row=idx, column=0, sticky="w", padx=8, pady=4)
            widget.grid(row=idx, column=1, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(
            form,
            text="Use a fine-grained PAT (repo + admin:public_key). Token is piped directly to gh auth login.",
            wraplength=360,
            justify="left",
        ).grid(row=len(rows) + 1, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 6))

        ctk.CTkButton(form, text="Add & Authenticate Account", command=self.handle_add_account, fg_color="#2563EB").grid(
            row=len(rows) + 2, column=0, columnspan=2, padx=8, pady=(10, 12), sticky="ew"
        )

    def _build_actions_section(self, parent):
        actions = ctk.CTkFrame(parent)
        actions.grid(row=0, column=1, sticky="nsew", pady=10)
        actions.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(actions, text="Account & Repo Actions", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, pady=(10, 8)
        )

        buttons = [
            ("Switch Global Authentication", self.handle_global_switch, "green"),
            ("Remove Selected Account", self.handle_remove_account, "#B91C1C"),
            ("Initialize Folder & Push", self.handle_repo_init, None),
            ("Refresh Active Status", self.update_status, None),
            ("Settings", self.open_settings, None),
        ]

        for idx, (text, command, color) in enumerate(buttons, start=1):
            ctk.CTkButton(actions, text=text, command=command, fg_color=color).grid(
                row=idx, column=0, sticky="ew", padx=12, pady=5
            )
    # endregion

    # region UI helpers
    def run(self):
        self.app.mainloop()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Get the active username
        active_username = self._get_active_username()
        
        for account in self.account_store.all():
            # Mark active account with a checkmark
            status = "✓" if account.username == active_username else ""
            self.tree.insert("", "end", iid=account.label, values=(status, account.label, account.username, account.name, account.email))

    def update_status(self):
        try:
            status_text = self.gh_cli.auth_status()
            self.status_label.configure(text=status_text)
        except FileNotFoundError:
            self.status_label.configure(text="GitHub CLI not installed")
        except Exception as e:
            self.status_label.configure(text=f"Error checking status: {str(e)}")
        
        # Refresh the list to update active indicators
        self.refresh_list()
    
    def _get_active_username(self) -> str | None:
        """Get the currently active GitHub username from gh CLI."""
        try:
            result = self.gh_cli.get_active_user()
            return result
        except Exception:
            return None

    def _selected_account(self) -> Account | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Select an account first")
            return None
        label = selection[0]
        account = self.account_store.get(label)
        if not account:
            messagebox.showerror("Missing", "Selected account no longer exists")
        return account

    def clear_form(self):
        for entry in [self.label_entry, self.username_entry, self.name_entry, self.email_entry, self.token_entry]:
            entry.delete(0, "end")
        self.protocol_var.set("HTTPS")
    # endregion

    # region Event handlers
    def handle_add_account(self):
        label = self.label_entry.get().strip()
        username = self.username_entry.get().strip()
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        token = self.token_entry.get().strip()
        protocol = self.protocol_var.get().lower()

        if not all([label, username, name, email]):
            messagebox.showerror("Error", "All required fields must be filled")
            return
        if not token:
            messagebox.showerror("Error", "Personal access token is required")
            return

        try:
            self.gh_cli.auth_with_token(protocol, token)
            try:
                self.gh_cli.setup_git()
            except subprocess.CalledProcessError:
                pass

            account = Account(label=label, username=username, name=name, email=email)
            self.account_store.upsert(account)
            self.refresh_list()
            self.update_status()
            self.clear_form()
            messagebox.showinfo("Success", f"Account '{label}' added and authenticated")
        except FileNotFoundError:
            messagebox.showerror("GitHub CLI Missing", "Could not locate the 'gh' executable. Install GitHub CLI and try again.")
        except subprocess.CalledProcessError as err:
            error_msg = err.stderr or err.stdout or str(err)
            messagebox.showerror("Authentication Failed", f"Error during authentication: {error_msg}")

    def handle_global_switch(self):
        account = self._selected_account()
        if not account:
            return
        try:
            self.gh_cli.switch_user(account.username)
            self.update_status()
            messagebox.showinfo("Success", f"Switched global auth to {account.label} ({account.username})")
        except FileNotFoundError:
            messagebox.showerror("GitHub CLI Missing", "Install GitHub CLI to switch accounts.")
        except subprocess.CalledProcessError as err:
            messagebox.showerror("Error", f"Switch failed: {err.stderr or err.stdout or err}")

    def handle_remove_account(self):
        account = self._selected_account()
        if not account:
            return
        if messagebox.askyesno("Confirm", f"Remove account '{account.label}'?"):
            self.account_store.remove(account.label)
            self.refresh_list()
            self.update_status()
            messagebox.showinfo("Removed", f"Account '{account.label}' deleted")

    def handle_repo_init(self):
        account = self._selected_account()
        if not account:
            return
        folder = filedialog.askdirectory(title="Select Repository Folder")
        if not folder:
            return

        # Automatically use the folder name as the repo name
        repo_name = Path(folder).name
        
        private = messagebox.askyesno("Visibility", f"Make repository '{repo_name}' private?")
        commit_message = self.settings.get_commit_message()

        try:
            self.repo_bootstrapper.initialize_and_push(folder, account, repo_name, private, commit_message)
            messagebox.showinfo("Success", f"Repository '{repo_name}' initialized and pushed to GitHub.")
        except FileNotFoundError:
            messagebox.showerror("GitHub CLI Missing", "Install GitHub CLI to create repositories.")
        except RuntimeError as err:
            messagebox.showerror("Error", str(err))
        except subprocess.CalledProcessError as err:
            messagebox.showerror("Git Error", err.stderr or err.stdout or str(err))

    def open_settings(self):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Settings")
        dialog.geometry("420x220")
        dialog.transient(self.app)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Default initial commit message", font=ctk.CTkFont(size=15, weight="bold")).pack(
            pady=(20, 10)
        )
        entry = ctk.CTkEntry(dialog, width=360)
        entry.insert(0, self.settings.get_commit_message())
        entry.pack(pady=(0, 20))

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)

        def save_settings():
            new_value = entry.get().strip() or DEFAULT_SETTINGS["initial_commit_message"]
            self.settings.set_commit_message(new_value)
            messagebox.showinfo("Settings", "Default commit message updated.")
            dialog.destroy()

        ctk.CTkButton(button_frame, text="Save", command=save_settings).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy, fg_color="#6b7280").grid(row=0, column=1, padx=10)
    # endregion
