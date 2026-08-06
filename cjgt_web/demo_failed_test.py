"""
演示失败的测试用例: 服务项目配置 - 新增表单验证
问题: 空表单提交时未显示验证错误
"""
import asyncio
import os
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


async def demo_failed_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 1. 登录
        print("步骤1: 登录系统")
        await page.goto(LOGIN_URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.fill('input[placeholder="账号"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button:has-text("登 录")')
        await page.wait_for_timeout(2500)
        print(f"  登录成功，URL: {page.url}")

        # 2. 导航到服务项目配置页面
        print("\n步骤2: 导航到服务项目配置页面")
        await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_01_project_config.png"))
        print(f"  已导航到: {page.url}")

        # 3. 点击"新增服务项目"按钮
        print("\n步骤3: 点击'新增服务项目'按钮")
        add_btn = page.locator('button:has-text("新增服务项目")').first
        await add_btn.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_02_add_form.png"))

        # 4. 检查表单结构
        print("\n步骤4: 检查表单结构")
        # 查找抽屉或弹窗
        drawer = page.locator('.ant-drawer').first
        modal = page.locator('.ant-modal').first

        if await drawer.count() > 0:
            print("  表单类型: Drawer (抽屉)")
        elif await modal.count() > 0:
            print("  表单类型: Modal (弹窗)")
        else:
            print("  表单类型: 未知")

        # 获取表单字段
        form_info = await page.evaluate("""
            () => {
                const result = {
                    labels: [],
                    inputs: [],
                    submit_buttons: [],
                };

                // 获取表单标签
                const labels = document.querySelectorAll('.ant-form-item-label label, .ant-form-item label');
                for (const l of labels) {
                    const text = l.textContent.trim();
                    if (text) result.labels.push(text);
                }

                // 获取所有输入框
                const inputs = document.querySelectorAll('.ant-form-item input, .ant-form-item textarea, .ant-form-item .ant-select-selector');
                for (const inp of inputs) {
                    const placeholder = inp.getAttribute('placeholder') || '';
                    const type = inp.tagName.toLowerCase();
                    result.inputs.push({ type, placeholder });
                }

                // 获取提交按钮
                const buttons = document.querySelectorAll('.ant-drawer button, .ant-modal button');
                for (const btn of buttons) {
                    const text = btn.textContent.trim();
                    if (text && (text.includes('确定') || text.includes('保存') || text.includes('提交') || text.includes('确认'))) {
                        result.submit_buttons.push(text);
                    }
                }

                return result;
            }
        """)
        print(f"  表单标签: {form_info['labels']}")
        print(f"  输入框数量: {len(form_info['inputs'])}")
        print(f"  提交按钮: {form_info['submit_buttons']}")

        # 5. 尝试提交空表单
        print("\n步骤5: 尝试提交空表单")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_03_before_submit.png"))

        # 查找并点击提交按钮
        submit_btn_text = form_info['submit_buttons'][0] if form_info['submit_buttons'] else None

        if submit_btn_text:
            submit_btn = page.locator(f'button:has-text("{submit_btn_text}")').first
            print(f"  点击提交按钮: {submit_btn_text}")
            await submit_btn.click()
            await page.wait_for_timeout(2000)
        else:
            # 尝试各种可能的按钮文本
            for btn_text in ["确定", "确 定", "保存", "提交", "确认"]:
                btn = page.locator(f'button:has-text("{btn_text}")').first
                if await btn.count() > 0:
                    print(f"  点击提交按钮: {btn_text}")
                    await btn.click()
                    await page.wait_for_timeout(2000)
                    break

        # 6. 检查是否有验证错误
        print("\n步骤6: 检查表单验证错误")
        errors = await page.evaluate("""
            () => {
                const selectors = [
                    '.ant-form-item-explain-error',
                    '.ant-form-explain',
                    '.ant-form-item-explain',
                    '[role="alert"]',
                    '.ant-message-error',
                ];
                const errors = [];
                for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        if (text) errors.push({ selector: sel, text });
                    }
                }
                return errors;
            }
        """)

        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_04_after_submit.png"))

        if errors:
            print(f"  ✓ 发现验证错误 ({len(errors)}条):")
            for err in errors:
                print(f"    - [{err['selector']}] {err['text']}")
        else:
            print(f"  ✗ 未发现任何验证错误!")
            print(f"  ✗ 这就是问题所在: 空表单提交后没有显示必填项的验证提示")

        # 7. 检查按钮状态（是否被禁用）
        print("\n步骤7: 检查提交按钮状态")
        button_state = await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('.ant-drawer button, .ant-modal button');
                const states = [];
                for (const btn of buttons) {
                    const text = btn.textContent.trim();
                    const disabled = btn.disabled || btn.classList.contains('ant-btn-disabled');
                    if (text && text.length < 10) {
                        states.push({ text, disabled });
                    }
                }
                return states;
            }
        """)
        print(f"  按钮状态: {button_state}")

        # 8. 截图保存
        print("\n步骤8: 保存演示截图")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_failed_test_result.png"))

        # 总结
        print("\n" + "=" * 60)
        print("测试失败原因分析")
        print("=" * 60)
        print(f"""
问题描述: 点击"新增服务项目"后，打开表单，在不填写任何字段的情况下
点击提交/确定按钮，预期应该显示必填项的验证错误提示。

实际结果: 提交后没有显示任何验证错误提示。

可能的原因:
1. 表单字段未配置必填项验证规则
2. 表单验证规则未正确绑定
3. 提交按钮的处理逻辑没有先验证表单
4. 验证错误样式类名可能不同

表单字段: {form_info['labels']}
        """)

        # 关闭抽屉
        close_btn = page.locator('.ant-drawer-close, .ant-modal-close').first
        if await close_btn.count() > 0:
            await close_btn.click()
            await page.wait_for_timeout(500)

        await browser.close()
        print("演示完成!")


if __name__ == "__main__":
    asyncio.run(demo_failed_test())
