from blockchain.server import blockchain
from node.app import bootstrap_node

from dotenv import load_dotenv
load_dotenv(".env")


blockchain.mount("/node", bootstrap_node)

