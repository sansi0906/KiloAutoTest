"""
深入探索codefield元素的结构和交互方式
"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 登录
        await page.goto(LOGIN_URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.fill('input[placeholder="账号"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button:has-text("登 录")')
        await page.wait_for_timeout(2000)

        # 进入服务项目配置并打开新增表单
        await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.click('button:has-text("新增服务项目")')
        await page.wait_for_timeout(1500)

        # 深入分析codefield元素
        print("=" * 60)
        print("分析codefield元素")
        print("=" * 60)
        
        # 获取第一个可见的codefield元素详情
        element_info = await page.evaluate("""
            () => {
                const inp = document.querySelector('.ant-modal input.ant-input[codefield]');
                if (!inp) return null;
                
                // 触发focus事件
                inp.focus();
                
                return {
                    tagName: inp.tagName,
                    type: inp.type,
                    placeholder: inp.placeholder,
                    className: inp.className,
                    id: inp.id,
                    attributes: Array.from(inp.attributes).map(a => ({ name: a.name, value: a.value })),
                    parentHTML: inp.parentElement ? inp.parentElement.outerHTML.substring(0, 300) : null,
                    formValues: inp.getAttribute('formvalues'),
                };
            }
        """)
        
        print(f"\n第一个codefield元素信息:")
        if element_info:
            for key, value in element_info.items():
                if key != 'parentHTML':
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}:\n    {value}")

        # 尝试设置value并检查是否能工作
        print("\n尝试设置codefield的值...")
        set_result = await page.evaluate("""
            () => {
                const inp = document.querySelector('.ant-modal input.ant-input[codefield]');
                if (!inp) return 'not_found';
                
                // 方法1: 直接设置value
                inp.value = '测试值';
                inp.dispatchEvent(new Event('input', {bubbles: true}));
                inp.dispatchEvent(new Event('change', {bubbles: true}));
                
                return {
                    value_after_set: inp.value,
                    formvalues_after: inp.getAttribute('formvalues'),
                };
            }
        """)
        print(f"  设置结果: {set_result}")
        
        # 截图看看效果
        await page.screenshot(path="codefield_test.png")
        print("  截图: codefield_test.png")
        
        # 检查有多少个可见的codefield input
        visible_count = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('.ant-modal input.ant-input[codefield]');
                const visible = [];
                for (const inp of all) {
                    if (inp.offsetParent !== null) {
                        visible.push({
                            id: inp.id,
                            placeholder: inp.placeholder,
                            value: inp.value,
                            rect: inp.getBoundingClientRect()
                        });
                    }
                }
                return visible;
            }
        """)
        print(f"\n可见的codefield元素 ({len(visible_count)}个):")
        for v in visible_count:
            print(f"  id={v['id']}, placeholder='{v['placeholder']}', value='{v['value']}'")
        
        # 关闭弹窗
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # 检查合同服务配置
        print("\n" + "=" * 60)
        print("分析合同服务配置")
        print("=" * 60)
        
        await page.goto(f"{BASE_URL}/smart-service/contract-service", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.click('button:has-text("新增合同服务")')
        await page.wait_for_timeout(1500)
        
        # 分析表单结构
        form_analysis = await page.evaluate("""
            () => {
                const modal = document.querySelector('.ant-modal');
                if (!modal) return null;
                
                const analysis = {
                    inputs: [],
                    textareas: [],
                    selects: [],
                    editors: [],
                };
                
                // 分析所有input
                const inputs = modal.querySelectorAll('input');
                for (const inp of inputs) {
                    if (inp.offsetParent !== null) {
                        analysis.inputs.push({
                            type: inp.type,
                            placeholder: inp.placeholder,
                            codefield: inp.hasAttribute('codefield'),
                            id: inp.id,
                            className: inp.className.substring(0, 50),
                        });
                    }
                }
                
                // 分析所有textarea
                const textareas = modal.querySelectorAll('textarea');
                for (const ta of textareas) {
                    if (ta.offsetParent !== null) {
                        analysis.textareas.push({
                            placeholder: ta.placeholder,
                            id: ta.id,
                        });
                    }
                }
                
                // 分析所有select
                const selects = modal.querySelectorAll('.ant-select-selector');
                for (const sel of selects) {
                    if (sel.offsetParent !== null) {
                        const placeholder = sel.querySelector('.ant-select-selection-placeholder');
                        analysis.selects.push({
                            placeholder: placeholder ? placeholder.textContent.trim() : '',
                        });
                    }
                }
                
                // 分析所有编辑器
                const editors = modal.querySelectorAll('[contenteditable="true"]');
                for (const ed of editors) {
                    if (ed.offsetParent !== null) {
                        analysis.editors.push({
                            tagName: ed.tagName,
                            className: ed.className.substring(0, 50),
                        });
                    }
                }
                
                return analysis;
            }
        """)
        
        print(f"\n表单结构:")
        if form_analysis:
            print(f"  inputs: {len(form_analysis['inputs'])}")
            for inp in form_analysis['inputs']:
                print(f"    - {inp}")
            print(f"  textareas: {len(form_analysis['textareas'])}")
            for ta in form_analysis['textareas']:
                print(f"    - {ta}")
            print(f"  selects: {len(form_analysis['selects'])}")
            for sel in form_analysis['selects']:
                print(f"    - {sel}")
            print(f"  editors: {len(form_analysis['editors'])}")
            for ed in form_analysis['editors']:
                print(f"    - {ed}")
        
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
