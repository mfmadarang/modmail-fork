# modmail-custom

[![Discord](https://discord.com/api/guilds/576016832956334080/widget.png)](https://discord.gg/wjWJwJB)
[![License](https://img.shields.io/github/license/chamburr/modmail.svg)](LICENSE)

This is my personal fork of [chamburr/modmail](https://github.com/chamburr/modmail), the open-source bot behind [modmail.xyz](https://modmail.xyz).

## Disclaimer

Just to be clear, this isn't affiliated with or endorsed by the actual ModMail team in any way. It's my own side project, not an official build. If you want the real thing, go grab it from the [upstream repo](https://github.com/chamburr/modmail) or check out [modmail.xyz](https://modmail.xyz). Our [Discord server](https://discord.gg/wjWJwJB) is the place for support on the actual bot.

## What I added

The base bot works exactly like upstream (tickets, replies, snippets, all that). On top of it I added:

| Feature | What it does |
|---|---|
| Ticket tagging | Label tickets (`bug`, `billing`, `abuse`, etc.) so they're easier to sort through |
| Auto-close | Tickets that go quiet for a while close themselves automatically |
| Webhook alerts | Sends a Discord webhook message whenever a ticket gets created, tagged, or auto-closed |
| Ops monitoring | A watchdog service that keeps an eye on container health, queue depth, DB connections, and flags anything that looks off. Feeds a little dashboard so I can actually see what's going on |

## How it's set up

I trimmed this down to five containers for local dev, dropped the official web dashboard and API since I didn't need them:

| Service | What it's for |
|---|---|
| `bot` | The actual bot logic (Python) |
| `dispatch` | Handles the gateway connection. Running [`tigefa/twilight-dispatch`](https://hub.docker.com/r/tigefa/twilight-dispatch) instead of the official image since I'm on Apple Silicon and the official one doesn't have an arm64 build. Community image, local dev only |
| `postgres` | Database |
| `redis` | Caching |
| `rabbitmq` | Queue between the bot and dispatch |
| `watchdog` | Mine, polls stats and logs stuff when something looks broken |
| `ops-api` | Mine, small FastAPI service that serves the watchdog's data to the dashboard |

## Dashboard

npm install
Threw together a React dashboard that polls `ops-api` every 30s and shows live stats per container. Doesn't run in Docker, just run it separately:

```bash
cd dashboard
npm run dev
```

It points at `http://localhost:8000` for the API by default, check `dashboard/.env` if you need to change that.

## Running it

```bash
cp .env.example .env
# fill in your bot token and the rest

cd docker
docker compose up -d
```

## Credit

All the real work here is chamburr's, I just built some stuff on top of it. License terms are in [`LICENSE`](./LICENSE), and the upstream repo is for anything core to the bot itself.