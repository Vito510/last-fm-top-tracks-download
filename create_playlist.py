import os
from natsort import natsorted

LIMIT = 100

with open(f"./playlist_{LIMIT}.m3u8", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for i, file in enumerate(natsorted(os.listdir("./downloads"), key=str.lower)):
        if i >= LIMIT:
            break
        
        f.write(f"#EXT-X-RATING:0\n{file}\n") 