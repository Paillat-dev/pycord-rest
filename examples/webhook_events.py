# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

"""Basic Discord bot example using Pycord REST.

This is a minimal example showing how to create slash commands.
"""

import logging
import os

from dotenv import load_dotenv

from pycord_rest import App, ApplicationAuthorizedEvent

# Load environment variables from .env file
load_dotenv()


# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = App()


# Register the event handler
@app.listen("on_application_authorized")
async def on_application_authorized(event: ApplicationAuthorizedEvent) -> None:
    if not event.guild:
        print(f"User {event.user.display_name} ({event.user.id}) installed the application.")

    else:
        print(
            f"Bot {event.user.display_name} ({event.user.id}) installed the application"  # noqa: ISC003
            + f" to guild {event.guild.name} ({event.guild.id})."
        )


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
