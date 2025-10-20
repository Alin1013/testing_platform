import pytest
import allure
import asyncio
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from playwright.async_api import async_playwright
import os


class UITestRunner:
    def __init__(self):
        self.report_base_dir = Path("reports/ui")
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
        test_file = report_dir / "test_ui.py"
        test_content = """
import pytest
import allure
import asyncio
from playwright.async_api import async_playwright
import os

"""

        for i, case in enumerate(test_cases):
            test_content += f"""
@allure.feature('UI Tests')
@allure.story('{case.case_name}')
async def test_case_{i}():
    \"\"\"Test case: {case.case_name}\"\"\"
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 创建截图目录
            screenshot_dir = "{report_dir / 'screenshots'}"
            os.makedirs(screenshot_dir, exist_ok=True)

            # 开始录制
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)

            # 动态执行UI脚本
            {self.wrap_script_content(case.script_content, case.case_name, screenshot_dir)}

            # 停止录制并保存
            await context.tracing.stop(path="{report_dir / f'trace_{i}.zip'}")

        except Exception as e:
            # 出错时截图
            await page.screenshot(path='{report_dir / f"screenshot_error_{i}.png"}')
            raise e
        finally:
            await browser.close()

"""

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        return test_file

    def wrap_script_content(self, script_content, case_name, screenshot_dir):
        """包装脚本内容，添加错误处理和截图功能"""
        wrapped_script = f"""
            # 脚本开始执行
            try:
                {script_content}

                # 成功时截图
                await page.screenshot(path='{screenshot_dir}/{case_name}_success.png')

            except Exception as e:
                # 失败时截图
                await page.screenshot(path='{screenshot_dir}/{case_name}_failure.png')
                raise e
        """
        return wrapped_script