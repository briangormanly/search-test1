from google import search
from google import get_page

for url in search("Brian Gormanly", stop=20):
	print(url)
	print( get_page(url))
