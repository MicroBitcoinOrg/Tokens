from fastapi import APIRouter
from ..chain import get_chain
from .args import BuildArgs
from ..errors import Abort
from .. import utils
import config


router = APIRouter(tags=["Construct"])

# used_utxos = []


@router.post("/construct", summary="Build token layer transaction")
async def construct(args: BuildArgs):
    validate = await utils.make_request("validateaddress", [args.send_address])

    if "error" in validate:
        raise Abort("construct", "bad-address")

    if not validate["isvalid"]:
        raise Abort("construct", "bad-address")

    if args.receive_address:
        validate = await utils.make_request(
            "validateaddress", [args.receive_address]
        )

        if "error" in validate:
            raise Abort("construct", "bad-address")

        if not validate["isvalid"]:
            raise Abort("construct", "bad-address")

    utxo_list = await utils.make_request(
        "getaddressutxos", [{"addresses": [args.send_address]}]
    )

    if "error" in utxo_list:
        raise Abort("construct", "bad-address")

    required_amount = args.fee

    if args.receive_address:
        required_amount += args.marker

    input_amount = 0
    outputs = {}
    inputs = []

    print(utxo_list)

    for utxo in utxo_list:
        # utxo_check = (utxo["outputIndex"], utxo["txid"])

        # if utxo_check in used_utxos:
        #     print(f"Skipping {utxo_check}")
        #     continue

        inputs.append({"vout": utxo["outputIndex"], "txid": utxo["txid"]})

        # used_utxos.append(utxo_check)

        input_amount += utxo["satoshis"]

        if input_amount >= required_amount:
            break

    change = input_amount - required_amount

    chain = get_chain(config.chain)

    if change > 0:
        outputs[args.send_address] = utils.amount(change, chain["decimals"])

    outputs["data"] = args.payload

    if args.receive_address:
        outputs[args.receive_address] = utils.amount(
            args.marker, chain["decimals"]
        )

    print(len(inputs))

    raw_tx = await utils.make_request("createrawtransaction", [inputs, outputs])

    if "error" in raw_tx:
        print(raw_tx["error"])
        raise Abort("construct", "failed")

    return {"data": raw_tx}


# @router.post("/construct/multi", summary="Build token layer transaction")
# async def construct_multi(args: list[BuildArgs]):
#     result = {}

#     used_utxos = []

#     for index, entry in enumerate(args):
#         validate = await utils.make_request(
#             "validateaddress", [entry.send_address]
#         )

#         if "error" in validate:
#             result[index] = None
#             continue

#         if not validate["isvalid"]:
#             result[index] = None
#             continue

#         if entry.receive_address:
#             validate = await utils.make_request(
#                 "validateaddress", [entry.receive_address]
#             )

#             if "error" in validate:
#                 result[index] = None
#                 continue

#             if not validate["isvalid"]:
#                 result[index] = None
#                 continue

#         utxo_list = await utils.make_request(
#             "getaddressutxos", [{"addresses": [entry.send_address]}]
#         )

#         if "error" in utxo_list:
#             result[index] = None
#             continue

#         required_amount = entry.fee

#         if entry.receive_address:
#             required_amount += entry.marker

#         input_amount = 0
#         outputs = {}
#         inputs = []

#         has_enough_utxo = False

#         for utxo in utxo_list:
#             utxo_check = (utxo["outputIndex"], utxo["txid"])

#             if utxo_check in used_utxos:
#                 continue

#             inputs.append({"vout": utxo["outputIndex"], "txid": utxo["txid"]})

#             used_utxos.append(utxo_check)

#             input_amount += utxo["satoshis"]

#             if input_amount >= required_amount:
#                 has_enough_utxo = True
#                 break

#         if not has_enough_utxo:
#             print("FUCK")
#             result[index] = None
#             continue

#         change = input_amount - required_amount - entry.fee

#         if entry.receive_address:
#             change -= entry.marker

#         chain = get_chain(config.chain)

#         outputs[entry.send_address] = utils.amount(change, chain["decimals"])

#         outputs["data"] = entry.payload

#         if entry.receive_address:
#             outputs[entry.receive_address] = utils.amount(
#                 entry.marker, chain["decimals"]
#             )

#         raw_tx = await utils.make_request(
#             "createrawtransaction", [inputs, outputs]
#         )

#         if "error" in raw_tx:
#             result[index] = None
#             continue

#         result[index] = raw_tx

#     return result
