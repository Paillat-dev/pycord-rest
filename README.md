# Pycord REST

A lightweight wrapper for Discord's HTTP interactions and webhook events using py-cord
and FastAPI.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
  - [How It Works](#how-it-works)
  - [Discord Application Setup](#discord-application-setup)
- [Features](#features)
  - [Interaction Handling](#interaction-handling)
  - [Webhook Events](#webhook-events)
- [Usage Examples](#usage-examples)
  - [Basic Commands](#basic-commands)
  - [Event Handling](#event-handling)
  - [Custom Routes](#custom-routes)
- [Configuration](#configuration)
- [Limitations](#limitations)
- [Development](#development)
  - [Local Testing](#local-testing)
  - [Contributing](#contributing)
- [License](#license)

## Overview

Pycord REST enables you to build Discord applications that respond to:

- **Interactions** via HTTP endpoints (slash commands, components, modals)
- **Webhook events** such as application authorization and entitlements

Built on:

- **FastAPI** - For handling HTTP requests
- **py-cord** - For Discord command builders and interaction handling
- **uvicorn** - ASGI server implementation

## Installation

```bash
pip install pycord-rest-bot --prerelease=allow
```

<!-- prettier-ignore -->
> [!NOTE]
> The package is currently in pre-release.

## Quick Start

```python
from pycord_rest import App
import discord

app = App()

@app.slash_command(name="ping", description="Responds with pong!")
async def ping(ctx):
    await ctx.respond("Pong!")

if __name__ == "__main__":
    app.run(
        token="YOUR_BOT_TOKEN",
        public_key="YOUR_PUBLIC_KEY",  # From Discord Developer Portal
        uvicorn_options={
            "host": "0.0.0.0",
            "port": 8000
        }
    )
```

## Core Concepts

### How It Works

Pycord REST creates an HTTP server that:

1. Listens for Discord interaction requests and webhook events
2. Verifies request signatures using your application's public key
3. Routes events to appropriate handlers
4. Returns responses back to Discord

Unlike traditional WebSocket-based Discord bots, HTTP-based applications:

- Only wake up when receiving interactions or webhook events
- Don't maintain a persistent connection to Discord's gateway
- Don't receive most real-time Discord events

### Discord Application Setup

1. Create an application on the
   [Discord Developer Portal](https://discord.com/developers/applications)
2. Copy your public key to verify signatures
3. Run your FastAPI server
4. Configure the endpoints:

- **Interactions Endpoint URL** - For slash commands and component interactions
  (`https://example.com`)
- **Webhook URL** - For receiving application events (e.g.,
  `https://example.com/webhook`)

<!-- prettier-ignore -->
> [!IMPORTANT]
> Don't forget to run your FastAPI server **before** setting up the application on Discord, or else Discord won't be able to verify the endpoints.

## Features

### Interaction Handling

Respond to Discord interactions such as:

- **Slash Commands** - Create and respond to application commands
- **UI Components** - Buttons, select menus, and other interactive elements
- **Modal Forms** - Pop-up forms for gathering user input
- **Autocomplete** - Dynamic option suggestions as users type

### Webhook Events

Handle Discord webhook events such as:

- **Application authorization** - When your app is added to a guild or authorized by a
  user
- **Entitlement creation** - When a user subscribes to your app's premium features

## Usage Examples

<!-- prettier-ignore -->
> [!TIP]
> For complete examples, check out the [examples directory](/examples).

### Basic Commands

Commands use the familiar py-cord syntax:

```python
@app.slash_command(name="hello", description="Say hello")
async def hello(ctx, user: discord.Member = None):
    user = user or ctx.author
    await ctx.respond(f"Hello {user.mention}!")

@app.slash_command()
async def button(ctx):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Click me!", custom_id="my_button"))
    await ctx.respond("Press the button!", view=view)
```

### Event Handling

The possible events are:

- `on_application_authorized` - When your app is added to a guild or authorized by a
  user
- `on_entitlement_create` - When a user subscribes to your app's premium features

<!-- prettier-ignore -->
> [!NOTE]
> For application installation events, use `on_application_authorized` instead of `on_guild_join`.

```python
@app.listen("on_application_authorized")
async def on_application_authorized(event: ApplicationAuthorizedEvent):
    # Triggers when app is added to a guild OR when a user authorizes your app
    print(f"Authorization received: Guild={event.guild}, User={event.user}")
```

### Custom Routes

Add your own FastAPI routes:

```python
from fastapi import Request

@app.router.get("/custom")
async def custom_endpoint(request: Request):
    return {"message": "This is a custom endpoint"}
```

## Configuration

```python
app.run(
    token="YOUR_BOT_TOKEN",
    public_key="YOUR_PUBLIC_KEY",
    uvicorn_options={
        "host": "0.0.0.0",  # Listen on all network interfaces
        "port": 8000,        # Port to listen on
        "log_level": "info", # Uvicorn logging level
    },
    health=True  # Enable /health endpoint for monitoring
)
```

### Integration Options

1. **Stand-alone HTTP Interaction Bot** - Commands and components only
2. **Webhook Event Handler Only** - Process application events alongside a separate
   gateway bot
3. **Full HTTP Application** - Handle both interactions and webhook events

## Limitations

Since Pycord REST doesn't use Discord's WebSocket gateway:

- **No Cache** - No local storage of guilds, channels, or users
- **Limited API Methods** - Functions that rely on cache won't work:
  - `app.get_channel()`, `app.get_guild()`, `app.get_user()`
  - Presence updates
  - Voice support
  - Member tracking
- **Limited Events** - Only interaction-based and webhook events work

## Development

### Local Testing

Use tunneling tools to expose your local development server:

- **ngrok**:

  ```bash
  # Install ngrok
  npm install -g ngrok

  # Expose your local server
  ngrok http 8000
  ```

- **Cloudflare Tunnel** or **localtunnel** - Alternative tunneling options

These tools provide temporary URLs for testing without deploying to production.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linter, formatter and type checker: `ruff check .`,`ruff format .`,
   `basedpyright .`
5. Submit a pull request

**Development Tools**:

- **Ruff**: For linting and formatting
- **HashiCorp Copywrite**: For managing license headers
- **basedpyright**: For type checking

<!-- prettier-ignore -->
> [!NOTE]
> This is an early-stage project and may have unexpected behaviors or bugs. Please report any issues you encounter.

## License

MIT License - Copyright (c) 2025 Paillat-dev

---

Made with ❤ by Paillat-dev
