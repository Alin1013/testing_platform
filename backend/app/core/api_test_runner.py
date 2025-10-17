import requests
import pytest
import allure
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys


class APITestRunner:
    def __init__(self):
        self.report_base_dir = Path("reports/api")
        self.report_base_dir.mkdir(parents=True, exist_ok=True)

    def run_tests(self, test_cases):
        # 创建测试目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.report_base_dir / timestamp
        report_dir.mkdir(parents=True, exist_ok=True)

        # 生成测试文件
        test_file = self.generate_test_file(test_cases, report_dir)

        # 运行 pytest 测试
        allure_results_dir = report_dir / "allure-results"
        allure_results_dir.mkdir(exist_ok=True)

        # 运行测试
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            f"--alluredir={allure_results_dir}",
            "--tb=short"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # 生成 allure 报告
        allure_report_dir = report_dir / "allure-report"
        subprocess.run([
            "allure", "generate",
            str(allure_results_dir),
            "-o", str(allure_report_dir),
            "--clean"
        ])

        return {
            "report_path": str(allure_report_dir),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    def generate_test_file(self, test_cases, report_dir):
        test_file = report_dir / "test_api.py"

        test_content = """
import pytest
import requests
import allure

"""

        for i, case in enumerate(test_cases):
            test_content += f"""
@allure.feature('API Tests')
@allure.story('{case.case_name}')
def test_case_{i}():
    \"\"\"Test case: {case.case_name}\"\"\"
    with allure.step('Send {case.method} request to {case.url}'):
        response = requests.request(
            method='{case.method}',
            url='{case.url}',
            headers={case.headers or {} },
            params={case.params or {} },
            json={case.body or {} }
        )

    with allure.step('Verify response status code'):
        assert response.status_code == 200

    with allure.step('Verify response data'):
        actual_data = response.json()
        expected_data = {case.expected_data or {} }
        # 这里可以添加更复杂的断言逻辑
        if expected_data:
            for key, value in expected_data.items():
                assert key in actual_data
                assert actual_data[key] == value

"""

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        return test_file