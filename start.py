import json
import subprocess
import os

params = {
    u"website_id": 1,
    u"task_id": 1,
    u"index": u"rolight-sample",
    u"elasticsearch_host": u"localhost",
    u"allowed_domains": [u"spidertest-app.smartgslb.com"],
    u"start_urls": [u"http://spidertest-app.smartgslb.com"],
    u"sleep": 1,
    u"parse_url_rules": [
        r"http://spidertest-app.smartgslb.com/\d{4}/\d{2}/\d{2}/.*",
    ],
}

params = json.dumps(params)


subprocess.call(["scrapy", "crawl", "generic_spider", "-a", "config="+params])
