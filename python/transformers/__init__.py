#!/usr/bin/env python3
from transformers.Odometry3d import Odometry3DTransformer
from transformers.Path import PathTransformer
from transformers.Image import ImageTransformer
from transformers.TagDetections import TagDetectionsTransformer
from transformers.Landmarks import LandmarksTransformer

ecal_schema_to_transformer = {
    "Odometry3d": Odometry3DTransformer,
    "Path": PathTransformer,
    "Image": ImageTransformer,
    "TagDetections": TagDetectionsTransformer,
    "Landmarks": LandmarksTransformer
}

subscriber_map = {}

def make_transformer(topic, name):
    if topic not in subscriber_map:
        subscriber_map[topic] = ecal_schema_to_transformer[name](topic)
    return subscriber_map[topic]
