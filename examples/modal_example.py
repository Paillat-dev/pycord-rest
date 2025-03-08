# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

"""Example showing how to work with modals in Pycord REST."""

import asyncio
import os
from typing import Any

import discord
from dotenv import load_dotenv

from pycord_rest import App

# Load environment variables from .env file
load_dotenv()

app = App()


class MyModal(discord.ui.Modal):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Name", placeholder="Enter your name", style=discord.InputTextStyle.short, custom_id="name_input"
            ),
            discord.ui.InputText(
                label="Feedback",
                placeholder="Please provide your feedback here...",
                style=discord.InputTextStyle.paragraph,
                custom_id="feedback_input",
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        name = self.children[0].value

        await interaction.respond(
            f"Thank you for your feedback, {name}! Your submission has been received.", ephemeral=True
        )


# Command that shows a form modal
@app.slash_command(name="feedback", description="Submit feedback through a form")
async def feedback(ctx: discord.ApplicationContext) -> None:
    # Create a modal
    modal = MyModal(title="Feedback Form")
    await ctx.send_modal(modal)
    await ctx.respond("Opening feedback form...", ephemeral=True)


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
