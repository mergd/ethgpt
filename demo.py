import json

from alchemy import Alchemy
alchemy_api_key = 'c1OGTMqn4wxF8BDGT2QNrchHkgqAO58Y'
alchemy = Alchemy(alchemy_api_key)


print(alchemy.core.getAssetTransfers({
    fromBlock: "0x0",
    fromAddress: "0x5c43B1eD97e52d009611D89b74fA829FE4ac56b1",
    category: ["external", "internal", "erc20", "erc721", "erc1155"],
}))
