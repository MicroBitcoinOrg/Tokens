from ..models import Balance, Transfer
from ..models import Token, Address
from ..utils import log_message
from .. import constants
from .. import utils

async def process_transfer(decoded, inputs, outputs, block, txid):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    token = await Token.filter(ticker=decoded["ticker"]).first()
    value = utils.amount(decoded["value"], token.decimals)

    send_address = await Address.filter(label=send_address_label).first()
    send_balance = await Balance.filter(
        address=send_address, token=token
    ).first()

    if not (receive_address := await Address.filter(
        label=receive_address_label
    ).first()):
        receive_address = await Address.create(**{
            "label": receive_address_label
        })

    if not (receive_balance := await Balance.filter(
        address=receive_address, token=token
    ).first()):
        receive_balance = await Balance.create(**{
            "address": receive_address,
            "token": token
        })

    transfer = await Transfer.create(**{
        "category": constants.CATEGORY_TRANSFER,
        "receiver": receive_address,
        "created": block.created,
        "send": send_address,
        "value": value,
        "token": token,
        "block": block,
        "txid": txid
    })

    send_balance.value -= transfer.value
    send_balance.sent += transfer.value

    receive_balance.received += transfer.value
    receive_balance.value += transfer.value

    await receive_balance.save()
    await send_balance.save()

    log_message(f"Transfered {value} {token.ticker}")
