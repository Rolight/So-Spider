import json
import redis
import subprocess

class SoSpiderSchduler(object):

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

    def run_spider(self, params):

    def get_task(self):
        task_data = self.redis_cache.blpop(self.queue_key, timeout=0)
        return task_data

    def __init__(self):
        self.load_conf()
        self.make_connection()
        for attr, values in self.conf['mq'].items():
            setattr(self, attr, values)

    def run(self):
        while True:
            task_data = self.get_task()
            task_args = [
                "scrapy", "crawl",
                "generic_spider", "-a", "config=%s"+task_data
            ]
            p = subprocess.Popen(
                task_args,
                stdin=


params = {
    "index": "rolight-sample",
    "allowed_domains": ["spidertest-app.smartgslb.com"],
    "start_urls": ["http://spidertest-app.smartgslb.com"],
    "sleep": 1,
    "parse_url_rules": [
        r"http://spidertest-app.smartgslb.com/\d{4}/\d{2}/\d{2}/.*",
    ],
}

params = json.dumps(params)

