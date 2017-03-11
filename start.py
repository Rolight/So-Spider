import json
import subprocess
import os

params = {
    "index": "rolight-sample",
    "elasticsearch_host": "localhost",
    "allowed_domains": ["spidertest-app.smartgslb.com"],
    "start_urls": ["http://spidertest-app.smartgslb.com"],
    "sleep": 1,
    "parse_url_rules": [
        r"http://spidertest-app.smartgslb.com/\d{4}/\d{2}/\d{2}/.*",
    ],
}

params = json.dumps(params)


subprocess.call(["scrapy", "crawl", "generic_spider", "-a", "config="+params])
