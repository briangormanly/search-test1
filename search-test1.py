import urllib
import json as m_json
query = raw_input ( 'Query: ' )
query = urllib.urlencode ( { 'q' : query } )
print( 'http://www.google.com/search?' + query )
response = urllib.urlopen ( 'https://www.google.com/search?q=' + query ).read()
#json = m_json.loads ( response )
print( response )
#results = json [ 'responseData' ] [ 'results' ]
#for result in results:
#    title = result['title']
#    url = result['url']   # was URL in the original and that threw a name error exception
#    print ( title + '; ' + url )
