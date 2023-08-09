#!/usr/bin/env python3
from transformers.Base import BaseTransformer, ecal_capnp_path

import capnp
capnp.add_import_hook([ecal_capnp_path])
import landmarks_capnp as eCALMsg

import json

class LandmarksTransformer(BaseTransformer):
    def __init__(self, topic):
        super().__init__(topic, eCALMsg, "Landmarks")
        self.sub.set_callback(self.transform)

    def delete(self):
        # TODO: fix cleanup
        self.sub.rem_callback(self.transform)

    def transform(self, topic_type, topic_name, msg, ts):

        data = {}
        data['cubes'] = []

        for lm in msg.landmarks:
            cube = {}
            pose = lm.pose
            position = pose.position
            orientation = pose.orientation
            if lm.id != 3:
                continue

            cube['pose'] = {}
            cube['pose']['position'] = {
                "x": position.x, 
                "y": position.y,
                "z": position.z }
            cube['pose']['orientation'] = {
                "x": orientation.x,
                "y": orientation.y,
                "z": orientation.z,
                "w": orientation.w }
            cube['size'] = {
                "x": 0.02,
                "y": lm.size,
                "z": lm.size
            }
            cube['color'] = {
                "r": 0.0,
                "g": 1.0,
                "b": 0.0,
                "a": 1.0
            }
            cube['id'] = lm.id
            data['cubes'].append(cube)
        
        ts = msg.header.stamp
        data['timestamp'] = {
            "sec": ts // 1000000000,
            "nsec": ts % 1000000000
        }
        data['lifetime'] = {
            "sec": 10,
            "nsec": 0
        }
        data['frame_id'] = "nwu"
        data['id'] = "april_landmarks"
        data['frame_locked'] = "true"
        data['metadata'] = []

        sceneupdate = {
            "entities" : [data],
            "deletions" : [],
        }

        payload = json.dumps(sceneupdate).encode("utf8")
        self.notify_callbacks("foxglove.SceneUpdate", 
                              topic_name, payload, ts)
