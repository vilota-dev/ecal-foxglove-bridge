from abc import ABC, abstractmethod

import json
import python_jsonschema_objects as pjs

jsonschema_path = "../external/foxglove-schemas/schemas/jsonschema"
ecal_python_path = "../external/ecal-common/python"
ecal_capnp_path = "../external/ecal-common/src/capnp"

import sys
sys.path.insert(0, ecal_python_path)
from capnp_subscriber import CapnpSubscriber

ecal_to_foxglove = {
    "Odometry3d": "PosesInFrame",
}

def read_json_schema(ecal_typename):
    json_typename = ecal_to_foxglove[ecal_typename]
    return open(f"{jsonschema_path}/{json_typename}.json")

class BaseTransformer(ABC):
    TransformType = None

    def __init__(self, topic, ecal_msg, name) -> None:
        ecal_struct = ecal_msg.__dict__[name]

        self.subscribers = []
        self.json_schema = json.load(read_json_schema(name))
        self.json_builder = pjs.ObjectBuilder(self.json_schema)
        self.name = name
        self.topic = topic
        self.typeclass = ecal_struct
        self.sub = CapnpSubscriber(self.name, 
                            self.topic, 
                            self.typeclass)

    def set_callback(self, callback):
        self.subscribers.append(callback)

    def notify_callbacks(self, topic_name, msg, ts):
        for callback in self.subscribers:
            callback(topic_name, msg, ts)

    @abstractmethod
    def delete(self):
        ...

    @abstractmethod
    def transform(self, data):
        ...
