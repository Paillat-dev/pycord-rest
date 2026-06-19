# SPDX-License-Identifier: MIT
# Copyright: 2024-2026 Paillat-dev

import discord


class PycordRestError(discord.DiscordException):
    pass


class InvalidCredentialsError(PycordRestError):
    pass
