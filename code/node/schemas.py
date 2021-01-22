from pydantic import BaseModel
from typing import List


class Peer(BaseModel):
    """
    BaseModel for Peer ORM.
    """
    ip: str


class Transaction(BaseModel):
    """
    BaseModel for Transaction ORM.
    """
    author: str = ""
    content: str = ""


class Block(BaseModel):
    """
    BaseModel for Block ORM.
    """
    index: int = None
    transactions: List = []
    timestamp: str = None
    previous_hash: str = None
    nonce: int = 0












