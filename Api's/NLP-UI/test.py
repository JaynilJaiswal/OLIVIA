import requests
import numpy as np

base="http://127.0.0.1:5000/"
payload={"input_str":"you are not sane"}
r = requests.get(base, params=payload).json()
print(r['result'])
