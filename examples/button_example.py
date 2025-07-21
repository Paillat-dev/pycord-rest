# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

"""Example demonstrating how to use buttons with Pycord REST."""

import os
from typing import Any

import discord
from dotenv import load_dotenv

from pycord_rest import App

# Load environment variables from .env file
load_dotenv()

app = App()


class MyView(discord.ui.View):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(
            discord.ui.Button(  # pyright: ignore[reportUnknownArgumentType]
                style=discord.ButtonStyle.link, label="GitHub", url="https://github.com/Paillat-dev/pycord-rest"
            )
        )

    @discord.ui.button(label="Green", style=discord.ButtonStyle.success)
    async def green_button(self, button: "discord.ui.Button[MyView]", interaction: discord.Interaction) -> None:
        await interaction.respond("You clicked the green button!", ephemeral=True)

    @discord.ui.button(label="Red", style=discord.ButtonStyle.danger)
    async def red_button(self, button: "discord.ui.Button[MyView]", interaction: discord.Interaction) -> None:
        await interaction.respond("You clicked the red button!", ephemeral=True)


# Create a slash command that shows buttons
@app.slash_command(name="buttons", description="Shows interactive buttons")
async def buttons(ctx: discord.ApplicationContext) -> None:
    # Create a view with buttons
    view = MyView()
    await ctx.respond("Choose a button:", view=view)


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
