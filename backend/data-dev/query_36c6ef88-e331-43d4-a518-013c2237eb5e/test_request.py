import requests
files = {'upload_file': open('../query_0fbfb73c-92ec-4730-be94-f2c9498ad02c/52e57fe30bed4b118380df20567a2b3d_model3d_compressed.npz', 'rb')}
url = 'http://127.0.0.1:8000/hicquery/hicqueries/0fbfb73c-92ec-4730-be94-f2c9498ad02c/'
r = requests.put(url, files=files, data={'title':'test_generate'})
print(r.content)
