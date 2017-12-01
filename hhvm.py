import requests
import time

from checks import AgentCheck
from hashlib import md5

class HHVMCheck(AgentCheck):
    def check(self, instance):
        if 'url' not in instance:
            self.log.info("skipping instance {} no url found", instance)
            return

        url = instance['url']

        # Just the url wouldn't work as it's likely to be localhost
        aggregation_key = md5(url + self.hostname).hexdigest()

        # Defines the auth to add to the end of the URL if needed 
        if instance['password']:
            auth = "?auth={}".format(instance['password'])
        else:
            auth = ""

        mem_url=  "{}/memory.json{}".format(url, auth)
        try:
            r = requests.get(mem_url)
        except requests.exceptions.Timeout as e:
            raise Exception("Timeout when connecting to {}".format(mem_url))

        if r.status_code != 200:
            raise Exception("Invalid response from {}, might be a auth issue, code {}".format(mem_url, r.status_code))

        resp = r.json()

        if resp["Success"] != 1:
            self.failure_event(resp["Success"], aggregation_key)
            return

        # Return all the metric in the json as gauges
        self.gauge("hhvm.memory.breakdown.unknown", resp["Memory"]["Breakdown"]["Unknown"])
        self.gauge("hhvm.memory.breakdown.code", resp["Memory"]["Breakdown"]["Code"]["Details"]["Bytes"])
        self.gauge("hhvm.memory.breakdown.tc_jit.bytes", resp["Memory"]["Breakdown"]["TC/Jit"]["Bytes"])
        self.gauge("hhvm.memory.breakdown.tc_jit.total_used", resp["Memory"]["Breakdown"]["TC/Jit"]["Details"]["Total Used"])
        self.gauge("hhvm.memory.breakdown.tc_jit.total_capacity", resp["Memory"]["Breakdown"]["TC/Jit"]["Details"]["Total Capacity"])
        for name in ["code.main", "code.hot", "code.cold", "code.frozen", "code.prof", "data"]:
            self.gauge("hhvm.memory.breakdown.tc_jit.{}.used".format(name), resp["Memory"]["Breakdown"]["TC/Jit"]["Details"][name]["Used"])
            self.gauge("hhvm.memory.breakdown.tc_jit.{}.capacity".format(name), resp["Memory"]["Breakdown"]["TC/Jit"]["Details"][name]["Capacity"])
        self.gauge("hhvm.memory.breakdown.static_string.bytes", resp["Memory"]["Breakdown"]["Static Strings"]["Bytes"])
        self.gauge("hhvm.memory.breakdown.static_string.count", resp["Memory"]["Breakdown"]["Static Strings"]["Details"]["Count"])
        self.gauge("hhvm.memory.process_stats.shared", resp["Memory"]["Process Stats (bytes)"]["Shared"])
        self.gauge("hhvm.memory.process_stats.vmsize", resp["Memory"]["Process Stats (bytes)"]["VmSize"])
        self.gauge("hhvm.memory.process_stats.vmrss", resp["Memory"]["Process Stats (bytes)"]["VmRss"])
        self.gauge("hhvm.memory.process_stats.data", resp["Memory"]["Process Stats (bytes)"]["Data"])
        self.gauge("hhvm.memory.process_stats.text", resp["Memory"]["Process Stats (bytes)"]["Text(Code)"])


        health_url=  "{}/check-health{}".format(url, auth)
        try:
            r = requests.get(health_url)
        except requests.exceptions.Timeout as e:
            raise Exception("Timeout when connecting to {}".format(health_url))

        if r.status_code != 200:
            raise Exception("Invalid response from {}, might be a auth issue, code {}".format(health_url, r.status_code))

        resp = r.json()

        self.gauge("hhvm.load", resp["load"])
        self.gauge("hhvm.queued", resp["queued"])
        self.gauge("hhvm.hhbc-roarena-capac", resp["hhbc-roarena-capac"])
        self.gauge("hhvm.tc-hotsize", resp["tc-hotsize"])
        self.gauge("hhvm.tc-coldsize", resp["tc-coldsize"])
        self.gauge("hhvm.tc-frozensize", resp["tc-frozensize"])
        self.gauge("hhvm.rds", resp["rds"])
        self.gauge("hhvm.rds-local", resp["rds-local"])
        self.gauge("hhvm.rds-persistent", resp["rds-persistent"])
        self.gauge("hhvm.catch-traces", resp["catch-traces"])
        self.gauge("hhvm.fixups", resp["fixups"])
        self.gauge("hhvm.units", resp["units"])
        self.gauge("hhvm.funcs", resp["funcs"])
        self.gauge("hhvm.request-count", resp["request-count"])
        self.gauge("hhvm.single-jit-requests", resp["single-jit-requests"])
        self.gauge("hhvm.prof-funcs", resp["prof-funcs"])
        self.gauge("hhvm.prof-bc", resp["prof-bc"])
        self.gauge("hhvm.opt-funcs", resp["opt-funcs"])

        stats_url = "{}/status.json".format(url, auth)
        try:
           r = requests.get(stats_url)
        except requests.exceptions.Timeout as e:
            raise Exception("Timeout connecting to {}".format(stats_url))

        if r.status_code != 200:
            raise Exception("Invalid response from {}, might be a auth issue, code {}".format(stats_url, r.status_code))

        resp = r.json()
        modes = {}
        ioduration = 0
        io_on = 0
        threads = resp["status"]["threads"]

        for thread in threads:
            if not thread["mode"] in modes:
                modes[thread["mode"]] = 1
            else:
                modes[thread["mode"]] += 1
            if thread["mode"] != "idle":
                if thread["io"] == 1:
                    io_on += 1
                    ioduration += thread["ioduration"]
                    self.histogram("hhvm.thread.io.duration", thread["ioduration"])
            else:
                self.gauge("hhvm.thread.io.idle", 1)


        for mode in modes:
            print mode
            metric = "hhvm.thread.mode.{}".format(mode)
            self.gauge(metric, modes[mode])
        # this is dump
        ioduration = ioduration / 1000.0
        self.count("hhvm.thread.io",  io_on)
        self.histogram("hhvm.thread.io.total.duration",  ioduration)


    def failure_event(self, code, aggregation_key):
        self.event({
            'timestamp' : int(time.time()),
            'event_type': 'hhvm_status',
            'msg_title': 'Non success return for hhvm instance',
            'msg_text': 'Returned a success code of {}'.format(code),
            'aggregation_key': aggregation_key,
        })
