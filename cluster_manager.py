import sys
import json
import redis

from scheduler import SoSpiderSchdulerBase


class SoClusterManager(SoSpiderSchdulerBase):

    def __init__(self, name):
        self.load_conf()
        self.make_connection()
        self.name = name

    def run(self):
        print('ClusterManger has running as %s' % self.name)


if __name__ == '__main__':
    name = sys.argv[1]
    manager = SoClusterManager(name)
    manager.run()
