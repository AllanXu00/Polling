import event_queue
import open_orders
import ordered_set
from solana.rpc.api import Client
from solana.publickey import PublicKey
import time
import base64
import argparse

def process_event(event, wallet_to_volume, client):
    # Get owner from Open Orders Account
    OPEN_ORDER = PublicKey(event.owner)
    account_info = client.get_account_info(OPEN_ORDER)
    account_data_raw = base64.b64decode(account_info['result']['value']['data'][0])
    open_orders_account = open_orders.OpenOrdersAccount(account_data_raw)
    owner = open_orders_account.get_owner()
    
    # Process the owner's volume
    if owner not in wallet_to_volume:
        wallet_to_volume[owner] = 0
    #if event.event_flags % 2 == 1:
    wallet_to_volume[owner] += event.native_quantity_paid
    wallet_to_volume[owner] += event.native_quantity_released
    

if __name__ == '__main__':
    # Command line arguements
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grainularity", help="seconds between polls", default = 60)
    parser.add_argument("-t", "--total", help="number of polls", default = 2)
    parser.add_argument("-e", "--event", help="pub key of event queue", default = "CNLTe8we7jy7usMunpDS9otvjF2qLXw9jMxUMnhVmKt6")
    args = parser.parse_args()
    grainularity = int(args.grainularity)
    total = int(args.total)

    # Solana Client
    client = Client("https://api.mainnet-beta.solana.com")
    EVENT_QUEUE = PublicKey(args.event)
    messages = dict()
    seen = ordered_set.OrderedSet()

    # Poll Solana accounts for raw data
    for idx in range(total):
        account_info = client.get_account_info(EVENT_QUEUE)
        account_data_raw = base64.b64decode(account_info['result']['value']['data'][0])
        assert len(account_data_raw) == 262156
        if account_data_raw not in seen:
            messages[idx] = account_data_raw
            seen.add(account_data_raw)
        time.sleep(grainularity)

    # Create list of parsed accounts from raw data
    parsed_accounts = []
    for raw_account in seen:
        parsed_accounts.append(event_queue.EventAccount(raw_account))
    num_parsed_accounts = len(parsed_accounts)
    wallet_to_volume = {}

    # Difference between accounts' events
    for i in range(num_parsed_accounts - 1):
        # Get difference between heads
        current_head = parsed_accounts[i].event_queue_header.head
        next_head = parsed_accounts[i+1].event_queue_header.head
        if current_head < next_head:
            difference = next_head - current_head 
        elif current_head == next_head:
            continue    
        else:
            difference = next_head + 2978 - current_head
        print("The current head, next head, and difference are", current_head, next_head, difference)
        
        # process all events that were processed between states
        current_count = parsed_accounts[i].event_queue_header.count
        for j in range(min(difference, current_count)):
            process_event(parsed_accounts[i].events[j], wallet_to_volume, client)

    # Last account's events
    for event in parsed_accounts[-1].events:
        process_event(event, wallet_to_volume, client)

    # Generate output
    print(wallet_to_volume)