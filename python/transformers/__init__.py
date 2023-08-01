#!/usr/bin/env python3
from transformers.Odometry3D import Odometry3DTransformer
from transformers.Path import PathTransformer

ecal_schema_to_transformer = {
    "Odometry3d": Odometry3DTransformer,
    "Path": PathTransformer
}
