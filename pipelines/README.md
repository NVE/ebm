# Azure pipelines

## template-push-to-github.yml

This Azure DevOps template safely pushes commits to a GitHub repository with optional dry-run support.

### Require Azure DevOps variables
 - GITHUB_REPO
 - GITHUB_TOKEN (secret)

### Parameters

| Name             | Description                                      | Default                      |
|------------------|--------------------------------------------------|------------------------------|
| `remote_repo`    | GitHub repo path (e.g., `github.com/org/repo`)   | `$(GITHUB_REPO)`             |
| `remote_branch`  | Branch to push to                                | `$(Build.SourceBranchName)` |
| `git_user_email` | Git user email                                   | `ebm@nve.no`                 |
| `git_user_name`  | Git user name                                    | `Azure DevOps Build Bot`     |
| `dryRun`         | If true, skips the push step                     | `false`                      |

### Features

- Validates repo format
- Configures Git identity
- Checks for divergence
- Supports dry-run mode


## template-pytest-tasks.yml

This Azure DevOps template run pytest and ruff for the source.

### Features
 - Run pytest
 - Ruff check 
 - build the package for testing
 - publishes test reports

## template-twine-upload.yml

Template will build and upload package to `PYPI_REPOSITORY` using Twine.

### Require Azure DevOps variables
 - PYPI_REPOSITORY
 - PYPI_USERNAME
 - PYPI_PASSWORD (secret)

### Features
 - Build package
 - Run twine upload

Do not run this template without testing. The package must have a unique version number. Twine does not allow re-uploading
duplicate versions. 
