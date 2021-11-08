import fds
import os

search = 'city'
if not os.path.exists(search):
    os.makedirs(search)

fds.scrap(text=search, maximum=50000, output_folder=search)
