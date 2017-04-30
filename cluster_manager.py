import sys
import time

from scheduler import SoSpiderSchdulerBase


class SoClusterManager(SoSpiderSchdulerBase):

    def __init__(self, name):
        self.load_conf()
        self.make_connection()
        self.name = name
        self.log_file = open('./logs/%s_cluster.log' % self.name, 'w')

    def log(self, text):
        self.log_file.write(text + '\n')
        self.log_file.flush()

    def run(self):
        self.log('ClusterManger has running as %s' % self.name)
        while True:
            time.sleep(5)
            current_spider_key = self.key_of_spider(self.name)
            cluster_key = self.key_of_spider_cluster()

            self.redis_cache.expire(current_spider_key, 30)
            self.redis_cache.sadd(cluster_key, self.name)

            all_spiders = self.redis_cache.smembers(cluster_key)
            self.log('spiders supposed in cluster is %s' % all_spiders)

            living_spiders = [
                name for name in all_spiders
                if self.redis_cache.exists(self.key_of_spider(name))
            ]
            self.log('living spiders in cluster is %s' % living_spiders)
            if living_spiders:
                self.redis_cache.sadd(cluster_key, *living_spiders)
            for spider in all_spiders:
                if spider not in living_spiders:
                    self.redis_cache.srem(cluster_key, spider)


if __name__ == '__main__':
    name = sys.argv[1]
    manager = SoClusterManager(name)
    manager.run()
