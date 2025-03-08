# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT
from discord import *  # noqa: F403, I001  # pyright: ignore [reportWildcardImportFromLibrary]
from .app import App

Bot = App

__all__ = ["App", "Bot"]
