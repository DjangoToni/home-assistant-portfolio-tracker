# Changelog

All notable changes to Portfolio Tracker are documented here.

## 1.8.2 - 2026-11-05

- Register the duplicate-consolidation command in the Home Assistant WebSocket
  schema so the backend accepts the dashboard action.
- Keep the allowed manager actions in one shared backend constant and add a
  regression test preventing another schema/implementation mismatch.

## 1.8.1 - 2026-11-05

- Add an explicitly confirmed duplicate-asset consolidation action to the
  dashboard manager.
- Keep the established active asset ID while merging unique transactions,
  alerts, and missing instrument metadata for matching symbols.
- Count copied transaction IDs only once and reject unsafe combined histories
  atomically without changing the original portfolio.
- Remove obsolete duplicate devices and entities through the existing registry
  cleanup after the portfolio reloads.

## 1.8.0 - 2026-11-05

- Add an administrator-only portfolio manager directly to the Lovelace overview
  card for active assets, watched assets, warrants, transactions, and alerts.
- Support Swissquote, Yahoo Finance, and numeric Home Assistant sensor settings
  when adding or editing warrants from the dashboard.
- Add complete dashboard-manager translations for German, English, French, and
  Italian, including responsive mobile layouts and accessible confirmation UI.
- Protect dashboard writes with per-portfolio locks, revision conflict checks,
  atomic rollback, strict input validation, and transaction-balance checks.
- Keep the full integration configuration available for portfolio-wide market,
  notification, benchmark, and general settings.
- Add manager regression tests for permissions, conflicts, warrants, alerts,
  transaction metadata, deletion confirmation, and failed-write rollback.

## 1.7.1 - 2026-11-05

- Restore Swiss warrant lookup for current Swissquote search responses that no
  longer consistently label SIX products as `WAR` or `EXO`.
- Retry failed mobile price-alert deliveries on the next update while still
  suppressing duplicate notifications after a successful delivery.
- Add the Home Assistant `finance` integration category.
- Add automated calculation, transaction, provider-parser, coordinator,
  translation, and release-artifact tests.
- Validate the integration against Home Assistant 2026.9.1 and 2026.11.0 in CI.

## 1.7.0 - 2026-09-06

- Add configurable mobile push notifications for price alerts through Home
  Assistant notify entities.
- Allow persistent Home Assistant price-alert notifications to be disabled.
- Verified compatibility with Home Assistant 2026.9.1.
- Store the coordinator in typed config-entry runtime data and explicitly bind it
  to the config entry for cleaner lifecycle handling.
- Avoid entity updates when fetched portfolio data has not changed.
- Validate integration imports against Home Assistant 2026.9.1 on Python 3.14.

## 1.6.2 - 2026-08-28

- Allow lower and upper alert thresholds to be removed by clearing their fields.

## 1.6.1 - 2026-08-28

- Added 30-day Swissquote OHLCV history and detail charts for SIX and Swiss DOTS warrants.
- Fixed cleared lower and upper alert thresholds being restored while editing an asset.

## 1.6.0 - 2026-08-22

- Added Swissquote as a dedicated price source for Swiss warrants.
- Added exact valor-number lookup and venue validation for SIX Structured Products and Swiss DOTS.
- Added last, bid, ask, midpoint, previous-close, currency, and timestamp quote normalization.
- Kept the last successful quote available during temporary Swissquote failures.
- Made Swissquote with midpoint pricing the default for newly configured Swiss warrants.

## 1.5.1 - 2026-08-21

- Optimized warrant configuration for Swiss SIX Structured Products and Swiss DOTS.
- Made the Swiss valor number mandatory for Swiss warrant venues and defaulted quote currency to CHF.
- Added selectable external sensor pricing from state, bid, ask, or bid/ask midpoint.
- Added bid, ask, spread, selected price mode, and trading venue to warrant details.
- Added graceful state-price fallback when bid or ask attributes are temporarily missing.

## 1.5.0 - 2026-08-21

- Added a dedicated warrant workflow for active positions and watched assets.
- Added Yahoo Finance and numeric Home Assistant sensor price sources for warrants.
- Added warrant metadata including ISIN, WKN, valor number, issuer, underlying, type, strike, ratio, and expiry.
- Added warrant details, transactions, and price-alert states to the dashboard.
- Added immediate refreshes when a configured Home Assistant price sensor changes.
- Added complete German, English, French, and Italian warrant configuration texts.

## 1.4.2 - 2026-08-20

- Added lower and upper alert thresholds to the active-assets dashboard table.
- Added live alert states for active assets: armed, triggered, or not configured.
- Updated watched-asset alert states to distinguish armed alerts from passive monitoring.

## 1.4.1 - 2026-08-20

- Added complete German, English, French, and Italian localization.
- Added locale-aware numbers, dates, times, dynamic option labels, and price-alert notifications.
- Added direct dashboard navigation to the matching Portfolio Tracker configuration entry.
- Reorganized configuration into Assets, Transactions, Market & benchmark, and General settings.
- Added active-assets and watched-assets dashboard tables with expandable detail views.
- Improved price and performance charts with finer grid lines and right-side price labels.
- Added upper and lower price alerts with binary sensors and persistent notifications.
- Improved resilience during temporary Yahoo Finance outages.
- Fixed non-numeric market-status sensors being treated as numeric sensors.
