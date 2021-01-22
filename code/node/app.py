import os
import httpx
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Block, Transaction


bootstrap_node = FastAPI()
local_chain = []


bootstrap_node.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@bootstrap_node.on_event("startup")
async def load_local_chain() -> dict:
    """
    Populates local list with serialized blocks from server.
    """
    async with httpx.AsyncClient() as client:
        _ = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/new-peer/")
        response = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/mainchain/")
        print(response.json())
        global local_chain
        local_chain = response.json()["chain"]


@bootstrap_node.get("/")
async def index() -> dict:
    """
    Index endpoint for Bootstrap Node Client.
    :return: dict: keys: local_chain: List[dict] -> Local chain.
    """
    async with httpx.AsyncClient() as client:
        _ = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/new-peer/")
        response = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/mainchain/")
        global local_chain
        local_chain = response.json()["chain"]
    return {"local_chain": [block for block in local_chain]}


@bootstrap_node.get("/chain")
async def get_local_chain() -> dict:
    """
    Consensus Endpoint for BootStrap Node App.
    :return: dict: keys: local_chain: List[dict]
    """
    return {"local_chain":  [block for block in local_chain]}


@bootstrap_node.get("/add-peer")
async def new_peer_node() -> dict:
    """
    Endpoint for adding new Peer.
    :return: dict: keys: new_peer:str
    """
    async with httpx.AsyncClient() as client:
        confirm = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/new-peer")
    return confirm.json()


@bootstrap_node.get("/peer-nodes")
async def peers() -> dict:
    """
    Network Peers List Endpoint for Bootstrap Node App.
    :return: dict: List[str]
    """
    async with httpx.AsyncClient() as client:
        confirm = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/peers/")
        return confirm.json()


@bootstrap_node.get("/mine")
async def index() -> dict:
    """
    Mining Endpoint for Bootstrap Node App.
    :return: dict: block:dict -> New Block (serialized)
    """
    block = Block()
    block.index = len(local_chain) + 1
    block.timestamp = str(datetime.utcnow())
    async with httpx.AsyncClient() as client:
        confirm = await client.post(f"{os.environ.get('BLOCKCHAIN_URL')}/new_block", json=block.dict())
    return confirm.json()


@bootstrap_node.get("/transact")
async def index() -> dict:
    """
    New Transaction Endpoint for Bootstrap Node App.
    :return: dict: keys: sender:str; receipt:dict
    """
    tx = Transaction()
    tx.timestamp = str(datetime.now())
    async with httpx.AsyncClient() as client:
        confirm = await client.post(f"{os.environ.get('BLOCKCHAIN_URL')}/new_tx", json=tx.dict())
    return confirm.json()


@bootstrap_node.get("/mem_pool")
async def mempool() -> dict:
    """
    Mempool Endpoint for Bootstrap Node App.
    :return: dict: keys: mempool:dict -> Mempool State.
    """
    async with httpx.AsyncClient() as client:
        confirm = await client.get(f"{os.environ.get('BLOCKCHAIN_URL')}/mempool")
        return confirm.json()
