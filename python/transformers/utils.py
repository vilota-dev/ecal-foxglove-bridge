from scipy.spatial.transform import Rotation as R
import sophus as sp
import numpy as np

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
