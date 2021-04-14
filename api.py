import aiohttp


async def get_nft_eth(address):
    url = "https://api.opensea.io/api/v1/assets"
    tokens = {}
    params = {
        "order_direction": "desc",
        "offset": 0,
        "limit": 50,
        "owner": address
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            info = await response.json()
            info2 = info['assets']
            for data in info2:
                token_name = data["name"]
                link = data["permalink"]
                tokens_info = {f"{token_name}": f"{link}"}
                tokens.update(tokens_info)
            return tokens


async def get_nft_bsc(address):
    url = f"https://api.covalenthq.com/v1/56/address/{address}/balances_v2/?nft=true"
    tokens = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            info = await response.json()
            info2 = info.get('data').get('items')
            for data in info2:
                token_name = data["contract_name"]
                token_address = data["contract_address"]
                token_type = data["type"]
                token_balance = int(data["balance"])
                if token_type == "nft" and token_balance > 0:
                    link = f"https://www.bscscan.com/token/{token_address}?a={address}"
                    tokens_info = {f"{token_name}": f"{link}"}
                    tokens.update(tokens_info)
            return tokens
