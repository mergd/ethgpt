import uvicorn
from web3 import Web3, HTTPProvider
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional
import requests
import nparseTx
import re
import json
import os

from nparseTx import nparseTx
app = FastAPI()
w3 = Web3(HTTPProvider('https://eth.merkle.io'))


class Item(BaseModel):

    type: str = Field(..., pattern="^(ens|address|tx_hash)$")
    name: Optional[str] = None
    address: Optional[str] = None
    tx_hash: Optional[str] = None
    chain: Optional[str] = 'ethereum'

    @validator('name')
    def validate_name(cls, v, values, **kwargs):
        if 'type' in values and values['type'] == 'ens' and not v.endswith('.eth'):
            raise ValueError('ENS name must end with .eth')
        return v

    @validator('address')
    def validate_address(cls, v, values, **kwargs):
        if 'type' in values and values['type'] == 'address' and not re.match("^0x[a-fA-F0-9]{40}$", v):
            raise ValueError('Invalid Ethereum address')
        return v

    @validator('tx_hash')
    def validate_tx_hash(cls, v, values, **kwargs):
        if 'type' in values and values['type'] == 'tx_hash' and not re.match("^0x[a-fA-F0-9]{64}$", v):
            raise ValueError('Invalid transaction hash')
        return v


@app.post("/api/")
async def api(item: Item):
    try:
        if item.type == 'ens':
            eth_address = w3.ens.address(item.name)
            return {'address': eth_address}

        elif item.type == 'address':
            balance = w3.eth.get_balance(item.address)
            transaction_count = w3.eth.get_transaction_count(item.address)
            #  bruh cf gated api
            # # query llama api
            # llamaApiCall = requests.get(
            #     f'https://accounts.llama.fi/api/v2/address/{item.address}')
            # llamaApiCall.raise_for_status()
            # llamaLabels = parseLlamalabels(llamaApiCall.json())
            return {'balance': f'{balance/1e18} ETH', 'transaction_count': transaction_count}

        elif item.type == 'tx_hash':
            response = requests.get(
                f'https://tx.eth.samczsun.com/api/v1/trace/ethereum/{item.tx_hash}')
            response.raise_for_status()
            parsed = nparseTx(response.json())
            return parsed
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# no api works to get this to work
# @app.get("/address/transactions/")
# async def transactions(address: str):
#     start = (page - 1) * 10
#     end = start + 10
#     transactions = w3.eth.get_transaction_count(address)
#     return {'transactions': transactions[start:end]}


def parseLlamalabels(data):
    labels = []
    for label in list(data.values())[0]:
        labels.append({label['text'], label['tooltip']})
    return labels


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
