import cv2
import requests
from PIL import Image
from io import BytesIO
import numpy as np  # Asegúrate de importar numpy

def stream_video(url):
    stream = requests.get(url, stream=True)
    if stream.status_code == 200:
        bytes = b''
        for chunk in stream.iter_content(chunk_size=1024):
            bytes += chunk
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b + 2]
                bytes = bytes[b + 2:]
                img = Image.open(BytesIO(jpg))
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    stream.close()
    cv2.destroyAllWindows()

url = "http://192.168.11.85/640x480.mjpeg"
stream_video(url)
