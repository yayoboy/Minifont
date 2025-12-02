# Contributing to Minifont

Thank you for your interest in contributing to Minifont! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Minifont.git
   cd Minifont
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:
   ```bash
   pytest
   ```

4. Format your code:
   ```bash
   black src/ tests/
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request on GitHub

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable names

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage
- Place tests in the `tests/` directory

## Adding New Export Formats

To add a new export format:

1. Create a new exporter class in `src/minifont/exporters.py`:
   ```python
   class NewFormatExporter(BaseExporter):
       def export(self, glyphs: List[GlyphBitmap], output_path: str) -> None:
           # Implementation here
           pass
   ```

2. Add the format to `EXPORT_FORMATS` in `src/minifont/cli.py`

3. Write tests in `tests/test_exporters.py`

4. Update documentation

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Minifont version
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages or logs

## Feature Requests

Feature requests are welcome! Please:

- Check if the feature has already been requested
- Clearly describe the feature and its use case
- Explain why it would be useful to other users

## Questions?

Feel free to open an issue for questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
