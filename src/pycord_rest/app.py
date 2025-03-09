# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

import logging
from collections.abc import Callable, Coroutine
from functools import cached_property
from typing import Any, Never, override

import aiohttp
import discord
import uvicorn
from discord import Entitlement, Interaction, InteractionType
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from .models import EventType, WebhookEventPayload, WebhookType

logger = logging.getLogger("pycord.rest")


class ApplicationAuthorizedEvent:
    def __init__(self, user: discord.User, guild: discord.Guild | None, type: discord.IntegrationType) -> None:  # noqa: A002
        self.type: discord.IntegrationType = type
        self.user: discord.User = user
        self.guild: discord.Guild | None = guild

    @override
    def __repr__(self) -> str:
        return (
            f"<ApplicationAuthorizedEvent type={self.type} user={self.user}"
            + (f" guild={self.guild}" if self.guild else "")
            + ">"
        )


class PycordRestError(discord.DiscordException):
    pass


class InvalidCredentialsError(PycordRestError):
    pass


class App(discord.Bot):
    def __init__(self, *args: Any, **options: Any) -> None:  # pyright: ignore [reportExplicitAny]
        super().__init__(*args, **options)  # pyright: ignore [reportUnknownMemberType]
        self._app: FastAPI = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
        self.router: APIRouter = APIRouter()
        self._public_key: str | None = None

    @cached_property
    def _verify_key(self) -> VerifyKey:
        if self._public_key is None:
            raise InvalidCredentialsError("No public key provided")
        return VerifyKey(bytes.fromhex(self._public_key))

    async def _dispatch_view(self, component_type: int, custom_id: str, interaction: Interaction) -> None:
        # Code taken from ViewStore.dispatch
        self._connection._view_store._ViewStore__verify_integrity()  # noqa: SLF001  # pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportPrivateUsage]
        message_id: int | None = interaction.message and interaction.message.id
        key = (component_type, message_id, custom_id)
        value = self._connection._view_store._views.get(key) or self._connection._view_store._views.get(  # pyright: ignore [reportUnknownVariableType, reportUnknownMemberType, reportPrivateUsage]  # noqa: SLF001
            (component_type, None, custom_id)
        )
        if value is None:
            return

        view, item = value  # pyright: ignore [reportUnknownVariableType]
        item.refresh_state(interaction)

        # Code taken from View._dispatch_item
        if view._View__stopped.done():  # noqa: SLF001  # pyright: ignore [reportAttributeAccessIssue, reportUnknownMemberType]
            return

        if interaction.message:
            view.message = interaction.message

        await view._scheduled_task(item, interaction)  # noqa: SLF001  # pyright: ignore [reportPrivateUsage, reportUnknownMemberType]

    async def _verify_request(self, request: Request) -> None:
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
        body = (await request.body()).decode("utf-8")
        try:
            _ = self._verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        except BadSignatureError as e:
            raise HTTPException(status_code=401, detail="Invalid request signature") from e

    async def _process_interaction(self, request: Request) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
        # Code taken from ConnectionState.parse_interaction_create
        data = await request.json()
        interaction = Interaction(data=data, state=self._connection)
        match interaction.type:
            case InteractionType.component:
                custom_id: str = interaction.data["custom_id"]  # pyright: ignore [reportGeneralTypeIssues, reportOptionalSubscript, reportUnknownVariableType]
                component_type = interaction.data["component_type"]  # pyright: ignore [reportGeneralTypeIssues, reportOptionalSubscript, reportUnknownVariableType]
                await self._dispatch_view(component_type, custom_id, interaction)  # pyright: ignore [reportUnknownArgumentType]
            case InteractionType.modal_submit:
                user_id, custom_id = (  # pyright: ignore [reportUnknownVariableType]
                    interaction.user.id,  # pyright: ignore [reportOptionalMemberAccess]
                    interaction.data["custom_id"],  # pyright: ignore [reportGeneralTypeIssues, reportOptionalSubscript]
                )
                await self._connection._modal_store.dispatch(user_id, custom_id, interaction)  # pyright: ignore [reportUnknownArgumentType, reportPrivateUsage]  # noqa: SLF001
            case InteractionType.ping:
                return {"type": 1}
            case InteractionType.application_command | InteractionType.auto_complete:
                await self.process_application_commands(interaction)
        self.dispatch("interaction", interaction)
        return {"ok": True}

    @override
    async def on_interaction(self, *args: Never, **kwargs: Never) -> None:
        pass

    @override
    async def process_application_commands(  # noqa: PLR0912
        self, interaction: Interaction, auto_sync: bool | None = None
    ) -> None:
        # Code taken from super().process_application_commands
        if auto_sync is None:
            auto_sync = self._bot.auto_sync_commands  # pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]
        # TODO: find out why the isinstance check below doesn't stop the type errors below  # noqa: FIX002, TD002, TD003
        if interaction.type not in (
            InteractionType.application_command,
            InteractionType.auto_complete,
        ):
            return None

        command: discord.ApplicationCommand | None = None  # pyright: ignore [reportMissingTypeArgument]
        try:
            if interaction.data:
                command = self._application_commands[interaction.data["id"]]  # pyright: ignore [reportUnknownVariableType, reportUnknownMemberType, reportGeneralTypeIssues]
        except KeyError:
            for cmd in self.application_commands + self.pending_application_commands:  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
                if interaction.data:
                    guild_id = interaction.data.get("guild_id")
                    if guild_id:
                        guild_id = int(guild_id)
                    if cmd.name == interaction.data["name"] and (  # pyright: ignore [reportGeneralTypeIssues]
                        guild_id == cmd.guild_ids or (isinstance(cmd.guild_ids, list) and guild_id in cmd.guild_ids)
                    ):
                        command = cmd  # pyright: ignore [reportUnknownVariableType]
                        break
            else:
                if auto_sync and interaction.data:
                    guild_id = interaction.data.get("guild_id")
                    if guild_id is None:
                        await self.sync_commands()  # pyright: ignore [reportUnknownMemberType]
                    else:
                        await self.sync_commands(check_guilds=[guild_id])  # pyright: ignore [reportUnknownMemberType]
                return self._bot.dispatch("unknown_application_command", interaction)

        if interaction.type is InteractionType.auto_complete:
            self._bot.dispatch("application_command_auto_complete", interaction, command)
            await super().on_application_command_auto_complete(interaction, command)  # pyright: ignore [reportArgumentType, reportUnknownMemberType]
            return None

        ctx = await self.get_application_context(interaction)
        if command:
            ctx.command = command
        await self.invoke_application_command(ctx)
        return None

    @override
    async def on_application_command_auto_complete(self, *args: Never, **kwargs: Never) -> None:  # pyright: ignore [reportIncompatibleMethodOverride]
        pass

    def _process_interaction_factory(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, dict[str, Any]]]:  # pyright: ignore [reportExplicitAny]
        @self.router.post("/", dependencies=[Depends(self._verify_request)])
        async def process_interaction(request: Request) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
            return await self._process_interaction(request)

        return process_interaction

    async def _health(self) -> dict[str, str]:
        return {"status": "ok"}

    def _health_factory(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, dict[str, str]]]:  # pyright: ignore [reportExplicitAny]
        @self.router.get("/health")
        async def health(_: Request) -> dict[str, str]:
            return await self._health()

        return health

    async def _handle_webhook_event(self, data: dict[str, Any] | None, event_type: EventType) -> None:  # pyright: ignore [reportExplicitAny]
        if not data:
            raise HTTPException(status_code=400, detail="Missing event data")

        match event_type:
            case EventType.APPLICATION_AUTHORIZED:
                event = ApplicationAuthorizedEvent(
                    user=discord.User(state=self._connection, data=data["user"]),
                    guild=(discord.Guild(state=self._connection, data=data["guild"]) if data.get("guild") else None),
                    type=discord.IntegrationType.guild_install
                    if data.get("guild")
                    else discord.IntegrationType.user_install,
                )
                logger.debug("Dispatching application_authorized event")
                self.dispatch("application_authorized", event)
                if event.type == discord.IntegrationType.guild_install:
                    self.dispatch("guild_join", event.guild)
            case EventType.ENTITLEMENT_CREATE:
                entitlement = Entitlement(data=data, state=self._connection)  # pyright: ignore [reportArgumentType]
                logger.debug("Dispatching entitlement_create event")
                self.dispatch("entitlement_create", entitlement)
            case _:
                logger.warning(f"Unsupported webhook event type received: {event_type}")

    async def _webhook_event(self, payload: WebhookEventPayload) -> Response | dict[str, Any]:  # pyright: ignore [reportExplicitAny]
        match payload.type:
            case WebhookType.PING:
                return Response(status_code=204)
            case WebhookType.Event:
                if not payload.event:
                    raise HTTPException(status_code=400, detail="Missing event data")
                await self._handle_webhook_event(payload.event.data, payload.event.type)

        return {"ok": True}

    def _webhook_event_factory(
        self,
    ) -> Callable[[WebhookEventPayload], Coroutine[Any, Any, Response | dict[str, Any]]]:  # pyright: ignore [reportExplicitAny]
        @self.router.post("/webhook", dependencies=[Depends(self._verify_request)], response_model=None)
        async def webhook_event(payload: WebhookEventPayload) -> Response | dict[str, Any]:  # pyright: ignore [reportExplicitAny]
            return await self._webhook_event(payload)

        return webhook_event

    @override
    async def connect(  # pyright: ignore [reportIncompatibleMethodOverride]
        self,
        token: str,
        public_key: str,
        uvicorn_options: dict[str, Any] | None = None,  # pyright: ignore [reportExplicitAny]
        health: bool = True,
    ) -> None:
        self._public_key = public_key
        _ = self._process_interaction_factory()
        _ = self._webhook_event_factory()
        if health:
            _ = self._health_factory()
        self._app.include_router(self.router)
        uvicorn_options = uvicorn_options or {}
        uvicorn_options["log_level"] = uvicorn_options.get("log_level", logging.root.level)
        config = uvicorn.Config(self._app, **uvicorn_options)
        server = uvicorn.Server(config)
        try:
            self.dispatch("connect")
            await server.serve()
        except (TimeoutError, OSError, HTTPException, aiohttp.ClientError):
            logger.exception("An error occurred while serving the app.")
            self.dispatch("disconnect")

    @override
    async def close(self) -> None:
        pass

    @override
    async def start(  # pyright: ignore [reportIncompatibleMethodOverride]
        self,
        token: str,
        public_key: str,
        uvicorn_options: dict[str, Any] | None = None,  # pyright: ignore [reportExplicitAny]
        health: bool = True,
    ) -> None:
        if not token:
            raise InvalidCredentialsError("No token provided")
        if not public_key:
            raise InvalidCredentialsError("No public key provided")
        await self.login(token)
        await self.connect(
            token=token,
            public_key=public_key,
            uvicorn_options=uvicorn_options,
            health=health,
        )

    @override
    def run(
        self,
        *args: Any,  # pyright: ignore [reportExplicitAny]
        token: str,
        public_key: str,
        uvicorn_options: dict[str, Any] | None = None,  # pyright: ignore [reportExplicitAny]
        health: bool = True,
        **kwargs: Any,  # pyright: ignore [reportExplicitAny]
    ) -> None:
        super().run(
            *args,
            token=token,
            public_key=public_key,
            uvicorn_options=uvicorn_options,
            health=health,
            **kwargs,
        )
