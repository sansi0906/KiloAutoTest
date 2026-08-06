"""
监听服务项目表单提交的网络请求
"""
import asyncio
import json
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

        # 收集网络请求
        requests = []
        
        async def handle_request(request):
            if 'service' in request.url.lower() or 'project' in request.url.lower():
                post_data = request.post_data
                requests.append({
                    'url': request.url,
                    'method': request.method,
                    'post_data': post_data,
                })
                print(f"  📡 请求: {request.method} {request.url}")
                if post_data:
                    print(f"     数据: {post_data[:500]}")
        
        page.on("request", handle_request)
        
        # 收集响应
        responses = []
        
        async def handle_response(response):
            if 'service' in response.url.lower() or 'project' in response.url.lower():
                try:
                    body = await response.text()
                    responses.append({
                        'url': response.url,
                        'status': response.status,
                        'body': body[:500],
                    })
                    print(f"  📥 响应: {response.status} {response.url}")
                    print(f"     内容: {body[:300]}")
                except:
                    pass
        
        page.on("response", handle_response)

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

        print("\n" + "="*60)
        print("填写表单...")
        print("="*60)
        
        # 填写表单
        await page.locator('input#ServiceProjectForm_itemName').fill('测试服务项目')
        await page.locator('input#ServiceProjectForm_subtitle').fill('测试副标题')
        
        # 选择radio
        await page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.includes('计费方式')) {
                        const radios = item.querySelectorAll('.ant-radio');
                        if (radios.length > 0) { radios[0].click(); }
                    }
                }
            }
        """)
        
        # 填写textarea
        await page.evaluate("""
            () => {
                const textareas = document.querySelectorAll('.ant-modal textarea');
                for (const ta of textareas) {
                    if (ta.id.startsWith('my-editor_')) {
                        ta.style.visibility = 'visible';
                        ta.style.display = 'block';
                        ta.style.height = '100px';
                        
                        const nativeSetter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
                        nativeSetter.call(ta, '这是一个测试的服务项目介绍内容');
                        ta.dispatchEvent(new Event('input', {bubbles: true}));
                        ta.dispatchEvent(new Event('change', {bubbles: true}));
                        return true;
                    }
                }
                return false;
            }
        """)
        
        await page.wait_for_timeout(500)
        
        # 验证表单值
        form_values = await page.evaluate("""
            () => {
                const name = document.querySelector('input#ServiceProjectForm_itemName');
                const subtitle = document.querySelector('input#ServiceProjectForm_subtitle');
                const ta = document.querySelector('.ant-modal textarea');
                return {
                    name: name ? name.value : null,
                    subtitle: subtitle ? subtitle.value : null,
                    ta_value: ta ? ta.value : null,
                };
            }
        """)
        print(f"表单值: {form_values}")
        
        print("\n" + "="*60)
        print("点击提交...")
        print("="*60)
        
        # 点击提交
        await page.click('.ant-modal button:has-text("确 认")')
        await page.wait_for_timeout(3)
        
        print(f"\n总请求数: {len(requests)}")
        for req in requests:
            print(f"  {req['method']} {req['url']}")
            if req['post_data']:
                print(f"    POST: {req['post_data'][:200]}")
        
        print(f"\n总响应数: {len(responses)}")
        for resp in responses:
            print(f"  {resp['status']} {resp['url']}")
            print(f"    内容: {resp['body'][:200]}")
        
        # 检查最终状态
        modal_count = await page.locator(".ant-modal").count()
        toasts = await page.evaluate("""
            () => Array.from(document.querySelectorAll('.ant-message-notice-content')).map(m => m.textContent.trim())
        """)
        errors = await page.evaluate("""
            () => Array.from(document.querySelectorAll('.ant-form-item-explain-error')).map(e => e.textContent.trim())
        """)
        print(f"\n最终状态:")
        print(f"  弹窗数量: {modal_count}")
        print(f"  Toast: {toasts}")
        print(f"  表单错误: {errors}")
        
        await page.screenshot(path="submit_debug.png")
        print("  截图: submit_debug.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
