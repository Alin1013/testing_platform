import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from httprunner import HttpRunner, Config, Step, RunRequest


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

        # 运行测试
        allure_results_dir = report_dir / "allure-results"
        allure_results_dir.mkdir(exist_ok=True)

        # 运行HttpRunner测试
        cmd = [
            sys.executable, "-m", "httprunner", "run",
            str(test_file),
            "--allure", str(allure_results_dir)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # 生成allure报告
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
        test_file = report_dir / "test_api_testcases.py"

        # 生成HttpRunner格式的测试用例
        test_content = """
from httprunner import HttpRunner, Config, Step, RunRequest, RunTestCase

"""
        for i, case in enumerate(test_cases):
            test_content += f"""
class TestCase{case.id}(HttpRunner):
    config = (
        Config("{case.case_name}")
        .base_url("{case.base_url}")
        .export(*[])
    )

    teststeps = [
        Step(
            RunRequest("{case.case_name}")
            .{case.method.lower()}("{case.path}")
"""
            # 添加请求头
            if case.headers:
                headers_str = json.dumps(case.headers, ensure_ascii=False, indent=4)
                test_content += f"""            .headers({headers_str})
"""
            # 添加请求参数
            if case.params:
                params_str = json.dumps(case.params, ensure_ascii=False, indent=4)
                test_content += f"""            .params({params_str})
"""
            # 添加请求体
            if case.body:
                body_str = json.dumps(case.body, ensure_ascii=False, indent=4)
                test_content += f"""            .json({body_str})
"""
            # 添加响应提取
            if case.extract:
                for extract in case.extract:
                    test_content += f"""            .extract()
            .with_jmespath("{extract.jsonpath}", name="{extract.key}")
"""
            # 添加断言
            if case.validate:
                for validate in case.validate:
                    comparator_map = {
                        "eq": "equal_to",
                        "ne": "not_equal_to",
                        "lt": "less_than",
                        "gt": "greater_than",
                        "contains": "contains"
                    }
                    comparator = comparator_map.get(validate.comparator, "equal_to")
                    test_content += f"""            .validate()
            .assert_{comparator}("{validate.check}", {json.dumps(validate.expected)}, "{validate.check} {validate.comparator} {validate.expected}")
"""
            test_content += """        )
    ]

"""

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        return test_file