# modmail-custom

[![Discord](https://discord.com/api/guilds/576016832956334080/widget.png)](https://discord.gg/wjWJwJB)
[![License](https://img.shields.io/github/license/chamburr/modmail.svg)](LICENSE)

My own personal fork of [chamburr/modmail](https://github.com/chamburr/modmail), the open-source bot behind [modmail.xyz](https://modmail.xyz). All the real credit goes to chamburr and everyone who built it. Want the actual bot? Grab it from that repo instead, or join their [Discord server](https://discord.gg/wjWJwJB) for support and updates.

## What this actually is

I help out as an admin for the official ModMail bot, but this repo has nothing to do with that. It's just me messing around with the code on my own time to learn and try stuff. Not official, not connected to the ModMail team, not endorsed by them. Just my own side project built on top of their code.

## What I added

Everything here is extra stuff on top. The core bot still works exactly like the original (tickets, replies, snippets, all of it).

| Feature | What it does |
|---|---|
| Ticket tags | Label tickets like `bug`, `billing`, or `abuse` to keep things sorted |
| Auto-close | Tickets that sit quiet for a while close on their own |
| Webhook alerts | Sends a Discord webhook message when a ticket opens, gets tagged, or auto-closes |
| Ops monitoring *(still building this)* | The bot tracks its own speed and errors, and a separate watchdog service keeps an eye on the database, queue, and containers, flagging anything that looks off |

## Running it

Same as upstream, just trimmed to 5 containers for local testing, no dashboard or API needed:

- `bot`, the actual Discord bot, Python
- `dispatch`, handles the Discord connection (using `tigefa/twilight-dispatch` instead of the official image since I'm on Apple Silicon and the official one has no arm64 build. Unofficial, testing only)
- `postgres`, `redis`, `rabbitmq`

```
cp .env.example .env   # fill in your bot token etc
docker compose -f docker/docker-compose.yml up -d
```

## Credit

This is chamburr's code with my stuff added on top. Check [`LICENSE`](./LICENSE) for the terms, and the original repo for the most current version of those. Big thanks to chamburr and everyone in the ModMail community for the project this is built on.