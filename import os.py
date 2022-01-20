import os


camera_user = 'aperezcr'
os.system(f'python .\s3bucket.py -u { camera_user } -i 192.168.1.71 -p merakiate98 -P C:/Users/aperezcr -o output_test -d 15 -s aws -r aperez.com -l es-ES')