#!/usr/bin/env python3
from transformers.Base import BaseTransformer, ecal_capnp_path

import capnp
capnp.add_import_hook([ecal_capnp_path])
import tagdetection_capnp as eCALMsg

import json
import numpy as np
import base64, cv2

from scipy.spatial.transform import Rotation as R
import sophus as sp

# from transformers.utils import capnp_se3_to_sophus_se3

class TagDetectionsTransformer(BaseTransformer):
    def __init__(self, topic):
        super().__init__(topic, eCALMsg, "TagDetections")
        self.sub.set_callback(self.transform)

    def delete(self):
        # TODO: fix cleanup
        self.sub.rem_callback(self.transform)

    def capnp_se3_to_sophus_se3(self, capnp_se3):
        w = capnp_se3.orientation.w
        x = capnp_se3.orientation.x
        y = capnp_se3.orientation.y
        z = capnp_se3.orientation.z

        return self.make_se3(capnp_se3.position.x,
                                capnp_se3.position.y,
                                capnp_se3.position.z,
                                w, x, y, z)

    def make_se3(self, x, y, z, qw, qx, qy, qz):
        t = np.array([x, y, z], dtype=np.float64)
        r = R.from_quat([qx, qy, qz, qw]).as_matrix()
        return sp.SE3(r, t)

    def transform(self, topic_type, topic_name, msg, ts):
        ts = msg.header.stamp
        data = {}
        data['timestamp'] = {
            "sec":  ts // 1000000000,
            "nsec": ts % 1000000000
        }
        data['frame_id'] = "nwu"
        data['format'] = "webp"

        img = msg.image
        if img.encoding == "bgr8":
            h = img.height
            w = img.width
            img_ndarray = cv2.resize(np.frombuffer(img.data, dtype=np.uint8).reshape((h, w, 3)), 
                           (w // 2, h // 2),
                           interpolation = cv2.INTER_NEAREST).reshape((h // 2, w // 2, 3))
            jpg_img = cv2.imencode('.webp', img_ndarray)
            data['data'] = base64.b64encode(jpg_img[1]).decode('utf8')
        else:
            print("Unsupported image format: " + img.encoding)
            return
       
        payload = json.dumps(data).encode("utf8")

        tag_data = {}
        tag_data['timestamp'] = {
            "sec":  ts // 1000000000,
            "nsec": ts % 1000000000
        }
        tag_data['frame_id'] = "body_nwu"
        tag_data['poses'] = []
        body_T_cam = self.capnp_se3_to_sophus_se3(capnp_se3 = msg.cameraExtrinsic.bodyFrame)
        tags = msg.tags
        
        for tag in tags:
            cam_T_tag = self.capnp_se3_to_sophus_se3(capnp_se3 = tag.poseInCameraFrame)
            body_T_tag = body_T_cam * cam_T_tag

            position = body_T_tag.translation()
            orientation = R.from_matrix(body_T_tag.so3().matrix()).as_quat()
            tag_data['poses'].append({
                "id": tag.id,
                "position": {
                    "x": position[0],
                    "y": position[1],
                    "z": position[2]
                },
                "orientation": {
                    "w": orientation[0],
                    "x": orientation[1],
                    "y": orientation[2],
                    "z": orientation[3]
                }
            })

        self.notify_callbacks("foxglove.CompressedImage", topic_name, payload, msg.header.stamp)
        self.notify_callbacks("foxglove.PosesInFrame", topic_name, 
                              json.dumps(tag_data).encode("utf8"), msg.header.stamp)
