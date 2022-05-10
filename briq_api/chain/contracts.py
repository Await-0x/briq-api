import json
import logging
import os

from starknet_py.contract import Contract
from starknet_py.net.client import Client

logger = logging.getLogger(__name__)

# TODO: load from file maybe.
abi = json.loads('[ { "members": [ { "name": "low", "offset": 0, "type": "felt" }, { "name": "high", "offset": 1, "type": "felt" } ], "name": "Uint256", "size": 2, "type": "struct" }, { "members": [ { "name": "token_id", "offset": 0, "type": "felt" }, { "name": "qty", "offset": 1, "type": "felt" } ], "name": "FTSpec", "size": 2, "type": "struct" }, { "inputs": [ { "name": "token_id", "type": "felt" } ], "name": "get_approved", "outputs": [ { "name": "approved", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "operator", "type": "felt" } ], "name": "is_approved_for_all", "outputs": [ { "name": "is_approved", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "data": [ { "name": "from_", "type": "felt" }, { "name": "to_", "type": "felt" }, { "name": "token_id_", "type": "Uint256" } ], "keys": [], "name": "Transfer", "type": "event" }, { "data": [ { "name": "value__len", "type": "felt" }, { "name": "value_", "type": "felt*" }, { "name": "id_", "type": "felt" } ], "keys": [], "name": "URI", "type": "event" }, { "inputs": [ { "name": "address", "type": "felt" } ], "name": "setBriqAddress", "outputs": [], "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" } ], "name": "balanceOf_", "outputs": [ { "name": "balance", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" } ], "name": "balanceDetailsOf_", "outputs": [ { "name": "token_ids_len", "type": "felt" }, { "name": "token_ids", "type": "felt*" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "index", "type": "felt" } ], "name": "tokenOfOwnerByIndex_", "outputs": [ { "name": "token_id", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "felt" } ], "name": "ownerOf_", "outputs": [ { "name": "owner", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "felt" } ], "name": "is_realms_set", "outputs": [ { "name": "is_realms", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "felt" } ], "name": "tokenURI_data", "outputs": [ { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "felt" } ], "name": "tokenURI_", "outputs": [ { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "token_id_hint", "type": "felt" }, { "name": "fts_len", "type": "felt" }, { "name": "fts", "type": "FTSpec*" }, { "name": "nfts_len", "type": "felt" }, { "name": "nfts", "type": "felt*" }, { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "name": "assemble", "outputs": [], "type": "function" }, { "inputs": [ { "name": "token_id", "type": "felt" }, { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "name": "setTokenURI", "outputs": [], "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "token_id", "type": "felt" }, { "name": "add_fts_len", "type": "felt" }, { "name": "add_fts", "type": "FTSpec*" }, { "name": "add_nfts_len", "type": "felt" }, { "name": "add_nfts", "type": "felt*" }, { "name": "remove_fts_len", "type": "felt" }, { "name": "remove_fts", "type": "FTSpec*" }, { "name": "remove_nfts_len", "type": "felt" }, { "name": "remove_nfts", "type": "felt*" }, { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "name": "updateBriqs", "outputs": [], "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "token_id", "type": "felt" }, { "name": "fts_len", "type": "felt" }, { "name": "fts", "type": "FTSpec*" }, { "name": "nfts_len", "type": "felt" }, { "name": "nfts", "type": "felt*" } ], "name": "disassemble", "outputs": [], "type": "function" }, { "inputs": [ { "name": "sender", "type": "felt" }, { "name": "recipient", "type": "felt" }, { "name": "token_id", "type": "felt" } ], "name": "transferOneNFT", "outputs": [], "type": "function" }, { "inputs": [ { "name": "approved_address", "type": "felt" }, { "name": "token_id", "type": "felt" } ], "name": "approve_", "outputs": [], "type": "function" }, { "inputs": [ { "name": "approved_address", "type": "felt" }, { "name": "allowed", "type": "felt" } ], "name": "setApprovalForAll_", "outputs": [], "type": "function" }, { "inputs": [], "name": "name", "outputs": [ { "name": "name", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [], "name": "symbol", "outputs": [ { "name": "symbol", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" } ], "name": "balanceOf", "outputs": [ { "name": "balance", "type": "Uint256" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" } ], "name": "balanceDetailsOf", "outputs": [ { "name": "token_ids_len", "type": "felt" }, { "name": "token_ids", "type": "felt*" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "index", "type": "felt" } ], "name": "tokenOfOwnerByIndex", "outputs": [ { "name": "token_id", "type": "Uint256" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "Uint256" } ], "name": "ownerOf", "outputs": [ { "name": "owner", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "Uint256" } ], "name": "tokenURI", "outputs": [ { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "token_id", "type": "Uint256" } ], "name": "tokenURIData", "outputs": [ { "name": "uri_len", "type": "felt" }, { "name": "uri", "type": "felt*" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "sender", "type": "felt" }, { "name": "recipient", "type": "felt" }, { "name": "token_id", "type": "Uint256" } ], "name": "transferFrom", "outputs": [], "type": "function" }, { "inputs": [ { "name": "token_id", "type": "Uint256" } ], "name": "getApproved", "outputs": [ { "name": "approved", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "owner", "type": "felt" }, { "name": "operator", "type": "felt" } ], "name": "isApprovedForAll", "outputs": [ { "name": "is_approved", "type": "felt" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "name": "approved_address", "type": "felt" }, { "name": "token_id", "type": "Uint256" } ], "name": "approve", "outputs": [], "type": "function" }, { "inputs": [ { "name": "approved_address", "type": "felt" }, { "name": "allowed", "type": "felt" } ], "name": "setApprovalForAll", "outputs": [], "type": "function" } ]')

NETWORKS = {
    "testnet": {
        "client": Client("testnet"),
        "set_contract": None,
    }
}

NETWORKS["testnet"]["set_contract"] = Contract(
    address=os.environ.get("SET_ADDRESS") or "0x0266b1276d23ffb53d99da3f01be7e29fa024dd33cd7f7b1eb7a46c67891c9d0",
    abi=abi,
    client=NETWORKS["testnet"]["client"],
)
