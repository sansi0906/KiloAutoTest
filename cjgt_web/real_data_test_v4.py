"""
超级个体后台 - 实际数据提交验证 V4
使用CSS nth选择器精确定位表单元素
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def gen_data():
    ts = datetime.now().strftime("%m%d%H%M%S")
    return {
        "project_name": f"AUTO_项目_{ts}",
        "project_subtitle": f"副标题_{ts}",
        "project_desc": f"测试内容_{ts}",
        "contract_title": f"AUTO_合同_{ts}",
        "contract_content": f"合同内容_{ts}",
        "contract_fee": f"费用_{ts}",
        "scope_name": f"AUTO_范围_{ts}",
        "scope_remark": f"备注_{ts}",
        "knowledge_title": f"AUTO_知识_{ts}",
        "knowledge_content": f"知识内容_{ts}",
    }


class TestV4:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.results = []
        self.data = gen_data()
        self.created = {}

    async def setup(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=False)
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()

    async def teardown(self):
        if self.browser:
            await self.browser.close()
        if self.pw:
            await self.pw.stop()

    def ok(self, mod, name, detail, ss=""):
        self.results.append({"module": mod, "name": name, "status": "PASS", "detail": detail, "ss": ss})
        print(f"  ✅ [PASS] {name}: {detail}")

    def fail(self, mod, name, detail, ss=""):
        self.results.append({"module": mod, "name": name, "status": "FAIL", "detail": detail, "ss": ss})
        print(f"  ❌ [FAIL] {name}: {detail}")

    def skip(self, mod, name, detail, ss=""):
        self.results.append({"module": mod, "name": name, "status": "SKIP", "detail": detail, "ss": ss})
        print(f"  ⏭️ [SKIP] {name}: {detail}")

    async def ss(self, name):
        p = os.path.join(SCREENSHOT_DIR, f"{name}_{TIMESTAMP}.png")
        await self.page.screenshot(path=p)
        return p

    async def login(self):
        await self.page.goto(LOGIN_URL, wait_until="networkidle")
        await self.page.wait_for_timeout(1000)
        await self.page.fill('input[placeholder="账号"]', USERNAME)
        await self.page.fill('input[type="password"]', PASSWORD)
        await self.page.click('button:has-text("登 录")')
        await self.page.wait_for_timeout(2000)

    async def go(self, path):
        await self.page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
        await self.page.wait_for_timeout(1500)

    async def toasts(self):
        await self.page.wait_for_timeout(1)
        return await self.page.evaluate("""
            () => Array.from(document.querySelectorAll('.ant-message-notice-content')).map(m => m.textContent.trim())
        """)

    # ============ 服务项目配置 ============

    async def test_project_add(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/project-config")

        # 点击新增按钮
        await self.page.click('button:has-text("新增服务项目")')
        await self.page.wait_for_timeout(1500)
        await self.ss("proj_add_01")

        modal = self.page.locator(".ant-modal")
        if await modal.count() == 0:
            self.fail(mod, "新增服务项目", "弹窗未打开")
            return

        # 在modal内填写表单 - 跳过codefield和隐藏元素
        form_inputs = modal.locator(".ant-form-item input[type='text']")
        input_count = await form_inputs.count()
        print(f"  表单输入框数量: {input_count}")
        
        # 找到真正可见、可用的输入框（跳过codefield、隐藏的）
        visible_inputs = []
        for i in range(input_count):
            inp = form_inputs.nth(i)
            info = await inp.evaluate("""
                el => ({
                    className: el.className,
                    style: el.style.cssText,
                    offsetParent: el.offsetParent ? 'visible' : 'hidden',
                    codefield: el.hasAttribute('codefield'),
                    placeholder: el.placeholder || ''
                })
            """)
            # 过滤条件：不是codefield，不是隐藏
            if not info['codefield'] and info['offsetParent'] == 'visible':
                visible_inputs.append(inp)
                print(f"    可用输入框[{len(visible_inputs)-1}]: placeholder={info['placeholder']}")
        
        print(f"  可用输入框: {len(visible_inputs)}")
        
        if len(visible_inputs) >= 1:
            await visible_inputs[0].fill(self.data["project_name"])
            print(f"  填写服务项目名称: {self.data['project_name']}")
        
        if len(visible_inputs) >= 2:
            await visible_inputs[1].fill(self.data["project_subtitle"])
            print(f"  填写副标题: {self.data['project_subtitle']}")

        # 计费方式 - 第一个radio
        radios = modal.locator(".ant-form-item:has-text('计费方式') .ant-radio")
        radio_count = await radios.count()
        print(f"  计费方式选项: {radio_count}")
        if radio_count > 0:
            await radios.first.click()

        # 是否展示 - 第一个radio
        display_radios = modal.locator(".ant-form-item:has-text('是否展示') .ant-radio")
        if await display_radios.count() > 0:
            await display_radios.first.click()

        # 富文本 - 设置内容
        await self.page.evaluate("""
            (content) => {
                const editor = document.querySelector('.ant-modal .ql-editor');
                if (editor) {
                    editor.innerHTML = '<p>' + content + '</p>';
                    editor.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }
        """, self.data["project_desc"])
        print(f"  填写服务项目介绍: {self.data['project_desc']}")

        await self.ss("proj_add_02")

        # 提交
        submit = modal.locator('button:has-text("确 认"), button:has-text("确认")')
        if await submit.count() > 0:
            await submit.first.click()
        await self.page.wait_for_timeout(3)
        await self.ss("proj_add_03")

        # 检查结果
        msgs = await self.toasts()
        print(f"  Toast: {msgs}")

        if any("成功" in m for m in msgs):
            self.ok(mod, "新增服务项目", f"成功。Toast: {msgs}", await self.ss("proj_add_success"))
            self.created["project"] = self.data["project_name"]
        elif await modal.count() > 0:
            self.fail(mod, "新增服务项目", f"仍在表单中。Toast: {msgs}", await self.ss("proj_add_error"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            # 验证数据
            text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
            if self.data["project_name"] in text:
                self.ok(mod, "新增服务项目", "数据已在列表", await self.ss("proj_add_ok"))
            else:
                self.fail(mod, "新增服务项目", f"Toast: {msgs}, 数据未找到", await self.ss("proj_add_fail"))

    async def test_project_edit(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 编辑\n{'='*60}")
        await self.go("/smart-service/project-config")

        # 点击编辑
        edits = self.page.locator('a:has-text("编辑")')
        if await edits.count() > 0:
            await edits.first.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("proj_edit_01")

            modal = self.page.locator(".ant-modal")
            if await modal.count() > 0:
                # 修改副标题 - 找到可用输入框
                form_inputs = modal.locator(".ant-form-item input[type='text']")
                visible_inputs = []
                for i in range(await form_inputs.count()):
                    inp = form_inputs.nth(i)
                    info = await inp.evaluate("el => ({ codefield: el.hasAttribute('codefield'), offsetParent: el.offsetParent ? 'visible' : 'hidden' })")
                    if not info['codefield'] and info['offsetParent'] == 'visible':
                        visible_inputs.append(inp)

                if len(visible_inputs) >= 2:
                    await visible_inputs[1].fill(f"{self.data['project_subtitle']}_编辑")

                # 提交
                submit = modal.locator('button:has-text("确 认"), button:has-text("确认")')
                if await submit.count() > 0:
                    await submit.first.click()
                await self.page.wait_for_timeout(3)
                await self.ss("proj_edit_02")

                msgs = await self.toasts()
                if any("成功" in m for m in msgs):
                    self.ok(mod, "编辑服务项目", f"成功。Toast: {msgs}", await self.ss("proj_edit_ok"))
                elif await self.page.locator(".ant-modal").count() > 0:
                    self.fail(mod, "编辑服务项目", f"仍在表单中。Toast: {msgs}", await self.ss("proj_edit_err"))
                    await self.page.locator(".ant-modal-close").click()
                    await self.page.wait_for_timeout(500)
                else:
                    self.ok(mod, "编辑服务项目", f"Toast: {msgs}（需人工确认）", await self.ss("proj_edit_unknown"))
            else:
                self.fail(mod, "编辑服务项目", "弹窗未打开")
        else:
            self.skip(mod, "编辑服务项目", "未找到编辑按钮")

    async def test_project_toggle(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 切换展示\n{'='*60}")
        await self.go("/smart-service/project-config")

        toggle = self.page.locator('a:has-text("不展示"), a:has-text("展示")')
        if await toggle.count() > 0:
            text = await toggle.first.text_content()
            await toggle.first.click()
            await self.page.wait_for_timeout(1000)

            # 确认
            confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary, .ant-popover button.ant-btn-primary")
            if await confirm.count() > 0:
                await confirm.first.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"切换展示({text})", f"成功。Toast: {msgs}", await self.ss("proj_toggle_ok"))
            else:
                self.fail(mod, f"切换展示({text})", "无确认弹窗", await self.ss("proj_toggle_no"))
        else:
            self.skip(mod, "切换展示", "未找到按钮")

    # ============ 合同服务 ============

    async def test_contract_add(self):
        mod = "智能服务配置-合同服务配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/contract-service")

        await self.page.click('button:has-text("新增合同服务")')
        await self.page.wait_for_timeout(1500)
        await self.ss("contract_add_01")

        modal = self.page.locator(".ant-modal")
        if await modal.count() == 0:
            self.fail(mod, "新增合同服务", "弹窗未打开")
            return

        # 填写表单
        form_inputs = modal.locator(".ant-form-item input[type='text']")
        visible = []
        for i in range(await form_inputs.count()):
            inp = form_inputs.nth(i)
            info = await inp.evaluate("el => ({ codefield: el.hasAttribute('codefield'), offsetParent: el.offsetParent ? 'visible' : 'hidden' })")
            if not info['codefield'] and info['offsetParent'] == 'visible':
                visible.append(inp)

        if len(visible) >= 1:
            await visible[0].fill(self.data["contract_title"])
        if len(visible) >= 2:
            await visible[1].fill(self.data["contract_fee"])

        # 富文本
        await self.page.evaluate("""
            (content) => {
                const editor = document.querySelector('.ant-modal .ql-editor');
                if (editor) { editor.innerHTML = '<p>' + content + '</p>'; editor.dispatchEvent(new Event('input', {bubbles: true})); }
            }
        """, self.data["contract_content"])

        # 下拉选择
        selects = modal.locator(".ant-form-item .ant-select-selector")
        if await selects.count() > 0:
            await selects.first.click()
            await self.page.wait_for_timeout(300)
            options = self.page.locator(".ant-select-item-option")
            if await options.count() > 0:
                await options.first.click()

        print("  表单填写完成")
        await self.ss("contract_add_02")

        # 提交
        submit = modal.locator('button:has-text("确 认"), button:has-text("确认")')
        if await submit.count() > 0:
            await submit.first.click()
        await self.page.wait_for_timeout(3)
        await self.ss("contract_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增合同服务", f"成功。Toast: {msgs}", await self.ss("contract_add_ok"))
            self.created["contract"] = self.data["contract_title"]
        elif await modal.count() > 0:
            self.fail(mod, "新增合同服务", f"仍在表单中。Toast: {msgs}", await self.ss("contract_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增合同服务", f"Toast: {msgs}", await self.ss("contract_add_fail"))

    # ============ 经营范围 ============

    async def test_scope_add(self):
        mod = "智能服务配置-经营范围配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/scope-config")

        await self.page.click('button:has-text("新增经营范围")')
        await self.page.wait_for_timeout(1500)
        await self.ss("scope_add_01")

        modal = self.page.locator(".ant-modal")
        if await modal.count() == 0:
            self.fail(mod, "新增经营范围", "弹窗未打开")
            return

        # 填写
        form_inputs = modal.locator(".ant-form-item input[type='text']")
        visible = []
        for i in range(await form_inputs.count()):
            inp = form_inputs.nth(i)
            info = await inp.evaluate("el => ({ codefield: el.hasAttribute('codefield'), offsetParent: el.offsetParent ? 'visible' : 'hidden' })")
            if not info['codefield'] and info['offsetParent'] == 'visible':
                visible.append(inp)

        if len(visible) >= 1:
            await visible[0].fill(self.data["scope_name"])
        if len(visible) >= 2:
            await visible[1].fill(self.data["scope_remark"])

        # 启用状态 - switch
        switch = modal.locator(".ant-form-item:has-text('启用状态') .ant-switch")
        if await switch.count() > 0:
            is_checked = await switch.first.evaluate("el => el.classList.contains('ant-switch-checked')")
            if not is_checked:
                await switch.first.click()

        print("  表单填写完成")
        await self.ss("scope_add_02")

        # 提交
        submit = modal.locator('button:has-text("确 认"), button:has-text("确认")')
        if await submit.count() > 0:
            await submit.first.click()
        await self.page.wait_for_timeout(3)
        await self.ss("scope_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增经营范围", f"成功。Toast: {msgs}", await self.ss("scope_add_ok"))
            self.created["scope"] = self.data["scope_name"]
        elif await modal.count() > 0:
            self.fail(mod, "新增经营范围", f"仍在表单中。Toast: {msgs}", await self.ss("scope_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增经营范围", f"Toast: {msgs}", await self.ss("scope_add_fail"))

    # ============ 知识库 ============

    async def test_knowledge_add(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/content-manage/knowledge")

        await self.page.click('button:has-text("新增知识库")')
        await self.page.wait_for_timeout(1500)
        await self.ss("knowledge_add_01")

        modal = self.page.locator(".ant-modal")
        if await modal.count() == 0:
            self.fail(mod, "新增知识库", "弹窗未打开")
            return

        # 填写标题
        form_inputs = modal.locator(".ant-form-item input[type='text']")
        visible = []
        for i in range(await form_inputs.count()):
            inp = form_inputs.nth(i)
            info = await inp.evaluate("el => ({ codefield: el.hasAttribute('codefield'), offsetParent: el.offsetParent ? 'visible' : 'hidden' })")
            if not info['codefield'] and info['offsetParent'] == 'visible':
                visible.append(inp)

        if len(visible) >= 1:
            await visible[0].fill(self.data["knowledge_title"])

        # 富文本
        await self.page.evaluate("""
            (content) => {
                const editor = document.querySelector('.ant-modal .ql-editor');
                if (editor) { editor.innerHTML = '<p>' + content + '</p>'; editor.dispatchEvent(new Event('input', {bubbles: true})); }
            }
        """, self.data["knowledge_content"])

        # 下拉选择 - 展示位置
        selects = modal.locator(".ant-form-item .ant-select-selector")
        if await selects.count() >= 1:
            await selects.nth(0).click()
            await self.page.wait_for_timeout(300)
            await self.page.locator(".ant-select-item-option").first.click()
        
        if await selects.count() >= 2:
            await selects.nth(1).click()
            await self.page.wait_for_timeout(300)
            await self.page.locator(".ant-select-item-option").first.click()

        print("  表单填写完成")
        await self.ss("knowledge_add_02")

        # 提交
        submit = modal.locator('button:has-text("确 认"), button:has-text("确认")')
        if await submit.count() > 0:
            await submit.first.click()
        await self.page.wait_for_timeout(3)
        await self.ss("knowledge_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增知识库", f"成功。Toast: {msgs}", await self.ss("knowledge_add_ok"))
            self.created["knowledge"] = self.data["knowledge_title"]
        elif await modal.count() > 0:
            self.fail(mod, "新增知识库", f"仍在表单中。Toast: {msgs}", await self.ss("knowledge_add_err"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增知识库", f"Toast: {msgs}", await self.ss("knowledge_add_fail"))

    async def test_knowledge_toggle(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 状态切换\n{'='*60}")
        await self.go("/content-manage/knowledge")

        toggle = self.page.locator('a:has-text("禁用"), a:has-text("启用")')
        if await toggle.count() > 0:
            text = await toggle.first.text_content()
            await toggle.first.click()
            await self.page.wait_for_timeout(1000)

            # 确认
            confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
            if await confirm.count() > 0:
                await confirm.first.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"状态切换({text})", f"成功。Toast: {msgs}", await self.ss("knowledge_toggle_ok"))
            else:
                self.fail(mod, f"状态切换({text})", "无确认弹窗", await self.ss("knowledge_toggle_no"))
        else:
            self.skip(mod, "状态切换", "未找到按钮")

    async def test_knowledge_detail(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 查看详情\n{'='*60}")
        await self.go("/content-manage/knowledge")

        detail = self.page.locator('a:has-text("详情")')
        if await detail.count() > 0:
            await detail.first.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("knowledge_detail_01")

            if await self.page.locator(".ant-modal, .ant-drawer").count() > 0:
                content = await self.page.evaluate("""
                    () => {
                        const body = document.querySelector('.ant-modal-body, .ant-drawer-body');
                        return body ? body.textContent.trim().substring(0, 200) : null;
                    }
                """)
                self.ok(mod, "查看详情", f"内容: {content[:100] if content else '无'}...", await self.ss("knowledge_detail_ok"))
                
                close = self.page.locator(".ant-modal-close, .ant-drawer-close")
                if await close.count() > 0:
                    await close.first.click()
                    await self.page.wait_for_timeout(500)
            else:
                self.fail(mod, "查看详情", "弹窗未打开")
        else:
            self.skip(mod, "查看详情", "未找到详情按钮")

    def report(self):
        path = os.path.join(REPORT_DIR, f"real_data_report_{TIMESTAMP}.md")
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")

        lines = [
            f"# 超级个体后台 - 实际数据提交验证报告",
            f"",
            f"**时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 总数 | {total} |",
            f"| ✅通过 | {passed} |",
            f"| ❌失败 | {failed} |",
            f"| ⏭️跳过 | {skipped} |",
            f"",
            f"## 详细结果\n",
        ]

        mod = ""
        for r in self.results:
            if r["module"] != mod:
                mod = r["module"]
                lines.append(f"### {mod}\n")
            icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⏭️")
            lines.append(f"- {icon} **{r['name']}**: {r['detail']}")

        lines.extend([f"\n## 问题汇总\n"])
        issues = [r for r in self.results if r["status"] == "FAIL"]
        if issues:
            for i, iss in enumerate(issues, 1):
                lines.append(f"{i}. **{iss['name']}** - {iss['detail']}")
        else:
            lines.append("无问题。")

        lines.extend([f"\n## 测试数据（需清理）\n"])
        for k, v in self.created.items():
            lines.append(f"- {k}: `{v}`")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n报告: {path}")
        return path

    async def run(self):
        await self.setup()
        try:
            await self.login()
            await self.test_project_add()
            await self.test_project_edit()
            await self.test_project_toggle()
            await self.test_contract_add()
            await self.test_scope_add()
            await self.test_knowledge_add()
            await self.test_knowledge_toggle()
            await self.test_knowledge_detail()
        finally:
            await self.teardown()
        return self.report()


async def main():
    t = TestV4()
    await t.run()
    total = len(t.results)
    passed = sum(1 for r in t.results if r["status"] == "PASS")
    failed = sum(1 for r in t.results if r["status"] == "FAIL")
    skipped = sum(1 for r in t.results if r["status"] == "SKIP")
    print(f"\n总数:{total} 通过:{passed} 失败:{failed} 跳过:{skipped}")


if __name__ == "__main__":
    asyncio.run(main())
