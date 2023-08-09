#!/usr/bin/env python3
from transformers.Base import BaseTransformer, ecal_capnp_path

import capnp
capnp.add_import_hook([ecal_capnp_path])
import image_capnp as eCALMsg

import json
import numpy as np
import base64, cv2

class ImageTransformer(BaseTransformer):
    def __init__(self, topic):
        super().__init__(topic, eCALMsg, "Image")
        self.sub.set_callback(self.transform)

    def delete(self):
        # TODO: fix cleanup
        self.sub.rem_callback(self.transform)

    def transform(self, topic_type, topic_name, msg, ts):
        ts = msg.header.stamp
        data = {}
        data['timestamp'] = {
            "sec":  ts // 1000000000,
            "nsec": ts % 1000000000
        }
        data['frame_id'] = "nwu"
        data['format'] = "webp"

        if msg.encoding == "mono8":
            h = msg.height
            w = msg.width
            img_ndarray = np.repeat(
                cv2.resize(np.frombuffer(msg.data, dtype=np.uint8).reshape((h, w, 1)),
                           (w // 2, h // 2),
                           interpolation = cv2.INTER_NEAREST).reshape((h // 2, w // 2, 1)),
                3, axis=2)
            jpg_img = cv2.imencode('.webp', img_ndarray)
            data['data'] = base64.b64encode(jpg_img[1]).decode('utf8')
        else:
            print("Unsupported image format: " + msg.encoding)
            return
       
        payload = json.dumps(data).encode("utf8")
        self.notify_callbacks("foxglove.CompressedImage", topic_name, payload, msg.header.stamp)
