# Contributing to MGAS (Multi-GitHub Account Switcher)

Thanks for your interest in improving MGAS! This guide explains how to get set up, propose changes, and reach the maintainer. **The project currently targets Windows only**, so please test contributions on Windows before opening a pull request.

## Getting Started
1. Fork and clone the repository.
2. (Optional) Create a virtual environment: `python -m venv venv && ./venv/Scripts/activate`.
3. Install dependencies: `pip install customtkinter` (plus any new ones you introduce).
4. Run the app locally with `python github_account_switcher.py`.

## Code Style & Structure
- Keep UI logic inside `mgas/ui.py`, CLI/repo helpers inside `mgas/gh_cli.py`, and persistence/settings inside `mgas/accounts.py`.
- Prefer small, testable helpers over large functions. If logic grows, add a new module under `mgas/` and expose it via `mgas/__init__.py`.
- Use descriptive log/error messages; GUI dialogs should explain how to recover from failures.
- Stick to ASCII unless the existing file already uses Unicode characters.

## Feature Workflow
1. Create a feature branch.
2. Update or add documentation (`README.md`, `CONTRIBUTING.md`, etc.) for user-facing changes.
3. Test the GUI manually on Windows (PowerShell or Git Bash) and mention the environment in your PR description.
4. Keep commits focused; large features should be split into logical commits.

## Pull Request Checklist
- [ ] Code compiles and `python github_account_switcher.py` launches successfully on Windows.
- [ ] New modules or scripts are added under the `mgas/` package when appropriate.
- [ ] UI changes include screenshots or clear descriptions.
- [ ] Docs mention any new prerequisites or OS limitations.

## Contact
Have a question or want to discuss an idea before coding?

- **Email:** info.adnansultan@gmail
- **GitHub:** [madnansultandotme](https://github.com/madnansultandotme)
- **LinkedIn:** [dev-madnansultan](https://www.linkedin.com/in/dev-madnansultan)

Thanks for helping make MGAS better!
