from abc import ABC, abstractmethod

import json
from jsonschema import validate

jsonschema_path = "../external/foxglove-schemas/schemas/jsonschema"
ecal_python_path = "../external/ecal-common/python"
ecal_capnp_path = "../external/ecal-common/src/capnp"

import sys
sys.path.insert(0, ecal_python_path)
from capnp_subscriber import CapnpSubscriber

ecal_to_foxglove = {
    "Odometry3d": ["PosesInFrame", "FrameTransform"],
    "Path": ["PosesInFrame"],
    "Image": ["CompressedImage"],
    "TagDetections": ["CompressedImage", "PosesInFrame"],
    "Landmarks" : ["SceneUpdate"]
}

def read_json_schema(json_typename: str):
    return open(f"{jsonschema_path}/{json_typename}.json")

class BaseTransformer(ABC):

    def __init__(self, topic, ecal_msg, name) -> None:
        # ecal types
        self.topic = topic
        self.name = name
        self.typeclass = ecal_msg.__dict__[name]

        # foxglove types
        self.foxglove_types = ecal_to_foxglove[name]
        self.jsonschemas = [json.load(read_json_schema(type)) for type in self.foxglove_types]
        
        self.sub = CapnpSubscriber(self.name,
                            self.topic,
                            self.typeclass)

        # external callbacks
        self.subscribers = {}
        for type in self.foxglove_types:
            self.subscribers[f"foxglove.{type}"] = []

    def set_callback(self, foxglove_type, callback):
        self.subscribers[foxglove_type].append(callback)

    def notify_callbacks(self,
                         foxglove_type,
                         topic_name, msg, ts):
        for cb in self.subscribers[foxglove_type]:
            cb(topic_name, msg, ts)

    # can throw jsonschema.exceptions.ValidationError
    # or jsonschema.exceptions.SchemaError
    def validate_json(self, instance):
        validate(instance=instance, schema=self.json_schema)

    @abstractmethod
    def delete(self):
        ...

    @abstractmethod
    def transform(self, data):
        ...
