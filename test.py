from intra import ic

ic.progress_bar = True
data = ic.pages_threaded('users', stop_page=15)

print(len(data))
