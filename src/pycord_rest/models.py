# Copyright (c) Paillat-dev
# SPDX-License-Identifier: MIT

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class WebhookType(Enum):
    PING = 0
    Event = 1


class EventType(Enum):
    APPLICATION_AUTHORIZED = "APPLICATION_AUTHORIZED"
    ENTITLEMENT_CREATE = "ENTITLEMENT_CREATE"
    QUEST_USER_ENROLLMENT = "QUEST_USER_ENROLLMENT"


class EventBody(BaseModel):
    type: EventType
    timestamp: datetime
    data: dict[str, Any] | None = None  # pyright: ignore [reportExplicitAny]


class WebhookEventPayload(BaseModel):
    version: int
    application_id: int
    type: WebhookType
    event: EventBody | None = None
