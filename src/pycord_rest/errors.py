# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

import discord


class PycordRestError(discord.DiscordException):
    pass


class InvalidCredentialsError(PycordRestError):
    pass
