# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2026-11-05

### Fixed

- Check out the public lists repository over HTTPS so SSH authentication failures cannot stop generation. Load the deploy key only for publishing changed lists, verify the GitHub host key, and clean up temporary credentials. (https-lists-checkout)

## [1.1.0] - 2026-10-13

### Added

- Added V2Fly's maintained OpenAI domain rules as a second community source,
  plus hostnames from OpenAI's official network guide, expanding the OpenAI
  domain subscription from 31 entries at the previous release.
- Added OpenAI's official ChatGPT Voice server IP feed, with IPv4 subscription
  variants and per-range source timestamp. These ranges cover Voice on UDP
  port 3478, not general ChatGPT or API destinations.
- Added URL patterns from Microsoft's official, regularly updated Microsoft
  365 Worldwide endpoint feed to the Microsoft domain subscription.
- Added a source audit covering all configured providers and the supplied
  OpenAI observations, distinguishing destination IPs from egress IPs.
- Included domain source URLs in the generated coverage report.

### Changed

- Documented that OpenAI's crawler and integration IP feeds describe outbound
  source addresses and remain excluded from client VPN destination lists.
- Clarified that provider subscriptions reflect the documented scope of their
  sources and cannot guarantee every dynamic third-party dependency.

## [1.0.0] - 2026-10-13

### Added

- Configurable generation of domain subscriptions for 27 provider and service
  selections, including aggregated Google service rules.
- Domain parsing from v2fly, Clash, and MetaCubeX sources, with normalization,
  deduplication, deterministic ordering, and filtering of rules rejected by the
  GL.iNet Subscription URL parser.
- Attributable IPv4 and IPv6 CIDR subscriptions from official Google,
  Microsoft 365, and Telegram sources and documented community GeoIP sources
  for Meta, Netflix, and X. Shared Google Cloud customer ranges are excluded.
- CIDR validation, normalization, safe collapsing, and per-range source and
  update timestamps in a machine-readable coverage report.
- Canonical `-domains`, `-ips-v4`, `-ips-v6`, `-ips`, `-combined-v4`,
  `-combined-v6`, and `-combined` list formats where reliable data exists.
- Validation and offline tests for generated rules, aggregation, source
  attribution, CIDR syntax, and output integrity.
- Automated publication to the separate lists repository after generator
  changes, daily, or by manual dispatch, using a dedicated deploy key.
- Generated subscription catalog, source-license attribution, and GL.iNet VPN
  client compatibility guidance in the published lists repository.
