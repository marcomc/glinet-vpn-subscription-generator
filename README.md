# GL.iNet VPN subscription generator

[![Validate generator](https://github.com/marcomc/glinet-vpn-subscription-generator/actions/workflows/validate.yml/badge.svg)](https://github.com/marcomc/glinet-vpn-subscription-generator/actions/workflows/validate.yml)

This repository contains the source code and configuration that generate plain-text domain and IP routing subscriptions for the GL.iNet VPN client Subscription URL feature. Generated subscriptions are published separately in [glinet-vpn-subscription-lists](https://github.com/marcomc/glinet-vpn-subscription-lists).

Other OpenWrt VPN clients can use the published lists only when their policy importer accepts the same one-rule-per-line domain and CIDR syntax.

**Looking for a URL to paste into your router?** Start with the [ready-to-use subscriptions](https://github.com/marcomc/glinet-vpn-subscription-lists#quick-start). To request a provider, report a bad rule, or contribute a source, see [Contributing](CONTRIBUTING.md).

## Contents

- [Repositories](#repositories)
- [Generate and validate lists](#generate-and-validate-lists)
- [Development](#development)
- [Contributing](#contributing)
- [Compatibility and data limitations](#compatibility-and-data-limitations)
- [Source coverage](#source-coverage)
- [Publication](#publication)

## Repositories

| Repository | Contents |
| --- | --- |
| [glinet-vpn-subscription-generator](https://github.com/marcomc/glinet-vpn-subscription-generator) | Generator, source configuration, tests, router-format fixtures, and publication workflow |
| [glinet-vpn-subscription-lists](https://github.com/marcomc/glinet-vpn-subscription-lists) | Published domain/IP lists, coverage report, and subscription guide |

See the lists repository README for subscription URLs, setup steps, source attribution, and current coverage.

## Generate and validate lists

Clone both repositories as sibling directories, install the Python dependencies, then run the generator with the lists repository as its output root:

```sh
python -m pip install -r requirements.txt
python scripts/generate.py --output-root ../glinet-vpn-subscription-lists
python scripts/validate.py --root ../glinet-vpn-subscription-lists
python scripts/render_catalog.py --root ../glinet-vpn-subscription-lists
```

The output root is required so generated files are not written into the generator repository by mistake. Generation downloads configured upstream sources and writes the lists and `reports/coverage.json` only after all sources have been fetched and parsed. It removes obsolete generated list files, including the former plain-name and `-all` format aliases. The published README is rendered from [`templates/lists-README.md`](templates/lists-README.md).

## Development

The YAML configuration in [`config/services.yml`](config/services.yml) defines domain and attributable IP sources, provider/service mappings, and coverage notes. The generator resolves recursive includes, normalizes domains and CIDRs, removes duplicates, safely collapses overlapping ranges within a provider source, and sorts output deterministically.

Run the offline unit suite with:

```sh
python -m unittest discover -s tests -v
```

## Contributing

Open [a source request or list problem](https://github.com/marcomc/glinet-vpn-subscription-generator/issues/new/choose) in this repository. Pull requests should change the generator or its source configuration; the publication workflow updates the lists repository. The [contribution guide](CONTRIBUTING.md) explains the source and attribution requirements.

## Compatibility and data limitations

- Lists target the GL.iNet VPN client Subscription URL feature. GL.iNet documents domain and IPv4 CIDR rules; IPv6 parsing and routing vary by firmware and should be tested on the target router. IPv4-only links remain available.
- Other OpenWrt clients do not share one standard subscription parser. Confirm that the specific client accepts the list syntax before use.
- The generator filters domains known to be rejected by the GL.iNet parser and validates every generated list before publication.
- IP ranges are published only when source attribution is available. Shared cloud allocations and DNS-derived IP addresses are excluded; provider-level IP lists do not imply service-exclusive ownership.
- Domain policies can be bypassed by external or encrypted DNS, direct IP connections, or IPv6 paths not routed through the VPN. A successful import does not prove traffic is routed through the selected tunnel.

Source licensing and attribution for generated data are documented in [the lists repository](https://github.com/marcomc/glinet-vpn-subscription-lists/blob/main/DATA-LICENSES.md).

## Source coverage

The [source audit](docs/source-audit-1.1.0.md) records the usable official and
community sources for each configured provider. OpenAI domains include its
official network guide and two community feeds. OpenAI IP variants contain
only its published ChatGPT Voice server ranges for UDP 3478; its crawler and
integration IP files describe outbound requests to other systems. Microsoft's
official 365 feed supplements its domain rules and is scoped to Microsoft 365.
These lists cannot promise complete coverage of changing provider
infrastructure or third-party dependencies.

## Publication

The public lists repository is checked out over HTTPS without persisted
credentials. The `LISTS_DEPLOY_KEY` secret is used only when changed lists must
be pushed over SSH, with strict verification of GitHub's published host key.
Temporary key files are removed on success or failure. If SSH authentication fails,
the workflow reports failure without modifying the published lists.

The [publication workflow](.github/workflows/update-lists.yml) runs on changes to `main`, daily at 03:17 UTC, and on manual dispatch. It tests the generator, builds and validates the subscriptions, refreshes the catalog, then commits the result to the lists repository. A repository-specific deploy key grants this workflow write access only to the lists repository. Changes to source configuration or generator code are made here by maintainers. New upstream data updates only the lists repository; the workflow never commits to or updates the generator itself. The published Raw URLs stay stable.
