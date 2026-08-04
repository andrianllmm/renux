---
name: release
description: Cut a new renux release using commitizen (version bump derived from Conventional Commits history, git tag, build). Use when asked to release, bump the version, or cut a new version of renux.
---

# release

renux's version is derived from git tags via commitizen
(`version_provider = "pep621"`, `tag_format = "v$version"` in
`pyproject.toml`). Never hand-edit the version in `pyproject.toml` or
`src/renux/__init__.py`. Always go through `cz bump`.

## Steps

1. Make sure the working tree is clean and you're on `main`, up to date with
   `origin/main`.
2. Confirm tests and type checks pass:
   ```sh
   poetry run pytest
   poetry run mypy src
   ```
3. Preview the version bump before doing it for real:
   ```sh
   poetry run cz bump --dry-run
   ```
   This inspects Conventional Commits history since the last tag to decide
   patch/minor/major. Confirm the proposed version looks right.
4. Run the real bump (updates version in `pyproject.toml`, updates
   changelog, commits, and creates the `vX.Y.Z` tag):
   ```sh
   poetry run cz bump
   ```
5. Confirm with the user before pushing. Pushing tags/commits is a
   shared-state action:
   ```sh
   git push origin main --tags
   ```
6. Build the distributable if needed:
   ```sh
   poetry build
   ```

## Don't

- Don't manually edit the version number anywhere. It's commitizen's job.
- Don't force-push or delete/re-tag an already-pushed version tag.
- Don't skip the dry run. A stray `feat:`/`fix!:` commit in history can
  cause a bigger bump than expected.
