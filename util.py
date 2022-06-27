from solana.rpc.api import Client
from solana.publickey import PublicKey
import base64
import open_orders
import json

def parse_json(event, grainularity, total):
    f = open("{}_grainularity_{}_total_{}_key.json".format(grainularity, total, event))
    data = json.load(f)
    events = data["EventQueueAccount"]
    print(len(events), len(data))
    return data

def process_event(event, wallet_to_volume, data):
    owner = data[event['owner']]
    # Process the owner's volume
    if owner not in wallet_to_volume:
        wallet_to_volume[owner] = 0
    # Check if it's a fill event
    if event['event_flags'] % 2 == 1:
        wallet_to_volume[owner] += event['native_quantity_paid']
        wallet_to_volume[owner] += event['native_quantity_released']

def generate_table(data):
    parsed_accounts = data['EventQueueAccount']
    num_parsed_accounts = len(parsed_accounts)
    wallet_to_volume = {}
    # Difference between accounts' events
    for i in range(num_parsed_accounts - 1):
        # Get difference between heads
        current_head = parsed_accounts[i]['event_queue_header']['head']
        next_head = parsed_accounts[i+1]['event_queue_header']['head']
        if current_head < next_head:
            difference = next_head - current_head 
        elif current_head == next_head:
            continue
        else:
            difference = next_head + 2978 - current_head
        
        # process all events that were processed between states
        current_count = parsed_accounts[i]['event_queue_header']['count']
        for j in range(min(difference, current_count)):
            process_event(parsed_accounts[i]['events'][j], wallet_to_volume, data)

    # Last account's events
    for event in parsed_accounts[-1]['events']:
        process_event(event, wallet_to_volume, data)

    return wallet_to_volume