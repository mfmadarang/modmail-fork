# modmail-custom

[![Discord](https://discord.com/api/guilds/576016832956334080/widget.png)](https://discord.gg/wjWJwJB)
[![License](https://img.shields.io/github/license/chamburr/modmail.svg)](LICENSE)

A personal fork of [chamburr/modmail](https://github.com/chamburr/modmail), the open-source Discord bot behind [modmail.xyz](https://modmail.xyz), extended with additional features for ticket management and operational monitoring.

## Disclaimer

This project is unofficial and is not affiliated with, endorsed by, or representative of the ModMail team. It is an independent, personal effort built on top of their open-source code, maintained separately from any official capacity. For the original bot, visit the [upstream repository](https://github.com/chamburr/modmail) or [modmail.xyz](https://modmail.xyz). For support with the official bot, join their [Discord server](https://discord.gg/wjWJwJB).

## Overview

The core bot functionality (ticket creation, replies, snippets, and configuration) is unchanged from upstream. This fork adds the following on top:

| Feature | Description |
|---|---|
| Ticket tagging | Tickets can be labeled (e.g. `bug`, `billing`, `abuse`) for easier categorization and filtering |
| Auto-close on inactivity | Tickets with no activity for a configurable period are closed automatically |
| Webhook alerts | Outbound Discord webhook notifications on new ticket, tag, and auto-close events |
| Operational monitoring | A self-reporting metrics cog (bot latency, error rate) paired with a standalone watchdog service that tracks container health, RabbitMQ queue depth, and database connections, with threshold-based incident detection |

## Architecture

This fork runs a reduced five-container stack for local development, omitting the web dashboard and API service present in the upstream project:

| Service | Role |
|---|---|
| `bot` | Core Discord bot logic (Python) |
| `dispatch` | Gateway connection service. Uses [`tigefa/twilight-dispatch`](https://hub.docker.com/r/tigefa/twilight-dispatch) in place of the official image for Apple Silicon compatibility. Unofficial, intended for local development only |
| `postgres` | Primary datastore |
| `redis` | Caching and pub/sub |
| `rabbitmq` | Message queue between the bot and dispatch service |
| `watchdog` | Custom addition. Polls infrastructure metrics and logs threshold-based incidents |

## Getting started

```bash
cp .env.example .env
# populate the bot token and remaining configuration values

cd docker
docker compose up -d
```

## Credit and license

This project is derived from chamburr/modmail and inherits its license. See [`LICENSE`](./LICENSE) for full terms, and refer to the upstream repository for the current, authoritative version. All credit for the original bot belongs to chamburr and its contributors.