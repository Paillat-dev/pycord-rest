# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

"""Basic Discord bot example using Pycord REST.

This is a minimal example showing how to create slash commands.
"""

import os
from pydoc import describe

import discord
from dotenv import load_dotenv

from pycord_rest import App

# Load environment variables from .env file
load_dotenv()

app = App()


# Simple ping command
@app.slash_command(name="ping", description="Responds with pong!")
async def ping(ctx: discord.ApplicationContext) -> None:
    await ctx.respond("Pong!")


# Command with parameters
@app.slash_command(name="greet", description="Greets a user")
@discord.option("name", input_type=str, description="The name of the user to greet", required=False)
async def greet(ctx: discord.ApplicationContext, name: str | None = None) -> None:
    if name:
        await ctx.respond(f"Hello, {name}!")
    else:
        await ctx.respond(f"Hello, {ctx.author.display_name}!")


# Run the app
if __name__ == "__main__":
    app.run(
        token=os.environ["DISCORD_TOKEN"],
        public_key=os.environ["DISCORD_PUBLIC_KEY"],
        uvicorn_options={
            "host": "0.0.0.0",  # noqa: S104
            "port": 8000,
            "log_level": "info",
        },
    )
