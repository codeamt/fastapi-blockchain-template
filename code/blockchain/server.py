import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .data_structs import Block, Peer, \
    Blockchain, Transaction


chain = Blockchain()
blockchain = FastAPI()


blockchain.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@blockchain.get("/")
async def index():
    """
    Index endpoint for Blockchain server.
    :return: str
    """
    return "Index"


@blockchain.get("/mainchain")
async def b_chain() -> dict:
    """
    Ledger endpoint for Blockchain server.
    :return: dict -> keys: chain:Lis[dict] -> Serialized Blocks
    """
    authority_chain = await chain.consensus()
    return {"chain": authority_chain["chain"]}


@blockchain.get("/peers")
async def peers() -> dict:
    """
    Peers List endpoint for Blockchain Server.
    :return: dict -> keys: peers: List[str]
    """
    ips = [peer.ip for peer in chain.peers]
    return {"peers": ips}


@blockchain.get("/new-peer")
async def new_peer(request: Request) -> dict:
    """
    :param request: Request -> HTTP GET request.
    :return: dict -> keys: new_peer:str -> IP Address
    """
    peer_host = request.client.host
    peer_port = request.client.port
    if peer_host == "127.0.0.1":
        address = f"{chain.address}/node"
    else:
        address = f"http://{peer_host}:{peer_port}"
    print(address)
    chain.peers.add(Peer(address))
    return {"new_peer": address}


@blockchain.post("/new_tx")
async def new_tx(request: Request) -> dict:
    """
    New Transaction endpoint for Blockchain Server.
    :param request: Request -> HTTP POST request.
    :return: dict -> keys: sender:str; receipt:dict
    """
    peer = request.client.host
    tx = await request.json()
    tx = Transaction(**tx)
    chain.mempool.put_nowait(tx)
    return {"sender": peer, "receipt": tx.receipt()}


@blockchain.get("/mempool")
async def mempool() -> dict:
    """
    Mempool endpoint for Blockchain Server.
    :return: dict -> keys: mempool:dict
    """
    return {"mempool": chain.mempool_state()}


@blockchain.post("/new_block")
async def new_block(request: Request) -> dict:
    """
    New Block endpoint for Blockchain Server.
    :param request: Request -> HTTP POST request.
    :return: dict -> keys: miner_address:str, latest_block:dict, new_chain:List[dict]
    """
    block: dict = await request.json()
    block = await chain.add_block(block)
    response_block = Block(**block).to_dict()

    miner_ip = f"{request.client.host}:{request.client.port}"
    for node in chain.peers:
        async with httpx.AsyncClient() as client:
            _ = await client.get(f"{node}/")
    temp_chain = {f"Block-{height}": data.to_dict()
                  for height, data in enumerate(chain.serialized)}
    return {"miner_address": miner_ip,
            "latest_block": response_block.dict(),
            "new_chain": temp_chain, }
