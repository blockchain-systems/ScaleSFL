import typing
import requests


def invoke_chaincode(
    channel: str,
    contract: str,
    cc_fn: str,
    args: typing.List,
    server="localhost",
    port=5000,
):
    req = {
        "channel": channel,
        "contract": contract,
        "contractFunction": cc_fn,
        "args": args,
    }
    res = requests.post(
        f"http://{server}:{port}/transaction/invoke",
        json=req,
    )
    return res.text


def query_chaincode(
    channel: str,
    contract: str,
    cc_fn: str,
    args: typing.List,
    server="localhost",
    port=5000,
):
    req = {
        "channel": channel,
        "contract": contract,
        "contractFunction": cc_fn,
        "args": args,
    }
    res = requests.post(
        f"http://{server}:{port}/transaction/query",
        json=req,
    )
    return res.text
