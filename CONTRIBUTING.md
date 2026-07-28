# Contributing

Contributions are welcome! This guide covers how to set up the project and
submit changes.

## Setup

1. Fork and clone the repo
   ```sh
   git clone https://github.com/<your-username>/renux.git
   cd renux
   ```
2. Install dependencies with [Poetry](https://python-poetry.org/)
   ```sh
   poetry install
   ```
3. Install the pre-commit hooks
   ```sh
   poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

## Making changes

1. Create a feature branch
   ```sh
   git checkout -b feature/AmazingFeature
   ```
2. Make your changes.
3. Run tests
   ```sh
   poetry run pytest
   ```
4. Run type checks
   ```sh
   poetry run mypy src
   ```
5. Format and lint (also runs automatically via pre-commit on commit)
   ```sh
   poetry run black .
   poetry run isort .
   ```

## Committing

Commit messages must follow [Conventional
Commits](https://www.conventionalcommits.org/) (enforced by
[Commitizen](https://commitizen-tools.github.io/commitizen/) via the
`commit-msg` hook), e.g.:

```
feat: add date placeholder support
fix: handle empty replacement string
docs: update usage examples
```

You can use `poetry run cz commit` for a guided prompt.

## Submitting

1. Push to your fork
   ```sh
   git push origin feature/AmazingFeature
   ```
2. Open a pull request against `main`, describing what changed and why.
3. Ensure CI (tests, type checks, pre-commit) passes on your PR.

## Reporting issues

Use [GitHub Issues](https://github.com/andrianllmm/renux/issues) for bug
reports and feature requests. Include steps to reproduce, expected vs. actual
behavior, and your OS/Python version for bugs.
