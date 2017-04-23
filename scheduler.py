import json
import redis
import subprocess
import sys


class SoSpiderSchdulerBase(object):

    def load_conf(self):
        with open('conf.json', 'r') as f:
            self.conf = json.loads(f.read())

    def make_connection(self):
        redis_conf = self.conf['redis']
        self.redis_cache = redis.Redis(
            host=redis_conf['host'],
            port=redis_conf['port'],
            db=redis_conf['db'],
        )
        print('connect redis success')


class SoSpiderSchduler(SoSpiderSchdulerBase):

    def __init__(self, name):
        self.name = name

    def run(self):
        print('Schduler has running as %s' % self.name)
        subprocess.Popen(['python', 'cluster_manager.py', self.name])
        print('cluster manager run success')


if __name__ == '__main__':
    name = sys.argv[1]
    schduler = SoSpiderSchduler(name)
    schduler.run()
