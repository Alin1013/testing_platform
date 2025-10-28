import requests
import pytest
import allure
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from typing import List, Dict, Any
import time


class APITestRunner:
    def __init__(self):
        self.report_base_dir = Path("reports/api")
        self.report_base_dir.mkdir(parents=True, exist_ok=True)

    def run_tests(self, test_cases: List[Any]) -> Dict[str, Any]:
        """运行API测试用例"""
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
            "--tb=short",
            "-v"
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
            "stderr": result.stderr,
            "timestamp": timestamp
        }

    def generate_test_file(self, test_cases: List[Any], report_dir: Path) -> Path:
        """生成 pytest 测试文件"""
        test_file = report_dir / "test_api.py"

        test_content = '''
import pytest
import requests
import allure
import json
from typing import Dict, Any

'''

        for i, case in enumerate(test_cases):
            test_content += f'''
@allure.feature('API Tests')
@allure.story('{case.case_name}')
def test_case_{i}():
    """Test case: {case.case_name}"""
    with allure.step('Send {case.method} request to {case.url}'):
        # 准备请求参数
        headers = {case.headers or {} }
        params = {case.params or {} }
        json_data = {case.body or {} }

        # 发送请求
        response = requests.request(
            method='{case.method}',
            url='{case.url}',
            headers=headers,
            params=params,
            json=json_data,
            timeout=30
        )

    with allure.step('Verify response status code'):
        # 基本的HTTP状态码检查
        assert response.status_code in [200, 201, 202], f"Expected success status code, got {{response.status_code}}"

    with allure.step('Verify response data'):
        actual_data = response.json() if response.content else {{}}
        expected_data = {case.expected_data or {} }

        # 验证期望的数据
        if expected_data:
            for key, expected_value in expected_data.items():
                assert key in actual_data, f"Key '{{key}}' not found in response"
                assert actual_data[key] == expected_value, f"Value mismatch for key '{{key}}': expected {{expected_value}}, got {{actual_data[key]}}"

    with allure.step('Log response details'):
        allure.attach(json.dumps(actual_data, indent=2, ensure_ascii=False), 
                     name='Response Body', 
                     attachment_type=allure.attachment_type.JSON)
        allure.attach(str(response.headers), 
                     name='Response Headers', 
                     attachment_type=allure.attachment_type.TEXT)

'''

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        return test_file