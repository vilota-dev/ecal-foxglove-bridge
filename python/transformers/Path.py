#!/usr/bin/env python3
from transformers.Base import BaseTransformer, ecal_capnp_path

import capnp
capnp.add_import_hook([ecal_capnp_path])
import path_capnp as eCALMsg

import json

class PathTransformer(BaseTransformer):
    def __init__(self, topic):
        super().__init__(topic, eCALMsg, "Path")
        self.sub.set_callback(self.transform)

    def delete(self):
        # TODO: fix cleanup
        self.sub.rem_callback(self.transform)

    def transform(self, topic_type, topic_name, msg, ts):
        print(topic_name)

        data = {}
        data['poses'] = []

        for pose in msg.path:
            odom = {}
            odom['position'] = { 
                "x": pose.px, 
                "y": pose.py,
                "z": pose.pz }
            odom['orientation'] = {
                "x": pose.qx,
                "y": pose.qy,
                "z": pose.qz,
                "w": pose.qw }
            data['poses'].append(odom)

        last_pose_ts = msg.path[-1].stamp
        
        data['time'] = {
            "secs": last_pose_ts // 1000000000,
            "nsecs": last_pose_ts % 1000000000
        }
        data['frame_id'] = "nwu"
        
        payload = json.dumps(data).encode("utf8")
        self.notify_callbacks("foxglove.PosesInFrame", 
                              topic_name, payload, last_pose_ts)
