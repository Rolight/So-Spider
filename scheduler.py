import json
import redis
import subprocess
import sys
import time


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

    def key_of_spider_cluster(self):
        return self.conf['spiders_key']

    def key_of_spider(self, spider_name):
        return self.conf['spider_key'].format(
            spider_name=spider_name)


class SoSpiderSchduler(SoSpiderSchdulerBase):

    def __init__(self, name):
        self.serializer_fields = ['name', 'status', 'website_id', 'task_id']
        self.name = name
        self.status = 'idle'
        self.website_id = 0
        self.task_id = 0
        self.load_conf()
        self.make_connection()

    @property
    def data(self):
        return {field: getattr(self, field)
                for field in self.serializer_fields}

    def register(self):
        key = self.key_of_spider(self.name)
        self.redis_cache.set(key, self.data)

    def run(self):
        print('Schduler has running as %s' % self.name)
        self.register()
        subprocess.Popen(['python', 'cluster_manager.py', self.name])
        print('cluster manager run success')
        while True:
            time.sleep(5)


if __name__ == '__main__':
    name = sys.argv[1]
    schduler = SoSpiderSchduler(name)
    schduler.run()
