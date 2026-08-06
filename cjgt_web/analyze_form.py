"""
调查服务项目新增表单的完整结构
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

        # 进入服务项目配置
        await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.click('button:has-text("新增服务项目")')
        await page.wait_for_timeout(2000)

        print("=" * 60)
        print("服务项目新增表单 - 结构分析")
        print("=" * 60)
        
        # 获取所有表单元素
        structure = await page.evaluate("""
            () => {
                const result = {
                    formItems: [],
                    inputs: [],
                    textareas: [],
                    editors: [],
                    radios: [],
                    selects: [],
                    buttons: [],
                };
                
                // 所有表单项
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const control = item.querySelector('.ant-form-item-control');
                    
                    // 检查类型
                    let type = 'unknown';
                    if (control) {
                        if (control.querySelector('input[type="radio"]') || control.querySelector('.ant-radio')) {
                            type = 'radio';
                        } else if (control.querySelector('input[codefield]') || control.querySelector('.ant-input')) {
                            type = 'input';
                        } else if (control.querySelector('textarea')) {
                            type = 'textarea';
                        } else if (control.querySelector('.ant-select')) {
                            type = 'select';
                        } else if (control.querySelector('[contenteditable="true"]')) {
                            type = 'editor';
                        }
                    }
                    
                    result.formItems.push({
                        label: label ? label.textContent.trim() : '无标签',
                        type: type,
                    });
                }
                
                // 所有inputs
                const inputs = document.querySelectorAll('.ant-modal input');
                for (const inp of inputs) {
                    result.inputs.push({
                        id: inp.id,
                        type: inp.type,
                        placeholder: inp.placeholder,
                        visible: inp.offsetParent !== null,
                        codefield: inp.getAttribute('codefield'),
                    });
                }
                
                // 所有textareas
                const textareas = document.querySelectorAll('.ant-modal textarea');
                for (const ta of textareas) {
                    result.textareas.push({
                        id: ta.id,
                        visible: ta.offsetParent !== null,
                        ariaHidden: ta.getAttribute('aria-hidden'),
                    });
                }
                
                // 所有contenteditable
                const editors = document.querySelectorAll('.ant-modal [contenteditable="true"]');
                for (const ed of editors) {
                    result.editors.push({
                        tag: ed.tagName,
                        id: ed.id,
                        visible: ed.offsetParent !== null,
                    });
                }
                
                // 所有radio
                const radios = document.querySelectorAll('.ant-modal .ant-radio');
                for (const r of radios) {
                    const input = r.querySelector('input');
                    const span = r.querySelector('.ant-radio-inner');
                    radios_info = result.radios;
                    // 按组收集
                    let group = 'unknown';
                    const formItem = r.closest('.ant-form-item');
                    if (formItem) {
                        const label = formItem.querySelector('.ant-form-item-label label');
                        if (label) group = label.textContent.trim();
                    }
                    
                    // 查找radio的文本
                    let radioText = '';
                    const labelEl = r.closest('label');
                    if (labelEl) {
                        radioText = labelEl.textContent.trim();
                    }
                    
                    radios_info.push({
                        group: group,
                        text: radioText,
                        checked: r.classList.contains('ant-radio-checked'),
                    });
                }
                
                return result;
            }
        """)
        
        print("\n【表单项】")
        for item in structure['formItems']:
            print(f"  - {item['label']}: {item['type']}")
        
        print("\n【Inputs】")
        for inp in structure['inputs']:
            print(f"  - id={inp['id']}, type={inp['type']}, placeholder={inp['placeholder']}, visible={inp['visible']}, codefield={inp['codefield']}")
        
        print("\n【Textareas】")
        for ta in structure['textareas']:
            print(f"  - id={ta['id']}, visible={ta['visible']}, ariaHidden={ta['ariaHidden']}")
        
        print("\n【ContentEditable】")
        for ed in structure['editors']:
            print(f"  - tag={ed['tag']}, id={ed['id']}, visible={ed['visible']}")
        
        print("\n【Radios】")
        # 按组显示
        radio_groups = {}
        for r in structure['radios']:
            if r['group'] not in radio_groups:
                radio_groups[r['group']] = []
            radio_groups[r['group']].append(f"{r['text']}({'✓' if r['checked'] else '○'})")
        
        for group, radios in radio_groups.items():
            print(f"  - {group}: {', '.join(radios)}")
        
        await page.screenshot(path="form_structure.png")
        print("\n截图: form_structure.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
