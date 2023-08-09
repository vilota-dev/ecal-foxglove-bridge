#!/usr/bin/env python3
from transformers.Base import BaseTransformer, ecal_capnp_path

import capnp
capnp.add_import_hook([ecal_capnp_path])
import odometry3d_capnp as eCALMsg

import json

class Odometry3DTransformer(BaseTransformer):
    def __init__(self, topic):
        super().__init__(topic, eCALMsg, "Odometry3d")
        self.sub.set_callback(self.transform)

    def delete(self):
        # TODO: fix cleanup
        self.sub.rem_callback(self.transform)

    def transform(self, topic_type, topic_name, msg, ts):
        position_msg = msg.pose.position
        orientation_msg = msg.pose.orientation
        frame = "nwu" if msg.bodyFrame == 0 else "ned"

        odom_data = {}
        tf_data = {}
        odom = {}
        odom['position'] = tf_data['translation'] = { 
            "x": position_msg.x, 
            "y": position_msg.y,
            "z": position_msg.z }
        odom['orientation'] = tf_data['rotation'] = {
            "x": orientation_msg.x,
            "y": orientation_msg.y,
            "z": orientation_msg.z,
            "w": orientation_msg.w }
        odom_data['poses'] = [odom]
        odom_data['timestamp'] = {
            "sec": msg.header.stamp // 1000000000,
            "nsec": msg.header.stamp % 1000000000
        }
        odom_data['frame_id'] = tf_data['timestamp'] = frame
        frame_prefix = f"{msg.header.frameId}_" if msg.header.frameId != "" else ""
        tf_data['child_frame_id'] = f"{frame_prefix}body_{frame}"
        tf_data['parent_frame_id'] = frame
        
        self.notify_callbacks("foxglove.PosesInFrame", topic_name, 
                              json.dumps(odom_data).encode("utf8"), msg.header.stamp)
        self.notify_callbacks("foxglove.FrameTransform", topic_name, 
                              json.dumps(tf_data).encode("utf8"), msg.header.stamp)
