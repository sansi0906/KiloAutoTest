"""
探索所有新增表单的结构
先打开每个新增界面，获取所有输入框、选择框、按钮等信息
"""
import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


async def explore_form(page, page_name, button_text):
    """打开新增表单并探索结构"""
    print(f"\n{'='*60}")
    print(f"探索: {page_name}")
    print(f"{'='*60}")

    # 点击新增按钮
    try:
        await page.click(f'button:has-text("{button_text}")')
        await page.wait_for_timeout(1500)
    except Exception as e:
        print(f"  ❌ 点击失败: {e}")
        return None

    # 截图
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"explore_{page_name}_{TIMESTAMP}.png"))

    # 获取表单完整结构
    form_info = await page.evaluate("""
        () => {
            const result = {
                pageName: document.title,
                hasModal: !!document.querySelector('.ant-modal'),
                hasDrawer: !!document.querySelector('.ant-drawer'),
                formItems: [],
                allButtons: [],
                selects: [],
                editors: [],
                switches: [],
                radios: [],
                textareas: [],
            };

            // 获取所有表单项
            const formItems = document.querySelectorAll('.ant-form-item');
            for (let i = 0; i < formItems.length; i++) {
                const item = formItems[i];
                const label = item.querySelector('.ant-form-item-label label');
                const labelText = label ? label.textContent.trim() : '';
                const isRequired = label && label.textContent.includes('*');
                
                // 检查是否可见
                const isVisible = item.offsetParent !== null && item.style.display !== 'none';
                
                // 获取输入框信息
                const inputs = item.querySelectorAll('input');
                const inputInfo = [];
                for (const inp of inputs) {
                    inputInfo.push({
                        type: inp.type,
                        placeholder: inp.placeholder || '',
                        codefield: inp.hasAttribute('codefield'),
                        visible: inp.offsetParent !== null,
                        className: inp.className.substring(0, 50),
                    });
                }
                
                // 获取select信息
                const selects = item.querySelectorAll('.ant-select-selector');
                const selectInfo = [];
                for (const sel of selects) {
                    // 获取select的选项
                    const selectId = sel.getAttribute('aria-controls');
                    selectInfo.push({
                        placeholder: sel.querySelector('.ant-select-selection-placeholder')?.textContent?.trim() || '',
                        multiple: sel.className.includes('multiple'),
                    });
                }
                
                // 获取radio信息
                const radios = item.querySelectorAll('.ant-radio-wrapper');
                const radioInfo = [];
                for (const r of radios) {
                    radioInfo.push(r.textContent.trim());
                }
                
                // 获取switch信息
                const switches = item.querySelectorAll('.ant-switch');
                const switchInfo = [];
                for (const s of switches) {
                    switchInfo.push({
                        checked: s.classList.contains('ant-switch-checked'),
                    });
                }
                
                // 获取textarea
                const textareas = item.querySelectorAll('textarea');
                const textareaInfo = [];
                for (const t of textareas) {
                    textareaInfo.push({
                        placeholder: t.placeholder || '',
                        visible: t.offsetParent !== null,
                    });
                }
                
                // 获取富文本编辑器
                const editors = item.querySelectorAll('[contenteditable="true"], .ql-editor, .w-e-text');
                const editorInfo = [];
                for (const e of editors) {
                    editorInfo.push({
                        tagName: e.tagName,
                        className: e.className.substring(0, 50),
                    });
                }

                result.formItems.push({
                    index: i,
                    label: labelText,
                    labelVisible: isVisible,
                    required: isRequired,
                    inputs: inputInfo,
                    selects: selectInfo,
                    radios: radioInfo,
                    switches: switchInfo,
                    textareas: textareaInfo,
                    editors: editorInfo,
                });
            }

            // 获取弹窗内的所有按钮
            const modal = document.querySelector('.ant-modal, .ant-drawer');
            if (modal) {
                const buttons = modal.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent.trim();
                    if (text && text.length < 20) {
                        result.allButtons.push({
                            text: text,
                            disabled: btn.disabled,
                            className: btn.className.substring(0, 50),
                        });
                    }
                }
            }

            return result;
        }
    """)

    print(f"\n  页面标题: {form_info.get('pageName')}")
    print(f"  弹窗类型: {'Modal' if form_info.get('hasModal') else 'Drawer' if form_info.get('hasDrawer') else '无'}")
    print(f"\n  表单项数量: {len(form_info.get('formItems', []))}")
    
    for item in form_info.get('formItems', []):
        if not item.get('labelVisible'):
            continue  # 跳过隐藏的表单项
        
        print(f"\n  ┌─ 表单项 #{item['index']}")
        print(f"  │  标签: '{item['label']}' {'*必填' if item['required'] else ''}")
        
        if item['inputs']:
            print(f"  │  输入框:")
            for inp in item['inputs']:
                if inp['visible'] and not inp['codefield']:
                    print(f"  │    - type={inp['type']}, placeholder='{inp['placeholder']}'")
        
        if item['selects']:
            print(f"  │  下拉框:")
            for sel in item['selects']:
                print(f"  │    - placeholder='{sel['placeholder']}'")
        
        if item['radios']:
            print(f"  │  单选按钮: {item['radios']}")
        
        if item['switches']:
            print(f"  │  开关: {item['switches']}")
        
        if item['editors']:
            print(f"  │  富文本编辑器:")
            for ed in item['editors']:
                print(f"  │    - tag={ed['tagName']}, class='{ed['className']}'")
        
        if item['textareas']:
            print(f"  │  文本域: {item['textareas']}")
        
        print(f"  └─")

    if form_info.get('allButtons'):
        print(f"\n  弹窗按钮:")
        for btn in form_info['allButtons']:
            print(f"    - '{btn['text']}' {'(disabled)' if btn['disabled'] else ''}")

    # 关闭弹窗
    await page.click('.ant-modal-close, .ant-drawer-close')
    await page.wait_for_timeout(500)

    return form_info


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 登录
        print("登录系统...")
        await page.goto(LOGIN_URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.fill('input[placeholder="账号"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button:has-text("登 录")')
        await page.wait_for_timeout(2000)
        print("登录成功!")

        # 探索各个新增表单
        all_results = {}

        # 1. 服务项目配置
        print("\n\n" + "#" * 60)
        print("# 1. 服务项目配置")
        print("#" * 60)
        await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        result = await explore_form(page, "project_config", "新增服务项目")
        if result:
            all_results["project_config"] = result

        # 2. 合同服务配置
        print("\n\n" + "#" * 60)
        print("# 2. 合同服务配置")
        print("#" * 60)
        await page.goto(f"{BASE_URL}/smart-service/contract-service", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        result = await explore_form(page, "contract_service", "新增合同服务")
        if result:
            all_results["contract_service"] = result

        # 3. 经营范围配置
        print("\n\n" + "#" * 60)
        print("# 3. 经营范围配置")
        print("#" * 60)
        await page.goto(f"{BASE_URL}/smart-service/scope-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        result = await explore_form(page, "scope_config", "新增经营范围")
        if result:
            all_results["scope_config"] = result

        # 4. 知识库
        print("\n\n" + "#" * 60)
        print("# 4. 知识库")
        print("#" * 60)
        await page.goto(f"{BASE_URL}/content-manage/knowledge", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        result = await explore_form(page, "knowledge", "新增知识库")
        if result:
            all_results["knowledge"] = result

        # 保存结果
        result_path = os.path.join(SCREENSHOT_DIR, f"form_structure_{TIMESTAMP}.json")
        # 简化保存
        simplified = {}
        for key, value in all_results.items():
            simplified[key] = {
                "hasModal": value.get("hasModal"),
                "formItems": [],
                "allButtons": value.get("allButtons", []),
            }
            for item in value.get("formItems", []):
                if item.get("labelVisible"):
                    # 简化输入框信息
                    simple_inputs = []
                    for inp in item.get("inputs", []):
                        if inp.get("visible") and not inp.get("codefield"):
                            simple_inputs.append(inp)
                    
                    simplified[key]["formItems"].append({
                        "label": item["label"],
                        "required": item["required"],
                        "inputs": simple_inputs,
                        "selects": item.get("selects", []),
                        "radios": item.get("radios", []),
                        "switches": item.get("switches", []),
                        "editors": item.get("editors", []),
                        "textareas": item.get("textareas", []),
                    })

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(simplified, f, ensure_ascii=False, indent=2)

        print(f"\n\n结果已保存: {result_path}")
        print("\n" + "=" * 60)
        print("探索完成!")
        print("=" * 60)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
