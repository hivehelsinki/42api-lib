from intra import ic

ic.progress_bar = True
data = ic.pages_threaded('users', stop_page=5)

print(len(data))
