import subprocess
import sys
from datetime import datetime
from pathlib import Path


class PerformanceRunner:
    def __init__(self):
        self.report_base_dir = Path("reports/performance")
        self.report_base_dir.mkdir(parents=True, exist_ok=True)

    def run_test(self, test_config):
        # 创建测试目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.report_base_dir / timestamp
        report_dir.mkdir(parents=True, exist_ok=True)

        # 生成Locustfile
        locustfile = self.generate_locustfile(test_config, report_dir)

        # 运行Locust测试
        results = self.run_locust(locustfile, test_config, report_dir)

        return {
            "report_path": str(report_dir),
            "results": results
        }

    def generate_locustfile(self, test_config, report_dir):
        locustfile = report_dir / "locustfile.py"

        # 简化版的Locustfile模板
        locust_content = """
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def hello_world(self):
        self.client.get("/")
"""

        with open(locustfile, 'w') as f:
            f.write(locust_content)

        return locustfile

    def run_locust(self, locustfile, test_config, report_dir):
        # 运行Locust
        cmd = [
            "locust",
            "-f", str(locustfile),
            "--headless",
            "--users", str(test_config.get("users", 10)),
            "--spawn-rate", str(test_config.get("spawn_rate", 2)),
            "--run-time", str(test_config.get("run_time", "1m")),
            "--html", str(report_dir / "report.html")
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }