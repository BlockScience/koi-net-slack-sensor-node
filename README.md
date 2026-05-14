# koi-net-slack-sensor-node

A [KOI-net](https://github.com/DynamicalSystemsGroup/koi-net) sensor node that ingests Slack workspace events into the KOI-net protocol as typed Resource Identifiers (RIDs).

The node connects to a Slack workspace via the Slack bot/app APIs, normalises messages into `orn:slack.message:` RIDs, and broadcasts them as events to the KOI-net network. It also maintains state for `orn:slack.workspace`, `orn:slack.channel`, and `orn:slack.user` RIDs so downstream nodes can resolve mentions and references.

## What this node does

| Role | Detail |
|---|---|
| **Node type** | Full node (inherits from `koi_net.core.FullNode`) |
| **Events emitted** | `SlackMessage` |
| **State maintained** | `SlackMessage`, `SlackUser`, `SlackChannel`, `SlackWorkspace` |
| **Slack APIs used** | Events API (live), `conversations.history` (backfill), `users.info`, `conversations.info` |
| **Slack SDK** | `slack_bolt` (async) + `slack_sdk` |

The node runs three concurrent components, declared as class attributes on `SlackSensorNode` in `src/koi_net_slack_sensor_node/core.py`:

- **`SlackEventHandler`** — receives live Slack events, generates RIDs, and pushes them onto the KObj queue for KOI-net broadcast.
- **`Backfiller`** (`ThreadedComponent`) — backfills historical messages from each allowed channel, resuming from the timestamp recorded by `LastProcessedTSHandler`. Runs in a separate thread so live events keep flowing while backfill catches up.
- **`LastProcessedTSHandler`** — tracks the most recent message timestamp processed, so restarts pick up where the previous run left off rather than redoing full backfill.

## Configuration

Configuration is split between environment variables (Slack credentials) and `config.yaml` (workspace-specific settings).

### Required environment variables (read by `SlackEnvConfig` in `config.py`)

```
SLACK_BOT_TOKEN       # xoxb-... — bot user OAuth token
SLACK_SIGNING_SECRET  # for verifying request signatures from Slack
SLACK_APP_TOKEN       # xapp-... — Socket Mode connection token
```

### `config.yaml` keys

| Key | Type | Default | Description |
|---|---|---|---|
| `koi_net.node_name` | `str` | `"slack-sensor"` | KOI-net node identifier |
| `slack.allowed_channels` | `list[str]` | `[]` | Channel IDs the node listens to; empty list = listen to all channels the bot can see |
| `slack.last_processed_ts` | `str` | `"0"` | Backfill watermark; `"0"` means backfill full history |

Additional `koi_net.*` fields follow the [koi-net node config schema](https://github.com/DynamicalSystemsGroup/koi-net).

## Install and run

```bash
git clone https://github.com/DynamicalSystemsGroup/koi-net-slack-sensor-node.git
cd koi-net-slack-sensor-node
uv sync                                              # or: pip install -e .
uv run python -m koi_net_slack_sensor_node           # or: python -m koi_net_slack_sensor_node
```

The node reads `config.yaml` from the working directory at startup.

## Deployment as a systemd service

A `koi-net-slack-sensor-node.service` unit file is included for systemd deployments. After cloning and setting up the virtualenv, install the unit and enable:

```bash
sudo cp koi-net-slack-sensor-node.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now koi-net-slack-sensor-node
```

The unit assumes a working directory of `/home/dev/koi-net-slack-sensor-node` with a venv at `.venv/`. Edit the unit file paths if your deployment layout differs. `Restart=always` — the node restarts automatically on failure.

## Source layout

```
src/koi_net_slack_sensor_node/
├── __main__.py                    # entrypoint: instantiates SlackSensorNode and calls .run()
├── core.py                        # SlackSensorNode (FullNode subclass)
├── config.py                      # SlackEnvConfig, SlackConfig, SlackSensorNodeConfig
├── server.py                      # SlackSensorNodeServer — KOI-net HTTP server
├── slack_event_handler.py         # live Slack-events processor
├── backfiller.py                  # historical-message backfiller (ThreadedComponent)
├── last_processed_ts_handler.py   # watermark tracker
└── dereference.py                 # RID → content resolution
```

## Related repos

- [`koi-net`](https://github.com/DynamicalSystemsGroup/koi-net) — the protocol and full-node framework this builds on
- [`rid-lib`](https://github.com/DynamicalSystemsGroup/rid-lib) — defines the RID types this node emits (`SlackMessage`, `SlackChannel`, etc.)
- [`koi-net-coordinator-node`](https://github.com/DynamicalSystemsGroup/koi-net-coordinator-node) — typical coordinator the sensor node registers with on startup

## License

MIT. See [LICENSE](LICENSE).
