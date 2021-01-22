import os
import json
import httpx
import queue
import hashlib
from typing import List, Set
from uuid import uuid4
from datetime import datetime


class Transaction(object):
    """
    ORM Model for Transaction.
    """

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Transaction instance from a dictionary.
        :param data: dict -> dictionary mapping to member values.
        :return: Transaction
        """
        allowed_keys = ["author", "content"]
        tx = {k: v for k, v in data.items() if k in allowed_keys}
        return cls(**tx)

    def __init__(self, author: str = " ", content: str = ""):
        """
        Instantiate a Transaction.
        :param author:str -> transaction sender.
        :param content:str -> transaction data
        TODO: implement transaction signing.
        """
        self._id: str = str(uuid4()[:9])
        self.timestamp: str = str(datetime.utcnow())
        self.author: str = author
        self.content: str = content
        self.hash: str = ""

    def receipt(self):
        """
        Create a receipt for the Transaction.
        :return: dict -> Serialized Transaction.
        """
        self.hash = str(self.__hash__())
        return self.__dict__


class Block(object):
    """
    ORM Model of Block.
    """
    def __init__(self, index, txs: List):
        """
        Instantiate a Block.
        :param index: int -> Index ("height") on the Blockchain.
        :param txs:List[Transaction]
        """
        self.index = index
        self.transactions = txs
        self.timestamp = str(datetime.now())
        self.previous_hash = "None"
        self.nonce = 0
        self.hash: str = "None"

    def generate_hash(self):
        """
        Generates, assigns hexdigest of hash encoded Block contents
        :return: str -> Block's hash.
        """
        block_serialized = json.dumps(self.__dict__, sort_keys=True)
        proof = hashlib.sha256(block_serialized.encode()).hexdigest()
        self.hash = proof
        return proof

    def to_dict(self):
        """
        Serializes Block.
        :return: dict
        """
        # block_serialized = json.dumps(self.__dict__, sort_keys=True)
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Block instance from a dictionary object.
        :param data: dict ->  dictionary mapping to member values.
        :return: Block
        """
        allowed_keys = ["index", "transactions", "timestamp",
                        "previous_hash", "nonce", "hash"]
        block = {k: v for k, v in data.items() if k in allowed_keys}
        return cls(**block)


class Peer(object):
    """
    ORM Model for Peer.
    """
    def __init__(self, address: str):
        """
        Instantiates Peer object.
        :param address: str -> Peer IP address.
        """
        self.ip = address


class Blockchain(object):
    """
    ORM Model for Blockchain.
    """
    def __init__(self):
        """
        Instantiates a Blockchain.
        """
        self.difficulty = int(os.environ.get("INITIAL_DIFFICULTY"))
        self.address = os.environ.get("BLOCKCHAIN_URL")
        self.mempool = queue.Queue()
        self.pending_tsx = int(len(list(self.mempool.queue)))
        self.blockchain: List[Block] = []
        self.serialized = [b.__dict__ for b in self.blockchain]
        self.peers: Set[Peer] = set([])
        self.initialize_blockchain()
        print(self.blockchain[-1].to_dict())

    def network_state(self):
        """
        A method for getting a network snapshot.
        :return: dict
        """
        state = {"timestamp": str(datetime.utcnow()),
                 "difficulty": self.difficulty,
                 "num_pending_txs": self.pending_tsx,
                 "chain_height": len(self.blockchain),
                 "latest_block": self.blockchain[-1].to_dict(),
                 "num_peers": len(list(self.peers))}
        return state

    def mempool_state(self):
        """
        A method for getting a Mempool Snapshot.
        :return: dict
        """
        state = {
            "timestamp": str(datetime.utcnow()),
            "size": self.pending_tsx,
        }

        response = {
            "state": state,
            "mempool": [tx.__dict__ for tx in list(self.mempool.queue)]
        }
        return response

    def initialize_blockchain(self):
        """"
        Generates and appends Genesis Block to initialize the Blockchain.
        """
        genesis = Block(index=0, txs=[])
        genesis.previous_hash = None
        genesis.generate_hash()
        self.blockchain.append(genesis)
        self.serialized = [b.__dict__ for b in self.blockchain]
        print(self.blockchain)

    async def is_valid_proof(self, block: Block,  query: str) -> bool:
        """

        :param block: Block -> Block being validated.
        :param query: str -> Potential Proof of Work for Block.
        :return: bool
        """
        return (query.startswith("0" * self.difficulty) and
                query == block.generate_hash())

    async def check_chain_validity(self, candidate: List) -> bool:
        """
        Checks whether or not a candidate blockchain is valid.
        :param candidate: List[dict] -> The list of blocks,
        representing the candidate chain.
        :return bool
        """
        result = True
        previous_hash = "0"
        for block in candidate:
            block_hash = block.hash
            delattr(block, "hash")
            if not await self.is_valid_proof(block, block.hash) \
                    or previous_hash != block.previous_hash:
                result = False
                break
            block.hash = block_hash
            previous_hash = block_hash
        return result

    async def PoW(self, block: Block):
        """
        Iterates through potential proofs, until difficulty constraint is met.
        :param block: Block -> Block to be hashed.
        :return: str -> proof for the Block
        """
        proof = block.generate_hash()
        while not proof.startswith("0" * self.difficulty):
            block.nonce += 1
            proof = block.generate_hash()
        return proof

    async def consensus(self):
        """
        Gains consensus amongst peers of the network about the correct ledger.
        :return: dict -> keys: chain: Listp[dict] -> serialized blocks;
        consensus: bool -> Whether or not peers have consensus.
        """
        if len(list(self.peers)) <= 1:
            return {"chain": self.serialized,
                    "consensus": "True"}

        longest_chain = None
        curr_len = len(self.serialized)

        for node in self.peers:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{node.ip}/chain")
                print(response.json())
                peer_chain: List = response.json()["local_chain"]
                length = len(peer_chain)
                if length > curr_len and self.check_chain_validity(peer_chain):
                    curr_len = length
                    longest_chain = peer_chain
        if longest_chain:
            self.blockchain = [Block(**data) for data in longest_chain]
            self.serialized = longest_chain
            return {"chain": self.serialized, "consensus": True}

        return {"chain": self.serialized, "consensus": False}

    async def add_block(self, block: dict):
        """
        Adds valid Block to the blockchain.
        :param block: dict -> Latest (valid) Block.
        :return: -> Block
        """
        if not self.mempool.empty():
            txs = [self.mempool.get_nowait() for _ in range(len(list(self.mempool.queue)))]
        else:
            txs = []
        orm_block = Block(**block)
        orm_block.transactions = [Transaction(**tx) for tx in txs if len(txs) > 0]
        proof = await self.PoW(orm_block)
        orm_block.hash = proof
        self.blockchain.append(orm_block)
        self.serialized = [b.__dict__ for b in self.blockchain]
        return orm_block
