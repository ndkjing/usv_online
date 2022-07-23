import re
recv_content='B001,231'
ship_id = re.findall('[AB](\d+)',recv_content)
print(ship_id)