# Pycord REST

A lightweight wrapper for Discord's HTTP interactions using py-cord and FastAPI. This library enables you to build Discord bots that work exclusively through Discord's HTTP interactions, without requiring a WebSocket gateway connection.

## About

Pycord REST allows you to build Discord bots that respond to interactions via HTTP endpoints as described in [Discord's interaction documentation](https://discord.com/developers/docs/interactions/receiving-and-responding) and [interaction overview](https://discord.com/developers/docs/interactions/overview#preparing-for-interactions).

This project is built on:
- **FastAPI** - For handling the HTTP server
- **py-cord** - Leveraging Discord command builders and interaction handling
- **uvicorn** - ASGI server implementation

## Installation

```bash
pip install pycord-reactive-bot
```

## Quick Start

```python
from pycord_rest import App
import discord

app = App(intents=discord.Intents.default())

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

For more examples, check out the [examples directory](/examples) which includes:
- Basic slash command setup
- Button interactions
- Modal forms
- Production deployment configurations

## How It Works

Under the hood, Pycord REST creates an HTTP server using FastAPI and Uvicorn that:

1. Listens for incoming Discord interaction requests on your specified endpoint
2. Verifies the request signature using your application's public key
3. Routes the interaction to the appropriate command handler
4. Returns the response back to Discord

Unlike traditional Discord bots that maintain a persistent WebSocket connection to Discord's gateway, HTTP-based bots:
- Only wake up when an interaction is received
- Don't receive real-time events from Discord

## Usage

### Setting up your bot on Discord

1. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable the "Interactions Endpoint URL" for your application 
3. Set the URL to your public endpoint where your bot will receive interactions
4. Copy your public key from the Developer Portal to verify signatures

### Features

- Slash Commands
- UI Components (buttons, select menus)
- Modal interactions
- Autocomplete for commands

### Similarities to py-cord

Syntax is equivalent to py-cord, as it is what is being used under the hood, making it easy to adapt existing bots:

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

## Limitations

This library works differently than traditional bots because it does not use Discord's WebSocket gateway:

- **No Cache**: Since there's no gateway connection, there's no cache of guilds, channels, users, etc.
- **Limited API Methods**: Many standard py-cord methods that rely on cache won't work properly:
  - `app.get_channel()`, `app.get_guild()`, `app.get_user()`, etc.
  - Presence updates
  - Voice support
  - Member tracking
- **Event-Based Functions**: Only interaction-based events work; message events, etc. don't work

Remember that this is an HTTP-only bot that responds exclusively to interactions triggered by users.

## Configuration Options

```python
app.run(
    token="YOUR_BOT_TOKEN",
    public_key="YOUR_PUBLIC_KEY",
    uvicorn_options={
        "host": "0.0.0.0",  # Listen on all network interfaces
        "port": 8000,        # Port to listen on
        "log_level": "info", # Uvicorn logging level
        # Any valid uvicorn server options
    },
    health=True  # Enable /health endpoint
)
```

### Server Configuration

For Discord to reach your bot, you need a publicly accessible HTTPS URL. Options include:
- Using a VPS with a domain and SSL certificate
- Deploying to a cloud service like Heroku, Railway, or Fly.io

### Health Check

By default, Pycord REST includes a `/health` endpoint that returns a 200 status code. This endpoint is useful for monitoring services like UptimeRobot or health checks.

## Advanced Usage

### Adding Custom FastAPI Routes

```python
from fastapi import Request

@app.router.get("/custom")
async def custom_endpoint(request: Request):
    return {"message": "This is a custom endpoint"}
```

## Development Workflow

For faster development and testing, you can use tunneling tools to expose your local development server:

- **ngrok** - Creates a secure tunnel to your localhost
  ```bash
  # Install ngrok
  npm install -g ngrok
  
  # Expose your local server
  ngrok http 8000
  ```

- **Cloudflare Tunnel** - Provides a secure connection to your local server
- **localtunnel** - Simple tunnel service for exposing local endpoints

These tools provide temporary URLs that you can use in the Discord Developer Portal during development, allowing you to test changes quickly without deploying to production.

## Contributing

Contributions are welcome! This project is in early development, so there might be bugs or unexpected behaviors.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `ruff check` and `ruff format`
5. Submit a pull request

### Development Tools

- **Ruff**: For linting and formatting
- **HashiCorp Copywrite**: For managing license headers
- **basedpyright**: For type checking

## Disclaimer

This is an early-stage project and may have unexpected behaviors or bugs. Please report any issues you encounter.

## License

MIT License - Copyright (c) 2025 Paillat-dev

---

Made with ❤️ by Paillat-dev
