import requests
import numpy as np
import json
import cv2
import time

def process_mask_stream(stream_url, return_mask=False):
    prev_time = time.time()
    response = requests.post(stream_url, stream=True)
    shape_info = None
    data = b''
    frames = 0
    print(response.iter_content,"reached here")
    for chunk in response.iter_content(chunk_size=10240):
        # print(chunk,"line 14")
        data += chunk
        if b'--frame-end\r\n' in data:
            splits = data.split(b'--frame-end\r\n')
            print(len(splits))
            curr_data = splits[0]
            data = b'--frame-end\r\n'.join(splits[1:])
            shape_start = curr_data.find(b'--json\r\n') + len(b'--json\r\n')
            shape_end = curr_data.find(b'--json-end\r\n')
            shape_info = curr_data[shape_start:shape_end]
            shape_info = json.loads(shape_info.decode())
            dtype = np.dtype(shape_info["dtype"])
            width = shape_info["width"]
            height = shape_info["height"]
            channels = shape_info["channels"]
            print(width, height)

            frame_start = curr_data.find(b'--frame\r\n') + len(b'--frame\r\n')
            frame_data = curr_data[frame_start:]
            mask = np.frombuffer(frame_data, dtype=dtype).reshape((height, width, channels))
            max = mask.max()
            print(mask.shape)
            if return_mask:
                mask = mask*255/max
                mask = mask[...,0]
            else:
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)
            cv2.imshow("Mask", mask)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frames+=1
            # Calculate FPS based on time between frames
            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time

            print(f"Frame: {frames}, FPS: {fps:.2f}")
    end = time.time()
# Usage
STREAM_URL = "rtsp://135.237.162.70:8554/test-stream"
PROMPT =  "track all the dogs in the video"

MASK = False

url = f"http://20.80.252.146/video_feed?stream_url={STREAM_URL}&prompt={PROMPT}&mask={str(MASK).lower()}"
# print(url)
process_mask_stream(url, return_mask=MASK)
