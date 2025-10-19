# Contributing

Thank you for your interest in contributing to CarbonTrack!

## Development Workflow

1. Fork the repository and clone your fork.
2. Create a feature branch from `main` using a descriptive name.
3. Make your changes with clear, scoped commits.
4. Run tests locally and ensure linters pass.
5. Open a Pull Request (PR) into `main`.
6. Address CI feedback and reviewer comments.
7. Merge via the PR once approvals and checks pass.

## PR-only CI/CD and Deployments

We do not deploy on direct pushes to `main`.

- Frontend and backend deployments are triggered only when a Pull Request is merged into `main` (or via manual workflow dispatch for emergencies).
- A guard workflow blocks direct pushes to `main` unless the commit originated from a merged PR.

## Branch Protection Settings (GitHub → Settings → Branches)

Add a branch protection rule for `main`:

- Require a pull request before merging (at least 1 approved review).
- Require status checks to pass before merging (select CI checks).
- Dismiss stale approvals when new commits are pushed (optional).
- Require linear history (optional).
- Restrict who can push to matching branches (optional).

These settings, combined with our workflows, ensure changes land via PRs and deployments only occur after code review.
