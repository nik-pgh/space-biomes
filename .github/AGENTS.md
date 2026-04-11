# .github/ — Agent Guide

This directory contains GitHub Actions workflows, issue templates, custom actions, and autoapproval config.

## Structure

| Path               | Purpose                                                             |
| ------------------ | ------------------------------------------------------------------- |
| `workflows/`       | CI/CD workflow definitions (YAML)                                   |
| `ISSUE_TEMPLATE/`  | Issue templates (bug report, feature request, docs improvement)     |
| `actions/`         | Reusable composite actions (LFS caching, yarn install, Bazel setup) |
| `autoapproval.yml` | Config for auto-approving certain PRs                               |

## Constraints

- **Do not modify workflows** without explicit approval. CI changes affect all contributors.
- **Do not delete or rename issue templates.** You may add new templates if there's a concrete need.
- **Do not modify composite actions** in `actions/` — these are shared CI infrastructure.

## Common tasks

### Adding a new issue template

Create a new file in `ISSUE_TEMPLATE/` following the existing frontmatter format:

```yaml
---
name: Template Name
about: One-line description
title: ""
labels: ""
assignees: ""
---
```

### Understanding which CI runs on a PR

Each workflow has a `paths` trigger. Check the `on.pull_request.paths` field to see which file changes activate it:

- `src/` changes → `ts-ci.yml`
- `voxeloo/` changes → `cpp-ci.yml`
- `src/galois/` changes → `galois-ci.yml`
- `docs/` changes → `docs-deploy.yml`, `docs-test-deploy.yml`

## Validation

If you modify anything here, the change cannot be locally tested in full (workflows run on GitHub). Validate YAML syntax at minimum:

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/your-file.yml'))"
```
