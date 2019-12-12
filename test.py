import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
st = os.path.join(os.path.dirname(BASE_DIR), "/static/")
print(os.path.join('/home/ubuntu/luxmundi', "static/"))
