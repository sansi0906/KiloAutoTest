"""
演示修复后的测试用例: 服务项目配置 - 新增表单验证
修复: 正确检测表单验证错误提示
"""
import asyncio
import os
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


async def demo_fixed_test():
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
        print(f"  登录成功")

        # 2. 导航到服务项目配置页面
        print("\n步骤2: 导航到服务项目配置页面")
        await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        print(f"  已导航到: {page.url}")

        # 3. 点击"新增服务项目"按钮
        print("\n步骤3: 点击'新增服务项目'按钮")
        await page.click('button:has-text("新增服务项目")')
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_fixed_01_form.png"))
        print("  表单已打开")

        # 4. 检查表单字段
        print("\n步骤4: 检查表单字段")
        form_info = await page.evaluate("""
            () => {
                const result = {
                    fields: [],
                };

                // 获取所有表单项
                const formItems = document.querySelectorAll('.ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const labelText = label ? label.textContent.trim() : '';
                    const required = label && label.textContent.includes('*');
                    result.fields.push({
                        label: labelText,
                        required: required,
                    });
                }

                return result;
            }
        """)
        print(f"  表单字段: {form_info['fields']}")

        # 5. 提交空表单
        print("\n步骤5: 提交空表单（不填写任何字段）")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_fixed_02_before_submit.png"))

        # 点击确认按钮
        await page.click('button:has-text("确 认"), button:has-text("确认")')
        await page.wait_for_timeout(2000)  # 增加等待时间

        # 6. 检查验证错误（修复后的检测逻辑）
        print("\n步骤6: 检查表单验证错误")
        errors = await page.evaluate("""
            () => {
                const errors = [];

                // 方法1: 查找 .ant-form-item-explain-error 元素
                const errorElements = document.querySelectorAll('.ant-form-item-explain-error');
                for (const el of errorElements) {
                    const text = el.textContent.trim();
                    if (text) {
                        // 获取所属字段的标签
                        const formItem = el.closest('.ant-form-item');
                        const label = formItem ? formItem.querySelector('.ant-form-item-label label') : null;
                        const labelText = label ? label.textContent.trim() : '未知字段';
                        errors.push({
                            field: labelText,
                            message: text,
                            selector: '.ant-form-item-explain-error'
                        });
                    }
                }

                // 方法2: 检查 .ant-form-item-explain （可能包含错误）
                const explains = document.querySelectorAll('.ant-form-item-explain');
                for (const el of explains) {
                    // 检查是否有 error class
                    if (el.classList.contains('ant-form-item-explain-error')) continue;
                    const text = el.textContent.trim();
                    if (text) {
                        const formItem = el.closest('.ant-form-item');
                        const label = formItem ? formItem.querySelector('.ant-form-item-label label') : null;
                        const labelText = label ? label.textContent.trim() : '未知字段';
                        errors.push({
                            field: labelText,
                            message: text,
                            selector: '.ant-form-item-explain'
                        });
                    }
                }

                // 方法3: 查找所有包含错误信息的元素
                const allElements = document.querySelectorAll('[class*="error"], [class*="Error"]');
                for (const el of allElements) {
                    const text = el.textContent.trim();
                    if (text && text.includes('请输入')) {
                        errors.push({
                            field: '未知字段',
                            message: text,
                            selector: el.className
                        });
                    }
                }

                return errors;
            }
        """)

        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_fixed_03_after_submit.png"))

        if errors:
            print(f"  ✓ 发现 {len(errors)} 条验证错误:")
            for err in errors:
                print(f"    - [{err['field']}] {err['message']}")
        else:
            print(f"  ✗ 未发现验证错误")
            # 进一步检查
            print("\n  进一步检查DOM...")
            all_text_with_请 = await page.evaluate("""
                () => {
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null
                    );
                    const results = [];
                    let node;
                    while (node = walker.nextNode()) {
                        const text = node.textContent.trim();
                        if (text && text.includes('请输入')) {
                            const parent = node.parentElement;
                            results.push({
                                text: text.substring(0, 50),
                                parentClass: parent ? parent.className : '',
                                parentTag: parent ? parent.tagName : ''
                            });
                        }
                    }
                    return results;
                }
            """)
            print(f"  包含'请输入'的文本: {all_text_with_请}")

        # 7. 最终截图
        print("\n步骤7: 保存最终截图")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "demo_fixed_result.png"))

        print("\n" + "=" * 60)
        print("测试结果:")
        print("=" * 60)
        if errors:
            print(f"  ✓ 测试通过! 表单验证正常工作")
            print(f"  ✓ 共发现 {len(errors)} 条必填项验证错误")
            for err in errors:
                print(f"    - 字段 '{err['field']}': {err['message']}")
        else:
            print(f"  ✗ 测试失败: 未检测到验证错误")

        # 关闭弹窗
        await page.click('.ant-modal-close, button:has-text("取 消")')
        await page.wait_for_timeout(500)

        await browser.close()
        print("\n演示完成!")


if __name__ == "__main__":
    asyncio.run(demo_fixed_test())
