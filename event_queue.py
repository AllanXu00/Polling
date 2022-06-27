from solana.publickey import PublicKey
import json

class EventQueueHeader: 
    def __init__(self, bytes):
        self.account_flags = int.from_bytes(bytes[0:8], "little")
        self.head = int.from_bytes(bytes[8:16], "little")
        self.count = int.from_bytes(bytes[16:24], "little")
        self.seq_num = int.from_bytes(bytes[24:32], "little")
    def __str__(self):
        return (
            "Account Flags: " + str(self.account_flags) + "\n" +
            "Head: " + str(self.head) + "\n" +
            "Count: " + str(self.count) + "\n" + 
            "Sequence Number: " + str(self.seq_num) + "\n" 
        )

class Event:
    def __init__(self, bytes):
        self.event_flags = int.from_bytes(bytes[0:1], "little")
        self.owner_slot = int.from_bytes(bytes[1:2], "little")
        self.fee_tier = int.from_bytes(bytes[2:3], "little")
        padding = []
        for i in range(5):
            padding.append(int.from_bytes(bytes[3+i:4+i], "little"))
        self._padding = padding
        self.native_quantity_released = int.from_bytes(bytes[8:16], "little")
        self.native_quantity_paid = int.from_bytes(bytes[16:24], "little")
        self.native_fee_or_rebate = int.from_bytes(bytes[24:32], "little")
        self.order_id = int.from_bytes(bytes[32:48], "little")
        self.owner = PublicKey(bytes[48:80]).__str__()
        self.client_order_id = int.from_bytes(bytes[80:], "little")
    def __str__(self):
        return (
            "Event Flags: " + str(self.event_flags) + "\n" + 
            "Owner Slot: " + str(self.owner_slot) + "\n" + 
            "Fee Tier: " + str(self.fee_tier) + "\n" + 
            "Padding: " + ', '.join(str(item) for item in self._padding) + "\n" + 
            "Native Quantity Released: " + str(self.native_quantity_released) + "\n" +
            "Native Quantity Paid: " + str(self.native_quantity_paid) + "\n" + 
            "Native Fee or Rebate: " + str(self.native_fee_or_rebate) + "\n" + 
            "Order ID: " + str(self.native_fee_or_rebate) + "\n" + 
            "Owner: " + str(self.owner) + "\n" + 
            "Client Order ID: " + str(self.client_order_id) + "\n"
        )

class EventAccount:
    def __init__(self, bytes):
        bytes_without_padding = bytes[5:-7]
        header_bytes = bytes_without_padding[0:32]
        events_bytes = bytes_without_padding[32:]
        self.event_queue_header = EventQueueHeader(header_bytes)
        self.events = []
        for i in range(self.event_queue_header.count):
            starting_index = ((self.event_queue_header.head + i) % 2978) * 88
            ending_index = (starting_index + 88) 
            self.events.append(Event(
                events_bytes[starting_index:ending_index]
            ))
            
    def print_overview(self):
        print(self.event_queue_header)
        print("Number of Events", len(self.events))
        
    def print_events(self):
        for i in range(self.event_queue_header.count):
            print("------------ Event Number", i+1, "----------")
            print(self.events[i])