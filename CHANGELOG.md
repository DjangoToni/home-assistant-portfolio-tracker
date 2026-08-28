# Changelog

All notable changes to Portfolio Tracker are documented here.

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
