# Contributing

Contributions and focused bug reports are welcome.

## Bug reports

Please include:

- Home Assistant and Portfolio Tracker versions
- Asset type and symbol, with private transaction data removed
- Relevant `custom_components.portfolio_tracker` log entries
- Steps needed to reproduce the behavior

## Development

1. Fork and clone the repository.
2. Create a virtual environment with Python 3.14.
3. Install a supported Home Assistant release and the test tools:

   ```bash
   python -m pip install homeassistant==2026.11.0 -r requirements_test.txt
   ```

4. Run the automated checks:

   ```bash
   python -m pytest -q
   python -m ruff check custom_components tests --select E9,F63,F7,F82
   python -m compileall -q custom_components
   node --check custom_components/portfolio_tracker/frontend/portfolio-asset-card.js
   ```

5. Copy or link `custom_components/portfolio_tracker` into a Home Assistant development instance and verify the config flow, options flow, entities, notifications, and dashboard cards.
6. Test dashboard changes at desktop and mobile widths.
7. Keep changes focused, preserve existing config entries where possible, and open a pull request describing the user-visible behavior and verification performed.

Do not include API credentials, personal holdings, transaction exports, or Home Assistant diagnostic archives containing private data.
