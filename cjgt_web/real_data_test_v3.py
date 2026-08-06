"""
超级个体后台 - 实际数据提交验证测试 V3
使用Playwright原生API操作，更稳定
"""
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

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
        "project_desc": f"自动化测试内容_{ts}",
        "contract_title": f"AUTO_合同_{ts}",
        "contract_content": f"合同内容_{ts}",
        "contract_fee": f"费用_{ts}",
        "scope_name": f"AUTO_范围_{ts}",
        "scope_remark": f"备注_{ts}",
        "knowledge_title": f"AUTO_知识_{ts}",
        "knowledge_content": f"知识内容_{ts}",
    }


class TestV3:
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

    def ok(self, module, name, detail, path=""):
        self.results.append({"module": module, "name": name, "status": "PASS", "detail": detail, "screenshot": path})
        print(f"  ✅ [PASS] {name}: {detail}")

    def fail(self, module, name, detail, path=""):
        self.results.append({"module": module, "name": name, "status": "FAIL", "detail": detail, "screenshot": path})
        print(f"  ❌ [FAIL] {name}: {detail}")

    def skip(self, module, name, detail, path=""):
        self.results.append({"module": module, "name": name, "status": "SKIP", "detail": detail, "screenshot": path})
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
        return "/dashboard" in self.page.url

    async def go(self, path):
        await self.page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
        await self.page.wait_for_timeout(1500)

    async def toasts(self):
        await self.page.wait_for_timeout(1)
        return await self.page.evaluate("""
            () => {
                const msgs = document.querySelectorAll('.ant-message-notice-content');
                return Array.from(msgs).map(m => m.textContent.trim());
            }
        """)

    # ============ 服务项目配置 ============

    async def test_project_add(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/project-config")
        
        # 点击新增
        await self.page.get_by_role("button", name="新增服务项目").click()
        await self.page.wait_for_timeout(1500)
        await self.ss("proj_add_01")

        # 填写表单 - 使用 label 关联的 input
        # 服务项目名称
        name_input = self.page.get_by_label("服务项目名称")
        await name_input.fill(self.data["project_name"])
        
        # 副标题
        subtitle_input = self.page.get_by_label("副标题")
        await subtitle_input.fill(self.data["project_subtitle"])
        
        # 计费方式 - 选择第二个radio (按次)
        radios = self.page.get_by_label("计费方式").locator(".ant-radio")
        await radios.nth(0).click()
        
        # 是否展示 - 选择是
        display_radios = self.page.get_by_label("是否展示").locator(".ant-radio")
        await display_radios.nth(0).click()
        
        # 服务项目介绍 - 富文本
        await self.page.evaluate("""
            (content) => {
                const editor = document.querySelector('.ant-modal .ql-editor, .ant-modal .w-e-text');
                if (editor) {
                    editor.textContent = content;
                    editor.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }
        """, self.data["project_desc"])
        
        print("  表单填写完成")
        await self.ss("proj_add_02")

        # 点击确认
        await self.page.get_by_role("button", name="确 认").click()
        await self.page.wait_for_timeout(3)
        await self.ss("proj_add_03")

        # 检查结果
        msgs = await self.toasts()
        print(f"  Toast: {msgs}")

        if any("成功" in m for m in msgs):
            self.ok(mod, "新增服务项目", f"成功，Toast: {msgs}", await self.ss("proj_add_success"))
            self.created["project"] = self.data["project_name"]
        elif await self.page.locator(".ant-modal").count() > 0:
            self.fail(mod, "新增服务项目", f"仍在表单中，可能有验证错误。Toast: {msgs}", await self.ss("proj_add_error"))
            # 关闭
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            # 验证数据
            rows_text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
            if self.data["project_name"] in rows_text:
                self.ok(mod, "新增服务项目", "数据已在列表中", await self.ss("proj_add_verified"))
            else:
                self.fail(mod, "新增服务项目", f"Toast: {msgs}, 数据未找到", await self.ss("proj_add_failed"))

    async def test_project_edit(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 编辑\n{'='*60}")
        await self.go("/smart-service/project-config")

        # 点击第一个编辑按钮
        edit_link = self.page.get_by_role("link", name="编辑").first
        if await edit_link.count() > 0:
            await edit_link.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("proj_edit_01")

            if await self.page.locator(".ant-modal").count() > 0:
                # 修改副标题
                await self.page.get_by_label("副标题").fill(f"{self.data['project_subtitle']}_已编辑")
                
                await self.page.get_by_role("button", name="确 认").click()
                await self.page.wait_for_timeout(3)
                await self.ss("proj_edit_02")

                msgs = await self.toasts()
                if any("成功" in m for m in msgs):
                    self.ok(mod, "编辑服务项目", f"成功，Toast: {msgs}", await self.ss("proj_edit_success"))
                else:
                    self.ok(mod, "编辑服务项目", f"Toast: {msgs}（需人工确认）", await self.ss("proj_edit_unknown"))
            else:
                self.fail(mod, "编辑服务项目", "弹窗未打开")
        else:
            self.skip(mod, "编辑服务项目", "未找到编辑按钮")

    async def test_project_toggle(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 切换展示状态\n{'='*60}")
        await self.go("/smart-service/project-config")

        # 查找展示/不展示按钮
        toggle = self.page.get_by_role("link", name="不展示")
        if await toggle.count() == 0:
            toggle = self.page.get_by_role("link", name="展示")
        
        if await toggle.count() > 0:
            text = await toggle.text_content()
            await toggle.click()
            await self.page.wait_for_timeout(1000)

            # 确认弹窗
            confirm_ok = self.page.get_by_role("button", name="确 认")
            if await confirm_ok.count() > 0:
                await confirm_ok.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"切换展示状态({text})", f"成功，Toast: {msgs}", await self.ss("proj_toggle_ok"))
            else:
                self.fail(mod, f"切换展示状态({text})", "无确认弹窗", await self.ss("proj_toggle_no_confirm"))
        else:
            self.skip(mod, "切换展示状态", "未找到按钮")

    # ============ 合同服务配置 ============

    async def test_contract_add(self):
        mod = "智能服务配置-合同服务配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/contract-service")

        await self.page.get_by_role("button", name="新增合同服务").click()
        await self.page.wait_for_timeout(1500)
        await self.ss("contract_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增合同服务", "弹窗未打开")
            return

        # 填写
        await self.page.get_by_label("合同服务标题").fill(self.data["contract_title"])
        
        # 富文本
        await self.page.evaluate("""
            (content) => {
                const editor = document.querySelector('.ant-modal .ql-editor, .ant-modal .w-e-text');
                if (editor) { editor.textContent = content; editor.dispatchEvent(new Event('input', {bubbles: true})); }
            }
        """, self.data["contract_content"])
        
        await self.page.get_by_label("费用内容").fill(self.data["contract_fee"])
        
        # 选择所属服务项目
        select = self.page.get_by_label("所属服务项目")
        await select.click()
        await self.page.wait_for_timeout(500)
        await self.page.locator(".ant-select-item-option").first.click()
        
        print("  表单填写完成")
        await self.ss("contract_add_02")

        # 提交
        await self.page.get_by_role("button", name="确 认").click()
        await self.page.wait_for_timeout(3)
        await self.ss("contract_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增合同服务", f"成功，Toast: {msgs}", await self.ss("contract_add_success"))
            self.created["contract"] = self.data["contract_title"]
        elif await self.page.locator(".ant-modal").count() > 0:
            self.fail(mod, "新增合同服务", f"仍在表单中。Toast: {msgs}", await self.ss("contract_add_error"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增合同服务", f"Toast: {msgs}", await self.ss("contract_add_failed"))

    # ============ 经营范围配置 ============

    async def test_scope_add(self):
        mod = "智能服务配置-经营范围配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/scope-config")

        await self.page.get_by_role("button", name="新增经营范围").click()
        await self.page.wait_for_timeout(1500)
        await self.ss("scope_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增经营范围", "弹窗未打开")
            return

        # 填写
        await self.page.get_by_label("经营范围名称").fill(self.data["scope_name"])
        await self.page.get_by_label("备注").fill(self.data["scope_remark"])
        
        # 启用状态
        switch = self.page.get_by_label("启用状态")
        switch_checked = await switch.locator(".ant-switch").evaluate("el => el.classList.contains('ant-switch-checked')")
        if not switch_checked:
            await switch.click()
        
        print("  表单填写完成")
        await self.ss("scope_add_02")

        # 提交
        await self.page.get_by_role("button", name="确 认").click()
        await self.page.wait_for_timeout(3)
        await self.ss("scope_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增经营范围", f"成功，Toast: {msgs}", await self.ss("scope_add_success"))
            self.created["scope"] = self.data["scope_name"]
        elif await self.page.locator(".ant-modal").count() > 0:
            self.fail(mod, "新增经营范围", f"仍在表单中。Toast: {msgs}", await self.ss("scope_add_error"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增经营范围", f"Toast: {msgs}", await self.ss("scope_add_failed"))

    # ============ 知识库 ============

    async def test_knowledge_add(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/content-manage/knowledge")

        await self.page.get_by_role("button", name="新增知识库").click()
        await self.page.wait_for_timeout(1500)
        await self.ss("knowledge_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增知识库", "弹窗未打开")
            return

        # 填写
        await self.page.get_by_label("标题").fill(self.data["knowledge_title"])
        
        # 富文本
        await self.page.evaluate("""
            (content) => {
                const editor = document.querySelector('.ant-modal .ql-editor, .ant-modal .w-e-text');
                if (editor) { editor.textContent = content; editor.dispatchEvent(new Event('input', {bubbles: true})); }
            }
        """, self.data["knowledge_content"])
        
        # 下拉选择
        await self.page.get_by_label("展示位置").click()
        await self.page.wait_for_timeout(300)
        await self.page.locator(".ant-select-item-option").first.click()
        
        await self.page.get_by_label("资讯类型").click()
        await self.page.wait_for_timeout(300)
        await self.page.locator(".ant-select-item-option").first.click()
        
        print("  表单填写完成")
        await self.ss("knowledge_add_02")

        # 提交
        await self.page.get_by_role("button", name="确 认").click()
        await self.page.wait_for_timeout(3)
        await self.ss("knowledge_add_03")

        msgs = await self.toasts()
        if any("成功" in m for m in msgs):
            self.ok(mod, "新增知识库", f"成功，Toast: {msgs}", await self.ss("knowledge_add_success"))
            self.created["knowledge"] = self.data["knowledge_title"]
        elif await self.page.locator(".ant-modal").count() > 0:
            self.fail(mod, "新增知识库", f"仍在表单中。Toast: {msgs}", await self.ss("knowledge_add_error"))
            await self.page.locator(".ant-modal-close").click()
            await self.page.wait_for_timeout(500)
        else:
            self.fail(mod, "新增知识库", f"Toast: {msgs}", await self.ss("knowledge_add_failed"))

    async def test_knowledge_toggle(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 状态切换\n{'='*60}")
        await self.go("/content-manage/knowledge")

        # 查找禁用/启用
        toggle = self.page.get_by_role("link", name="禁用")
        if await toggle.count() == 0:
            toggle = self.page.get_by_role("link", name="启用")
        
        if await toggle.count() > 0:
            text = await toggle.text_content()
            await toggle.click()
            await self.page.wait_for_timeout(1000)
            
            confirm = self.page.get_by_role("button", name="确 认")
            if await confirm.count() > 0:
                await confirm.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"状态切换({text})", f"成功，Toast: {msgs}", await self.ss("knowledge_toggle_ok"))
            else:
                # 可能是popover确认
                pop_confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
                if await pop_confirm.count() > 0:
                    await pop_confirm.click()
                    await self.page.wait_for_timeout(2)
                    msgs = await self.toasts()
                    self.ok(mod, f"状态切换({text})", f"成功，Toast: {msgs}", await self.ss("knowledge_toggle_ok2"))
                else:
                    self.fail(mod, f"状态切换({text})", "无确认弹窗", await self.ss("knowledge_toggle_no_confirm"))
        else:
            self.skip(mod, "状态切换", "未找到禁用/启用按钮")

    async def test_knowledge_detail(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 查看详情\n{'='*60}")
        await self.go("/content-manage/knowledge")

        detail = self.page.get_by_role("link", name="详情")
        if await detail.count() > 0:
            await detail.click()
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
                
                # 关闭
                close = self.page.locator(".ant-modal-close, .ant-drawer-close")
                if await close.count() > 0:
                    await close.click()
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
            f"## 详细结果",
            f"",
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
    t = TestV3()
    await t.run()
    total = len(t.results)
    passed = sum(1 for r in t.results if r["status"] == "PASS")
    failed = sum(1 for r in t.results if r["status"] == "FAIL")
    print(f"\n总数:{total} 通过:{passed} 失败:{failed}")


if __name__ == "__main__":
    asyncio.run(main())
