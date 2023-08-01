#!/usr/bin/env python3
from transformers.Base import BaseTransformer, ecal_capnp_path

import capnp
capnp.add_import_hook([ecal_capnp_path])
import odometry3d_capnp as eCALMsg

class Odometry3DTransformer(BaseTransformer):
    def __init__(self, topic):
        super().__init__(topic, eCALMsg, "Odometry3d")
        self.sub.set_callback(self.transform)

    def delete(self):
        # TODO: fix cleanup
        self.sub.rem_callback(self.transform)

    def transform(self, topic_type, topic_name, msg, ts):
        import json
        position_msg = msg.pose.position
        orientation_msg = msg.pose.orientation

        print(topic_name)

        data = {}
        odom = {}
        odom['position'] = { 
            "x": position_msg.x, 
            "y": position_msg.y,
            "z": position_msg.z }
        odom['orientation'] = {
            "x": orientation_msg.x,
            "y": orientation_msg.y,
            "z": orientation_msg.z,
            "w": orientation_msg.w }
        data['poses'] = [odom]
        data['time'] = {
            "secs": msg.header.stamp // 1000000000,
            "nsecs": msg.header.stamp % 1000000000
        }
        data['frame_id'] = "nwu"
        self.validate_json(data)
       
        payload = json.dumps(data).encode("utf8")
        self.notify_callbacks(topic_name, payload, msg.header.stamp)
