from blockchain.server import blockchain
from node.app import bootstrap_node


blockchain.mount("/node", bootstrap_node)


