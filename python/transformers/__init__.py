#!/usr/bin/env python3
from transformers.Odometry3D import Odometry3DTransformer
from transformers.Path import PathTransformer
from transformers.Image import ImageTransformer

ecal_schema_to_transformer = {
    "Odometry3d": Odometry3DTransformer,
    "Path": PathTransformer,
    "Image": ImageTransformer
}
