"""
Created on 12:39, June. 4th, 2021
Author: fassial
Filename: VoltageJump.py
"""
import brainpy as bp

__all__ = [
    "VoltageJump",
]

class VoltageJump(bp.TwoEndConn):
    target_backend = ['numpy', 'numba', 'numba-parallel', 'numba-cuda']

    def __init__(self, pre, post, conn,
        weight = 1., delay = 0., **kwargs
    ):
        # init params
        self.weight = weight
        self.delay = delay

        # init connections
        self.conn = conn(pre.size, post.size)
        self.pre_ids, self.post_ids = self.conn.requires("pre_ids", "post_ids")
        self.size = len(self.pre_ids)

        # init vars
        self.Isyn = self.register_constant_delay("Isyn",
            size = self.size,
            delay_time = self.delay
        )

        # init super
        super(VoltageJump, self).__init__(pre = pre, post = post, **kwargs)

    def update(self, _t):
        # set post.V
        for i in range(self.size):
            pre_id, post_id = self.pre_ids[i], self.post_ids[i]
            self.Isyn.push(i,
                self.pre.spike[pre_id] * self.weight
            )
            if not self.post.refractory[post_id]:
                self.post.V[post_id] += self.Isyn.pull(i)

