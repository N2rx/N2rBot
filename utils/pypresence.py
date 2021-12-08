from pypresence import Presence
import time

client_id = '872537488302964767'
RPC = Presence(client_id)
RPC.connect()

RPC.update(details='Running N2r Bot',
           large_image='n2rbot',
           large_text='N2r Bot',
           start=time.time())

print("Discord Status Online")