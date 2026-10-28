[![Release](https://img.shields.io/github/v/release/merci-L/MyAITools?label=release)](https://github.com/merci-L/MyAITools/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/merci-L/MyAITools/ci.yml?branch=main&label=CI)](https://github.com/merci-L/MyAITools/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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

Or install directly from GitHub (no clone needed):

```powershell
pip install git+https://github.com/merci-L/MyAITools.git
```

## Available tools

| Command | Description | Example |
| --- | --- | --- |
| `word-count` | Count characters, words, and lines in a text file | `myaitools word-count README.md` |
| `sys-radar` | Show CPU, memory, and disk usage | `myaitools sys-radar` |
| `jd-detector` | Detect sales / field-promotion job posts via DeepSeek API | `myaitools jd-detector --file jd.txt` |

`jd-detector` requires the `DEEPSEEK_API_KEY` environment variable. See [docs/jd-detector.md](docs/jd-detector.md) for details.

### Real-world example

Calling DeepSeek (`deepseek-chat`) on a real job post:

```powershell
python -m myaitools jd-detector "招聘地推专员，要求吃苦耐劳，单休，底薪3000，年薪四十万不是梦"
```

```text
结论: 是销售/地推岗位
置信度: 98%
理由: 职位为地推专员，职责为地面推广拉新获客，属销售/地推岗位。
```

## Web UI (Streamlit)

Besides the CLI, the project ships a minimal Streamlit UI with two tabs: System Radar and JD Detector.

```powershell
# from the repository root
pip install -e .
streamlit run src/myaitools/app.py
```

Open <http://localhost:8501> if the browser does not open automatically. System Radar works out of the box; JD Detector requires `DEEPSEEK_API_KEY` (enter it in the sidebar or set the environment variable).

The UI follows a "precision archive card" visual world (paper sheets, calibrated gauges, stamped verdicts). Design tokens live in [DESIGN.md](DESIGN.md); product context lives in [PRODUCT.md](PRODUCT.md).

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
