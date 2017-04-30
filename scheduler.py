import json
import redis
import subprocess
import sys
import time
import threading
import requests


class SoSpiderSchdulerBase():

    def load_conf(self):
        with open('conf.json', 'r') as f:
            self.conf = json.loads(f.read())
        self.apg_host = self.conf['apg_host']

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

    def key_of_task_queue(self):
        return self.conf['task_queue_key']

    def key_of_task_log(self):
        return self.conf['log_key'].format(
            task_id=self.task_id)

    def key_of_task_command(self, command):
        return self.conf['task_command_key'].format(
            task_id=self.task_id,
            command=command)


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

    def set_idle(self):
        self.status = 'idle'
        self.website_id = 0
        self.task_id = 0
        self.register()

    def wait_for_task(self):
        print('watting for task')
        key = self.key_of_task_queue()
        task = self.redis_cache.blpop(key, timeout=0)
        task = json.loads(str(task[1]))
        print('get a task %s' % task)
        return task

    def collect_log(self, process):
        log_key = self.key_of_task_log()
        while process.poll() is None:
            log = process.stdout.readline()
            if log.strip():
                self.redis_cache.rpush(log_key, log)
            time.sleep(0.05)
        logs = process.stdout.readlines()
        # push remind logs
        if logs:
            self.redis_cache.rpush(log_key, *logs)
        self.mannual_log(
            'task finished with return_code %s' %
            process.poll())
        self.sync_log()

    def mannual_log(self, log):
        log_key = self.key_of_task_log()
        self.redis_cache.rpush(log_key, log)

    def sync_log(self):
        url = self.apg_host + 'spidertasks/{task_id}/sync/'.format(
            task_id=self.task_id)
        try:
            response = requests.put(url, data={'spider': self.name})
            print('sync log with response %s' % response.text)
        except Exception as e:
            print(e)

    # set status to finish
    def sync_status(self):
        url = self.apg_host + 'spidertasks/{task_id}/'.format(
            task_id=self.task_id)
        try:
            response = requests.put(url, data={'status': 1})
            print('sync status with response %s' % response.text)
        except Exception as e:
            print(e)

    def run_task(self, task):
        self.status = 'running'
        self.website_id = task['website_id']
        self.task_id = task['task_id']
        self.register()

        # start subprocess to run the spider
        # process = subprocess.Popen(
        #     ['scrapy', 'crawl', 'generic_spider', '-a',
        #      'config=%s' % json.dumps(task)],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE
        # )
        process = subprocess.Popen(
            ['ping', 'www.baidu.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # run the log thread to collect log
        log_thread = threading.Thread(
            target=self.collect_log,
            args=(process, )
        )
        log_thread.start()

        while True:
            # check if the process still running
            return_code = process.poll()
            if return_code is not None:
                self.sync_status()
                break
            # checkif has command
            command = 'stop'
            command_key = self.key_of_task_command(command)
            num_commands = self.redis_cache.getset(
                command_key, 0)
            if num_commands is not None and int(num_commands) > 0:
                process.kill()
                self.mannual_log('received stop command')
            time.sleep(3)
            # sync through apg
            self.sync_log()

    def register(self):
        key = self.key_of_spider(self.name)
        self.redis_cache.set(key, json.dumps(self.data))
        print('Registered (%s) with data:\n%s' % (key, self.data))

    def run(self):
        print('Schduler has running as %s' % self.name)
        self.register()
        subprocess.Popen(['python', 'cluster_manager.py', self.name],
                         stdout=subprocess.PIPE)
        print('cluster manager run success')
        while True:
            self.set_idle()
            task = self.wait_for_task()
            self.run_task(task)
            time.sleep(5)


if __name__ == '__main__':
    name = sys.argv[1]
    schduler = SoSpiderSchduler(name)
    schduler.run()
