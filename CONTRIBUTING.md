# Contributing to TARS

Thank you for being here.

TARS is built with a simple belief: good tools should feel calm, clear, and humane.
We care deeply about useful features, but we also believe in achieving more with less:
solutions should be powerful without becoming heavy, and ambitious without becoming
needlessly complicated.

This guide is not only about how to open a PR. It is also about how we hope to build
software together: with care, clarity, and respect for the next person reading the code.

## Maintainers

| Maintainer | Focus |
|------------|-------|
| [@zandenkoh](https://github.com/zandenkoh) | Project lead, `main` branch |

## Branching Strategy

We use a two-branch model to balance stability and exploration:

| Branch | Purpose | Stability |
|--------|---------|-----------|
| `main` | Stable releases | Production-ready |

### Which Branch Should I Target?

**Target `main` if your PR includes:**

- Bug fixes with no behavior changes
- Documentation improvements
- Minor tweaks that don't affect functionality

**When in doubt, target `main`.**

### Quick Summary

| Your Change | Target Branch |
|-------------|---------------|
| New feature | `main` |
| Bug fix | `main` |
| Documentation | `main` |
| Refactoring | `main` |
| Unsure | `main` |

## Development Setup

Keep setup boring and reliable. The goal is to get you into the code quickly:

```bash
# Clone the repository
git clone https://github.com/zandenkoh/TARS.git
cd TARS

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check TARS/

# Format code
ruff format TARS/
```

## Code Style

We care about more than passing lint. We want TARS to stay small, calm, and readable.

When contributing, please aim for code that feels:

- Simple: prefer the smallest change that solves the real problem
- Clear: optimize for the next reader, not for cleverness
- Decoupled: keep boundaries clean and avoid unnecessary new abstractions
- Honest: do not hide complexity, but do not create extra complexity either
- Durable: choose solutions that are easy to maintain, test, and extend

In practice:

- Line length: 100 characters (`ruff`)
- Target: Python 3.11+
- Linting: `ruff` with rules E, F, I, N, W (E501 ignored)
- Async: uses `asyncio` throughout; pytest with `asyncio_mode = "auto"`
- Prefer readable code over magical code
- Prefer focused patches over broad rewrites
- If a new abstraction is introduced, it should clearly reduce complexity rather than move it around

## Questions?

If you have questions, ideas, or half-formed insights, you are warmly welcome here.

Please feel free to open an [issue](https://github.com/zandenkoh/TARS/issues), join the community, or simply reach out:

- [Discord](https://discord.gg/MnCvHqpUGB)
- [Feishu/WeChat](./COMMUNICATION.md)
- Email: Zanden Koh (@zandenkoh) — <[EMAIL_ADDRESS]>

Thank you for spending your time and care on TARS. We would love for more people to participate in this community, and we genuinely welcome contributions of all sizes.
