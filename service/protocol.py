from pydantic import BaseModel, Field
from pydantic import ValidationError
from typing import Union
from . import constants
import msgpack

class CategoryValidation(BaseModel):
    category: int = Field(ge=constants.CREATE, le=constants.COST)

class CreateValidation(CategoryValidation):
    decimals: int = Field(ge=constants.MIN_DECIMALS, le=constants.MAX_DECIMALS)
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    reissuable: bool

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class IssueValidation(CategoryValidation):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class TransferValidation(CategoryValidation):
    lock: Union[int, None] = Field(default=None, ge=1)
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class BurnValidation(CategoryValidation):
    value: int = Field(ge=1, le=constants.MAX_VALUE)

    ticker: str = Field(
        min_length=constants.MIN_TICKER_LENGTH,
        max_length=constants.MAX_TICKER_LENGTH
    )

class CostValidation(CategoryValidation):
    value: int = Field(ge=1, le=constants.MAX_VALUE)
    type: str = Field(regex=constants.TOKEN_TYPE_RE)
    action: str = Field(regex=constants.ACTIONS_RE)

class Protocol(object):
    @classmethod
    def encode(cls, payload):
        # Validate category
        try:
            CategoryValidation(**payload)
        except ValidationError:
            return None

        category = payload["category"]

        # Validate the rest of the payload
        try:
            if category == constants.CREATE:
                data = CreateValidation(**payload)
                payload = {
                    "r": data.reissuable,
                    "d": data.decimals,
                    "c": data.category,
                    "a": data.value,
                    "t": data.ticker
                }

            elif category == constants.ISSUE:
                data = IssueValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.value,
                    "t": data.ticker
                }

            elif category == constants.TRANSFER:
                data = TransferValidation(**payload)
                payload = {
                    "c": data.category,
                    "t": data.ticker,
                    "a": data.value,
                    "l": data.lock
                }

            elif category == constants.BURN:
                data = BurnValidation(**payload)
                payload = {
                    "c": data.category,
                    "t": data.ticker,
                    "a": data.value
                }

            elif category == constants.COST:
                data = CostValidation(**payload)
                payload = {
                    "c": data.category,
                    "a": data.action,
                    "v": data.value,
                    "t": data.type,
                }

            elif category == constants.BAN:
                data = CategoryValidation(**payload)
                payload = {
                    "c": data.category
                }

            elif category == constants.UNBAN:
                data = CategoryValidation(**payload)
                payload = {
                    "c": data.category
                }

            elif category == constants.FEE_ADDRESS:
                data = CategoryValidation(**payload)
                payload = {
                    "c": data.category
                }

        except ValidationError as e:
            print("Failed to encode payload:", e)
            return None

        return msgpack.packb(payload).hex()

    @classmethod
    def decode(cls, data):
        # Validate bytes
        try:
            data = bytes.fromhex(data)
            payload = msgpack.unpackb(data)
        except ValueError:
            return None

        if "c" not in payload:
            return None

        payload["category"] = payload.pop("c")

        # Validate category
        try:
            CategoryValidation(**payload)
        except ValidationError:
            return None

        category = payload["category"]

        # Validate the rest of the payload
        try:
            if category == constants.CREATE:
                payload["reissuable"] = payload.pop("r")
                payload["decimals"] = payload.pop("d")
                payload["ticker"] = payload.pop("t")
                payload["value"] = payload.pop("a")

                CreateValidation(**payload)

            elif category == constants.ISSUE:
                payload["ticker"] = payload.pop("t")
                payload["value"] = payload.pop("a")

                IssueValidation(**payload)

            elif category == constants.TRANSFER:
                payload["ticker"] = payload.pop("t")
                payload["value"] = payload.pop("a")
                payload["lock"] = payload.pop("l")

                TransferValidation(**payload)

            elif category == constants.BURN:
                payload["ticker"] = payload.pop("t")
                payload["value"] = payload.pop("a")

                BurnValidation(**payload)

            elif category == constants.COST:
                payload["action"] = payload.pop("a")
                payload["value"] = payload.pop("v")
                payload["type"] = payload.pop("t")

                CostValidation(**payload)

        except ValidationError as e:
            print("Failed to decode payload:", e)
            return None

        return payload
