# Vector: AI Agents Lab

<h2 align="center">💖 Sponsored By</h2>

<p align="center">
  <a href="https://www.outskill.com/" target="_blank">
    <img src="https://img.shields.io/static/v1?label=&message=OUTSKILL&color=95FF00&style=for-the-badge&labelColor=1C1C1C" alt="Outskill" />
  </a>
  <a href="https://deepstation.ai/" target="_blank">
    <img src="https://img.shields.io/static/v1?label=&message=DEEPSTATION&color=5E17EB&style=for-the-badge&labelColor=0B0033" alt="DeepStation" />
  </a>
</p>



## Project Overview
Vector is an AI Agents Lab developed for people willing to learn how to build AI Agents.  
  
The projects in Vector are divided into 3 categories based on their complexity - 
1. `src/beginner` -
   - Entry Level Projects meant for people just starting out with Agents.
   - All agents are under 100 lines of code.
   - Single Agent Single Tool Systems

2. `src/intermediate` -
   - These projects are aimed at people well versed with basics for AI Agents.
   - Multi Agent Multi Tool projects.
  
3. `src/advanced` -
   - End to End projects utilizing multiple concepts within AI Agents.
   - Takes care of best practices and aimed at building products.
  

## Project Setup

This project uses [uv](https://docs.astral.sh/uv/) as a package manager for fast, reliable dependency management.

### Prerequisites
- Python 3.11 or higher
- pip (for installing uv)

### Setup Steps

1. **Install `uv`**  
   Follow instructions at the [installation](https://docs.astral.sh/uv/getting-started/installation/) page or run:
   ```bash
   pip install uv
   ```

2. **Clone the repository**  
   ```bash
   git clone https://github.com/ishandutta0098/vector-ai-agents-lab.git
   cd vector-ai-agents-lab
   ```

3. **Install dependencies**  
   ```bash
   uv sync
   ```
   This command:
   - Creates a virtual environment in `.venv/`
   - Installs all required packages from `pyproject.toml`
   - Locks dependencies for reproducible builds

4. **Run a script**  
   ```bash
   uv run src/beginner/website_scraper/crewai_scrape.py
   ```

## Usage

### Running Scripts
Use `uv run` to execute any Python script in the project:
```bash
uv run <path-to-script>.py
```

The `uv run` command automatically:
- Uses the project's virtual environment
- Ensures all dependencies are available
- Handles Python version compatibility

### Adding Dependencies
```bash
uv add <package-name>
```

### Removing Dependencies
```bash
uv remove <package-name>
```

## Notes

- Dependencies are managed in `pyproject.toml`
- The virtual environment is created in `.venv/` (git-ignored)
- `uv.lock` ensures reproducible installations across different machines
- No need to manually activate the virtual environment when using `uv run`

## Troubleshooting

**Issue**: Import errors when running scripts  
**Solution**: Make sure you've run `uv sync` to install all dependencies

**Issue**: Python version mismatch  
**Solution**: Ensure you have Python 3.11+ installed: `python --version`

**Issue**: `uv` command not found  
**Solution**: Reinstall uv with `pip install uv` and ensure pip's bin directory is in your PATH

## Contributing
Contributions are welcome to Vector!
  
If you have a project idea raise an Issue with it along with how you plan to implement it.   
Please don't raise a PR until your project has been approved.
  
## License 
This project is under the MIT License.

## Contact
Email - duttaishan0098@gmail.com
[LinkedIn](https://www.linkedin.com/in/ishandutta0098/)
[X](https://x.com/ishandutta0098)
[Instagram](https://www.instagram.com/ishandutta.ai)
