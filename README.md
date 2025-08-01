# Anthropic Course

A simple Python toy/POC project demonstrating colorful logging with loguru, rich, and Pydantic validation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🚀 **Modern Python**: Follows PEP 621 standards with src-layout
- 📦 **Pixi Package Management**: Fast dependency management with standard `[project.dependencies]`
- 🎨 **Beautiful Logging**: Colorful loguru + rich integration with custom configuration
- 🎯 **CLI Interface**: Typer-based command-line application
- 🔧 **Pydantic Integration**: Data validation and configuration management
- 🧪 **Testing Foundation**: Basic pytest setup for good development habits
- 🎨 **Code Quality**: Ruff for linting and formatting
- 📋 **Semantic Versioning**: Python Semantic Release (PSR) for automated versioning

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [Pixi](https://pixi.sh/) package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd anthropic-course
   ```

2. **Install dependencies with Pixi**
   ```bash
   # Install core dependencies only
   pixi install
   
   # Install with development dependencies
   pixi install --environment dev
   ```

3. **Set up environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

4. **Run the application**
   ```bash
   pixi run start
   ```

## Usage

The main application demonstrates colorful logging, rich formatting, and Pydantic validation:

```bash
# Run with default settings
pixi run start

# Enable debug mode
pixi run start --debug

# Show help
pixi run start --help
```

## Development

### Running Tests
```bash
# Using dev environment (recommended)
pixi run --environment dev test

# Using default environment (if dev tools are available)
pixi run test
```

### Code Quality
```bash
# Lint code (using dev environment)
pixi run --environment dev lint

# Format code (using dev environment)
pixi run --environment dev format
```

### All Development Tasks
```bash
# Run all quality checks (using dev environment)
pixi run --environment dev lint && pixi run --environment dev format && pixi run --environment dev test
```

### Semantic Versioning
```bash
# Check current version (using dev environment)
pixi run --environment dev version --print

# Perform version bump (using dev environment)
pixi run --environment dev version

# Publish release (if configured)
pixi run --environment dev publish
```

#### Version Bump Workflow
1. **Make changes** to your code
2. **Commit with conventional commit message**:
   ```bash
   git add .
   git commit -m "feat: add new feature"  # Minor version bump
   git commit -m "fix: resolve bug"        # Patch version bump
   git commit -m "feat!: breaking change"  # Major version bump
   ```
3. **Check what version will be bumped to**:
   ```bash
   pixi run --environment dev version --print
   ```
4. **Perform the version bump**:
   ```bash
   pixi run --environment dev version
   ```

#### Dev Versioning (Prereleases)
For development versions, use prerelease flags:

```bash
# Check dev version (1.0.0-dev.1)
pixi run --environment dev semantic-release version --print --prerelease --prerelease-token dev

# Create dev version
pixi run --environment dev semantic-release version --prerelease --prerelease-token dev

# Other prerelease tokens
pixi run --environment dev semantic-release version --print --prerelease --prerelease-token alpha  # 1.0.0-alpha.1
pixi run --environment dev semantic-release version --print --prerelease --prerelease-token beta   # 1.0.0-beta.1
pixi run --environment dev semantic-release version --print --prerelease --prerelease-token rc     # 1.0.0-rc.1
```

#### Commit Message Types
| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat:` | **Minor** (1.0.0 → 1.1.0) | `feat: add new logging feature` |
| `fix:` | **Patch** (1.0.0 → 1.0.1) | `fix: resolve debug mode issue` |
| `BREAKING CHANGE:` | **Major** (1.0.0 → 2.0.0) | `feat!: breaking change in API` |
| `docs:`, `style:`, `refactor:`, `test:`, `chore:` | **No bump** | `docs: update README` |

#### What Gets Updated Automatically
- `pyproject.toml:tool.pixi.project.version` (automatically updated by PSR)
- `pyproject.toml:version` (may need manual sync)
- `src/anthropic_course/__init__.py:__version__` (may need manual sync)
- `CHANGELOG.md` with new version entry
- Git tag for the new version

#### Important Notes
- **Local Development**: Use `--no-push` flag to prevent remote push attempts
- **Version Sync**: PSR may not update all version locations automatically in local development
- **Manual Sync**: You may need to manually update `[project].version` and `__init__.py:__version__` to match the PSR version

#### Troubleshooting Version Bumping
If PSR doesn't update all version files automatically:

1. **Check current PSR version**:
   ```bash
   pixi run --environment dev version --print
   ```

2. **Manually sync versions**:
   ```bash
   # Update pyproject.toml [project].version
   # Update src/anthropic_course/__init__.py __version__
   # Update tests if they check version
   ```

3. **Verify application shows correct version**:
   ```bash
   pixi run start
   ```

#### Commit Message Convention
This project uses [Conventional Commits](https://www.conventionalcommits.org/) for semantic versioning:

- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)
- `BREAKING CHANGE:` - Breaking changes (major version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

## Project Structure

```
anthropic-course/
├── pyproject.toml          # Project configuration (PEP 621 + Pixi + PSR)
├── .gitignore             # Comprehensive git ignore patterns
├── .gitattributes         # Git attributes for version files
├── .env.example           # Environment configuration template
├── CHANGELOG.md           # Semantic versioning changelog
├── README.md              # This file
├── src/
│   └── anthropic_course/  # Source package (src-layout)
│       ├── __init__.py    # Package initialization
│       ├── __main__.py    # Module execution entry point
│       ├── main.py        # CLI application
│       └── logger.py      # Logger configuration
└── tests/                 # Test suite
    ├── __init__.py
    └── test_main.py       # Application tests
```

## Dependencies

### Core Dependencies
- **loguru**: Beautiful logging with custom configuration
- **typer**: Modern CLI framework
- **rich**: Rich text and formatting
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings management

### Development Dependencies
Install with `pixi install --environment dev` to include:
- **pytest**: Testing framework
- **ruff**: Fast Python linter and formatter
- **python-semantic-release**: Automated semantic versioning

## Environments

This project uses Pixi environments to separate core and development dependencies:

- **default**: Core application dependencies only
- **dev**: Core dependencies + development tools (pytest, ruff, semantic-release)

### Environment Usage
```bash
# Run application (uses default environment)
pixi run start

# Run development tasks (uses dev environment)
pixi run --environment dev test
pixi run --environment dev lint
pixi run --environment dev format
pixi run --environment dev version
```

## Environment Configuration

Copy `.env.example` to `.env` and customize:

```bash
# Debug mode (true/false)
DEBUG=false

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Application name
APP_NAME=Anthropic Course

# Application version
VERSION=0.1.0
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pixi](https://pixi.sh/) for fast package management
- [Loguru](https://loguru.readthedocs.io/) for beautiful logging
- [Typer](https://typer.tiangolo.com/) for CLI development
- [Rich](https://rich.readthedocs.io/) for rich text and formatting
- [Pydantic](https://pydantic.dev/) for data validation 