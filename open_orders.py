from solana.publickey import PublicKey
import json

class OpenOrdersAccount: 
    def __init__(self, bytes):
        # Remove "serum" and "padding"
        bytes = bytes[5:-7]
        self.account_flags = int.from_bytes(bytes[0:8], "little")
        self.market = []
        for i in range(32):
            self.market.append(int.from_bytes(bytes[8+i:9+i], "little"))
        self.owner = PublicKey(bytes[40:72]).__str__()
        self.native_base_free = int.from_bytes(bytes[72:80], "little")
        self.native_base_total = int.from_bytes(bytes[80:88], "little")
        self.native_quote_free = int.from_bytes(bytes[88:96], "little")
        self.native_quote_total = int.from_bytes(bytes[96:104], "little")
        self.free_slot_bits = int.from_bytes(bytes[104:120], "little")
        self.is_bid_bits = int.from_bytes(bytes[120:136], "little")
        self.orders = []
        for i in range(128):
            starting_index = 136 + i*16
            ending_index = 136 + (i + 1) * 16
            self.orders.append(
                int.from_bytes(bytes[starting_index:ending_index], "little")
            )
        self.client_order_ids = []
        for i in range(128):
            starting_index = 2184 + i*8
            ending_index = 2184 + (i + 1) * 8
            self.orders.append(
                int.from_bytes(bytes[starting_index:ending_index], "little")
            )
        self.referrer_rebates_accrued = int.from_bytes(bytes[3208:3216], "little")
    def get_owner(self):
        return self.owner
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)