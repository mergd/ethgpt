import json
from eth_utils import big_endian_to_int
import re

# Rough ethereum transaction parser which tries to decode events

addresses = {}


def format_address(address):
    # query llamafi for price and name
    addresses.append(address)
    return f"0x{address[-40:]}"


def format_numeric(data):
    print(f"format_numeric {data}")
    if (int(data, 16) > 1e17) or (int(data, 16) < -1e17):
        # try to cast as a wad if possible
        return str(int(data, 16) / 10e18)

    return str(int(data, 16))


def parse_event(event_hash, contract_info, child):
    print(f"parsevent {event_hash}")
    for event_selector, event in contract_info['events'].items():
        if event_hash == event_selector:
            event_data = {"event": event['name']}
            indexed_count = 0
            # print(event['inputs'])
            # truncate initial 0x in child['data']
            child['data'] = child['data'][2:]

            for input in event['inputs']:
                if input['indexed']:
                    indexed_count += 1
                    # Format based on type
                    if input['type'].startswith('uint'):
                        event_data[input['name']] = format_numeric(
                            child['topics'][indexed_count])
                    elif input['type'] == 'address':
                        # print(f"input name: {input['name']}")
                        # print(f"input name: {child['topics'][indexed_count]}")
                        event_data[input['name']] = format_address(
                            child['topics'][indexed_count])
                    else:
                        event_data[input['name']
                                   ] = child['topics'][indexed_count]
                else:
                    # rough topic
                    topic = child['data'][0:64]
                    # remove topic from data
                    child['data'] = child['data'][64:]
                    if input['type'].startswith('uint'):
                        event_data[input['name']] = format_numeric(
                            topic) if topic else 0
                    elif input['type'] == 'address':
                        event_data[input['name']] = format_address(
                            topic)
                    else:
                        event_data[input['name']] = child['data']
            return event_data
    print(f"Event not found: {event_hash}")


def parse_children(children, to, contracts):
    parsed_data = {"call": {"contract": to, "logs": []}}
    for child in children:
        # print(f"reached {child}")
        if child['type'] == 'log':
            # print(f"reached log {child}")
            event_selector = child['topics'][0]
            contract_info = contracts.get(to)
            print(f"event_selector: {event_selector}")
            print(f"contract_info: {contract_info}")
            if contract_info:
                event_data = parse_event(event_selector, contract_info, child)
                if event_data:
                    parsed_data["call"]["logs"].append(event_data)

        elif child['type'] in ['call', 'delegatecall']:
            child_data = parse_children(
                child['children'], child['to'], contracts)
            if 'call' in child_data:  # To avoid empty call structures
                parsed_data["call"]["call"] = child_data["call"]
    return parsed_data


def parse_json(data):
    result = {
        "chain": data['result']['chain'],
        "txhash": data['result']['txhash'],
        "from": data['result']['entrypoint']['from'],
    }

    contracts = {}
    for address, contract_data in data['result']['addresses'].items():
        for codehash, contract_info in contract_data.items():
            contracts[address] = contract_info

    call_data = parse_children(
        data['result']['entrypoint']['children'], data['result']['entrypoint']['to'], contracts)

    if 'call' in call_data:  # To avoid empty call structures
        result["call"] = call_data["call"]

    return result


async def pullTokenInfo():
    # query llamafi for price and name
    url = 'coins.llama.fi/prices/current/'
    for address in addresses:
        url.append(f"ethereum:{address},")
    response = requests.get(url)
    response.raise_for_status()
    parsed = response.json()


async def nparseTx(data):
    res = parse_json(data)
    # formatted_res = json.dumps(res, indent=4)
    return res


# Parse the JSON data
if __name__ == "__main__":
    with open('gg.json', 'r') as f:
        data = json.load(f)

    res = parse_json(data)
    formatted_res = json.dumps(res, indent=4)
    print(formatted_res)
