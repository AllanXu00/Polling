import json 
import event_queue
import open_orders
import ordered_set
from solana.rpc.api import Client
from solana.publickey import PublicKey
import time
import base64
import argparse

if __name__ == '__main__':
    # Command line arguements
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grainularity", help="seconds between polls", default = 60)
    parser.add_argument("-t", "--total", help="number of polls", default = 2)
    # BTC/USDC event queue
    parser.add_argument("-e", "--event", help="pub key of event queue", default = "AgtsKGytmt4vyU2U5ziPyQYEgHsNjizU4HWrv5sK1T24")
    args = parser.parse_args()
    grainularity = float(args.grainularity)
    total = int(args.total)

    # Solana Client
    client = Client("https://extend.mainnet.rpcpool.com/30af34cbb7f1e44cf8776c7ecae8")
    EVENT_QUEUE = PublicKey(args.event)
    seen = ordered_set.OrderedSet()

    dictionary = {}
    dictionary['EventQueueAccount'] = []

    # Poll Solana accounts for raw data
    for idx in range(total):
        account_info = client.get_account_info(EVENT_QUEUE)
        account_data_raw = base64.b64decode(account_info['result']['value']['data'][0])
        assert len(account_data_raw) == 262156
        if account_data_raw not in seen:
            seen.add(account_data_raw)
            parsed_event_queue_account = event_queue.EventAccount(account_data_raw)
            dictionary['EventQueueAccount'].append(parsed_event_queue_account)
            for event in parsed_event_queue_account.events:
                if event.owner in dictionary:
                    continue
                OPEN_ORDER = PublicKey(event.owner)
                open_orders_info = client.get_account_info(OPEN_ORDER)
                open_orders_data_raw = base64.b64decode(open_orders_info['result']['value']['data'][0])
                open_orders_account = open_orders.OpenOrdersAccount(open_orders_data_raw)
                dictionary[event.owner] = open_orders_account.owner
        time.sleep(grainularity)

    # subclass JSONEncoder
    class AccountEncoder(json.JSONEncoder):
            def default(self, o):
                return o.__dict__

    with open("{}_grainularity_{}_total_{}_key.json".format(grainularity, total, args.event), 'w') as outfile:
        json.dump(dictionary, outfile, cls = AccountEncoder)

