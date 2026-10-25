# MyAITools

[简体中文](README.md) | [English](README.en.md)

A growing collection of lightweight, composable Python command-line tools.

## Features

- **One tool per module** — independent, easy to read, change, or delete
- **A single CLI entry point** — every tool is exposed as `myaitools <command>`
- **Standard `src` layout + `pyproject.toml`** — editable install for development, ready for PyPI
- **Quality built in** — pytest, ruff, GitHub Actions CI, and pre-commit hooks
- **Open-source ready** — LICENSE, contribution guide, code of conduct, issue/PR templates, changelog

## Project layout

```text
MyAITools/
├── .github/                  # Issue / PR templates and CI workflow
├── docs/                     # Documentation
├── src/myaitools/            # The single source package
│   ├── cli.py                # CLI entry point and subcommand registration
│   └── tools/                # One module per tool
├── tests/                    # pytest test suite
├── pyproject.toml            # Project metadata, dependencies, tool config
├── README.md / README.en.md  # Chinese / English docs
└── CHANGELOG.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE
```

## Quick start

Requires Python 3.10+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"

myaitools --help
myaitools word-count README.md
```

## Available tools

| Command | Description | Example |
| --- | --- | --- |
| `word-count` | Count characters, words, and lines in a text file | `myaitools word-count README.md` |
| `sys-radar` | Show CPU, memory, and disk usage | `myaitools sys-radar` |

## Adding a tool

See [docs/adding-a-tool.md](docs/adding-a-tool.md). In short:

1. Add a module under `src/myaitools/tools/` implementing `name`, `help`, `add_arguments()`, and `run()`
2. Register it in `TOOL_REGISTRY` in `src/myaitools/tools/__init__.py`
3. Add tests, then update this README and `CHANGELOG.md`

## Development

```powershell
ruff check .
ruff format .
pytest
pytest --cov=myaitools
pre-commit install
```

## Git and releases

See [docs/git-workflow.md](docs/git-workflow.md) for the full walkthrough covering local initialization, pushing to GitHub, branching, commit conventions, tagging, and publishing.

## License

[MIT](LICENSE) © 2026 merci_L
