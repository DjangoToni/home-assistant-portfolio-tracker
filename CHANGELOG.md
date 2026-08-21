# Changelog

All notable changes to Portfolio Tracker are documented here.

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
