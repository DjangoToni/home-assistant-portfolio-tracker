# Portfolio Tracker for Home Assistant

[English](README.md) | [Deutsch](README.de.md)

[![GitHub Release](https://img.shields.io/github/v/release/DjangoToni/home-assistant-portfolio-tracker)](https://github.com/DjangoToni/home-assistant-portfolio-tracker/releases)
[![HACS Validation](https://github.com/DjangoToni/home-assistant-portfolio-tracker/actions/workflows/validate.yml/badge.svg)](https://github.com/DjangoToni/home-assistant-portfolio-tracker/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Home Assistant custom integration for monitoring investment portfolios, transactions, market indices, watchlists, price alerts, and portfolio performance.

Portfolio Tracker provides native Home Assistant entities and two automatically registered dashboard cards. Active assets contribute to portfolio calculations, while watched assets remain completely separate from portfolio value and performance.

## Highlights

- Stocks, ETFs, funds, cryptocurrencies, currencies, and other Yahoo Finance symbols
- CoinGecko market details for cryptocurrencies
- Active positions and a separate watchlist
- Upper and lower price alerts with binary sensors and persistent notifications
- Editable purchase, sale, and opening-balance transaction ledger
- Cost basis, realized and unrealized gains, fees, taxes, total return, and time-weighted return
- Benchmark comparison against configurable market indices
- Detailed 30-day charts with price grid, date/time scale, and market metrics
- Professional portfolio performance chart with daily grid lines
- Multilingual UI: German, English, French, and Italian
- Resilient quote updates that keep the dashboard available during temporary provider outages

## Installation

### HACS

[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=DjangoToni&repository=home-assistant-portfolio-tracker&category=integration)

1. Open **HACS** in Home Assistant.
2. Open the menu in the upper-right corner and select **Custom repositories**.
3. Add `https://github.com/DjangoToni/home-assistant-portfolio-tracker` as category **Integration**.
4. Search for **Portfolio Tracker** and select **Download**.
5. Restart Home Assistant.
6. Open **Settings > Devices & services > Add integration** and search for **Portfolio Tracker**.

### Manual installation

1. Copy `custom_components/portfolio_tracker` into your Home Assistant configuration directory at `custom_components/portfolio_tracker`.
2. Restart Home Assistant.
3. Add **Portfolio Tracker** from **Settings > Devices & services**.

## Initial configuration

The initial setup asks for:

- **Portfolio name**: used for the portfolio device and dashboard title.
- **Base currency**: the currency used for aggregated values, for example `CHF`, `EUR`, or `USD`.
- **Update interval**: how often market data should be refreshed.

After setup, open the integration's **Configure** dialog. Configuration is grouped into:

- **Assets**: add, edit, or remove active and watched assets.
- **Transactions**: maintain purchases, sales, and opening balances.
- **Market & benchmark**: select market indices and the performance benchmark.
- **General settings**: change the base currency and update interval.

The dashboard card contains a **Manage portfolio** button that links directly to the matching Portfolio Tracker configuration entry.

## Assets

### Active positions

Active positions affect portfolio value, allocation, gains, and performance. Enter the symbol exactly as used by Yahoo Finance, for example:

- `NOVN.SW` for Novartis on SIX
- `AAPL` for Apple
- `BTC-USD` for Bitcoin quoted in USD

The initial quantity and purchase price create an opening transaction. Further purchases and sales should be maintained through the transaction ledger. Lower and upper alert thresholds and their current state are shown directly in the **Active assets** table.

### Watched assets

Watched assets receive prices, market details, history, and alerts, but never affect portfolio totals. They are shown in a separate dashboard table with their alert thresholds and current status.

## Transactions

Supported transaction types are opening balance, purchase, and sale. Each transaction can contain:

- Trade date and quantity
- Unit price or complete amount
- Trading and market-price currencies
- Fees and taxes
- Exchange or broker
- Optional note

Portfolio Tracker prevents sales that would result in a negative historical quantity.

## Price alerts

An asset can have a lower threshold, an upper threshold, or both. Portfolio Tracker creates binary sensor entities for configured thresholds and sends one persistent Home Assistant notification when a threshold becomes active. A new notification is possible after the price leaves and later re-enters the alert range.

## Dashboard cards

The integration registers its frontend module automatically. Cards can be added through the Home Assistant dashboard card picker.

### Portfolio overview

```yaml
type: custom:portfolio-overview-card
entity: sensor.my_portfolio_value
view_mode: table
```

Set `view_mode` to `overview` for allocation-focused display or `table` for the detailed active-assets table.

### Asset details

```yaml
type: custom:portfolio-asset-card
entity: sensor.apple_price
```

Rows in the active-assets and watched-assets tables can also be expanded directly into the same detail view.

## Data sources

- [Yahoo Finance](https://finance.yahoo.com/) supplies quotes, exchange rates, stock details, market indices, and stock history.
- [CoinGecko](https://www.coingecko.com/) supplies extended cryptocurrency market data and history.

Public provider endpoints can occasionally be unavailable or rate limited. Portfolio Tracker retains the last successful data after startup and retries on the next scheduled update.

## Troubleshooting

### Dashboard shows “Configuration error”

1. Confirm that Home Assistant has been restarted after installation or update.
2. Confirm that Portfolio Tracker is loaded under **Settings > Devices & services**.
3. Reload the dashboard once. The card URL contains a version marker to avoid stale frontend files.
4. Check **Settings > System > Logs** for `custom_components.portfolio_tracker`.

### No quotes are available

Temporary Yahoo Finance failures do not remove existing entities. Once data has previously loaded, the last successful values remain available until the provider responds again.

### Integration is not offered after HACS installation

Restart Home Assistant and refresh the browser. HACS installs integrations into `custom_components`, but Home Assistant only discovers new custom integrations during startup.

## Privacy and disclaimer

Symbols, portfolio configuration, and transactions remain in the Home Assistant configuration entry. Market-data requests send only the required symbols or CoinGecko identifiers to the respective providers.

Portfolio Tracker is an informational tool, not financial advice. Market data may be delayed, incomplete, or inaccurate and must not be used as the sole basis for investment decisions.

## Support and development

- Report bugs or request features through [GitHub Issues](https://github.com/DjangoToni/home-assistant-portfolio-tracker/issues).
- See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.
- Security concerns are covered in [SECURITY.md](SECURITY.md).
- Release history is available in [CHANGELOG.md](CHANGELOG.md).

## License

Released under the [MIT License](LICENSE).
