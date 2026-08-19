"""
jeecgboot_client.py - JeecgBoot 业务 API 客户端
================================================
继承 BaseClient，封装用户登录、登出、验证码发送等业务接口
所有接口路径基于 OpenAPI 规范（/v3/api-docs）
使用通用 CRUD 辅助方法减少重复代码
"""

from api_clients.base_client import BaseClient


class JeecgBootClient(BaseClient):
    def login(self, username, password, login_type=1, web_type=0):
        """用户密码登录"""
        return self.post(
            "/sys/login",
            json={
                "username": username,
                "password": password,
                "loginType": login_type,
                "webType": web_type,
            },
        )

    def login_with_sms(self, username, sms_code, web_type=0):
        """短信验证码登录"""
        return self.post(
            "/sys/login",
            json={
                "username": username,
                "smsCode": sms_code,
                "loginType": 0,
                "webType": web_type,
            },
        )

    def logout(self):
        """用户登出"""
        token = self.token
        self.clear_token()
        return self.post("/sys/logout", headers={"token": token} if token else {})

    def send_code(self, phone, web_type=0):
        """发送短信验证码"""
        return self.post(
            "/sys/sendCode",
            json={"phone": phone, "webType": web_type},
        )

    def save_platform_user(self, user_name, real_name, sex=1, role_group_id=5, status=1):
        """创建平台用户"""
        return self._save("/platform/user/save",
            userName=user_name,
            realName=real_name,
            sex=sex,
            roleGroupId=role_group_id,
            status=status,
        )

    def page_users(self, page_num=1, page_size=10, user_name=None, role_group_id=None, status=None):
        """分页查询平台用户"""
        return self._page("/platform/user/page",
            page_num=page_num,
            page_size=page_size,
            userName=user_name,
            roleGroupId=role_group_id,
            status=status,
        )

    def reset_pwd(self, user_id):
        """重置平台用户密码"""
        return self.post("/platform/user/resetPwd", json={"id": user_id})

    def edit_user(self, user_id, user_name, real_name, sex=1, role_group_id=5, status=1):
        """编辑平台用户"""
        return self._edit("/platform/user/edit", user_id,
            userName=user_name,
            realName=real_name,
            sex=sex,
            roleGroupId=role_group_id,
            status=status,
        )

    def get_user_detail(self, user_id):
        """获取平台用户详情"""
        return self._detail("/platform/user/detail", user_id)

    def delete_user(self, user_id):
        """删除平台用户"""
        return self._delete("/platform/user/delete", user_id)

    def change_user_status(self, user_id, status):
        """修改平台用户状态"""
        return self._change_status("/platform/user/changeStatus", user_id, status)

    def get_api_definition(self, definition_id=None):
        """获取 API 定义列表或指定定义"""
        if definition_id:
            return self.get(f"/sys/api/definition/{definition_id}")
        return self.get("/sys/api/definition")

    def get_api_case(self, case_id=None):
        """获取 API 用例列表或指定用例"""
        if case_id:
            return self.get(f"/sys/api/case/{case_id}")
        return self.get("/sys/api/case")

    def save_api_case(self, payload):
        """创建或更新 API 用例"""
        return self.post("/sys/api/case", json=payload)

    def get_area_tree(self):
        """获取全国省市区街道四级区域树"""
        return self.post("/common/area/treeAll")

    def add_service_item(self, item_name, billing_method, subtitle=None, icon_url=None, item_desc=None):
        """新增服务项目"""
        return self._save("/platform/serviceItem/add",
            itemName=item_name,
            billingMethod=billing_method,
            subtitle=subtitle,
            iconUrl=icon_url,
            itemDesc=item_desc,
        )

    def page_service_items(self, page_num=1, page_size=10, item_name=None, billing_method=None, is_display=None, start_time=None, end_time=None):
        """分页查询服务项目"""
        return self._page("/platform/serviceItem/paging",
            page_num=page_num,
            page_size=page_size,
            itemName=item_name,
            billingMethod=billing_method,
            isDisplay=is_display,
            startTime=start_time,
            endTime=end_time,
        )

    def list_display_service_items(self, is_display=None):
        """获取展示状态的服务项目列表"""
        payload = {}
        if is_display is not None:
            payload["isDisplay"] = is_display
        return self.post("/platform/serviceItem/listDisplay", json=payload)

    def update_service_item_status(self, item_id, is_display):
        """切换服务项目展示状态"""
        return self._change_status("/platform/serviceItem/updateStatus", item_id, is_display)

    def edit_service_item(self, item_id, item_name, billing_method, subtitle=None, icon_url=None, item_desc=None):
        """编辑服务项目"""
        return self._edit("/platform/serviceItem/edit", item_id,
            itemName=item_name,
            billingMethod=billing_method,
            subtitle=subtitle,
            iconUrl=icon_url,
            itemDesc=item_desc,
        )

    def execute_api_case(self, case_id):
        """执行 API 用例"""
        return self.post(f"/sys/api/case/execute/{case_id}")

    def get_pricing_tree(self, service_item_id):
        """获取指定服务项目的定价树结构"""
        return self.post("/platform/pricing/tree", json={"serviceItemId": service_item_id})

    def get_pricing_tree_by_areas(self, service_item_id, area_list):
        """根据区域列表获取服务定价树"""
        return self.post("/platform/pricing/treeByAreas", json={
            "serviceItemId": service_item_id,
            "areaList": area_list,
        })

    def update_pricing(self, service_item_id, pending_amount, area_list, effective_time=None):
        """更新服务定价（批量更新区县定价）"""
        payload = {
            "serviceItemId": service_item_id,
            "pendingAmount": pending_amount,
            "areaList": area_list,
        }
        if effective_time is not None:
            payload["effectiveTime"] = effective_time
        return self.post("/platform/pricing/updatePricing", json=payload)

    def import_pricing(self, service_item_id, service_item_name, file_path):
        """导入服务定价数据（Excel文件）"""
        import os
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            files = {
                "file": (file_name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            }
            return self.post(
                f"/platform/pricing/import?serviceItemId={service_item_id}&serviceItemName={service_item_name}",
                files=files,
            )

    def save_knowledge(self, title, content, consult_type, display_position, applicable_area):
        """新增知识库"""
        return self.post("/platform/knowledge/save", json={
            "title": title,
            "content": content,
            "consultType": consult_type,
            "displayPosition": display_position,
            "applicableArea": applicable_area,
        })

    def page_knowledge(self, page_num=1, page_size=10, title=None, consult_type=None, display_position=None, status=None):
        """分页查询知识库"""
        return self._page("/platform/knowledge/page",
            page_num=page_num,
            page_size=page_size,
            title=title,
            consultType=consult_type,
            displayPosition=display_position,
            status=status,
        )

    def get_knowledge_detail(self, knowledge_id):
        """获取知识库详情"""
        return self._detail("/platform/knowledge/detail", knowledge_id)

    def edit_knowledge(self, knowledge_id, title, content, consult_type, display_position, applicable_area):
        """编辑知识库"""
        return self._edit("/platform/knowledge/edit", knowledge_id,
            title=title,
            content=content,
            consultType=consult_type,
            displayPosition=display_position,
            applicableArea=applicable_area,
        )

    def change_knowledge_status(self, knowledge_id, status):
        """修改知识库状态"""
        return self._change_status("/platform/knowledge/changeStatus", knowledge_id, status)

    def delete_knowledge(self, knowledge_id):
        """删除知识库"""
        return self._delete("/platform/knowledge/delete", knowledge_id)

    def add_business_scope(self, scope_name, remark=None):
        """新增经营范围"""
        return self._save("/platform/businessScope/add",
            scopeName=scope_name,
            remark=remark,
        )

    def page_business_scopes(self, page_num=1, page_size=10, scope_name=None, is_enabled=None):
        """分页查询经营范围"""
        return self._page("/platform/businessScope/paging",
            page_num=page_num,
            page_size=page_size,
            scopeName=scope_name,
            isEnabled=is_enabled,
        )

    def get_business_scope_detail(self, scope_id):
        """获取经营范围详情"""
        return self._detail("/platform/businessScope/detail", scope_id)

    def edit_business_scope(self, scope_id, scope_name, remark=None):
        """编辑经营范围"""
        return self._edit("/platform/businessScope/edit", scope_id,
            scopeName=scope_name,
            remark=remark,
        )

    def update_business_scope_status(self, scope_id, is_enabled):
        """修改经营范围状态"""
        return self._change_status("/platform/businessScope/updateStatus", scope_id, is_enabled)

    def delete_business_scope(self, scope_id):
        """删除经营范围"""
        return self._delete("/platform/businessScope/del", scope_id)

    def save_role(self, role_name, status=1, role_remark=None):
        """新增角色"""
        return self._save("/common/role/save",
            roleName=role_name,
            status=status,
            roleRemark=role_remark,
        )

    def page_roles(self, page_num=1, page_size=10, role_name=None, status=None):
        """分页查询角色列表"""
        return self._page("/common/role/page",
            page_num=page_num,
            page_size=page_size,
            roleName=role_name,
            status=status,
        )

    def get_role_detail(self, role_id):
        """获取角色详情"""
        return self._detail("/common/role/detail", role_id)

    def edit_role(self, role_id, role_name, status=1, role_remark=None):
        """编辑角色"""
        return self._edit("/common/role/edit", role_id,
            roleName=role_name,
            status=status,
            roleRemark=role_remark,
        )

    def delete_role(self, role_id):
        """删除角色"""
        return self._delete("/common/role/delete", role_id)

    def change_role_status(self, role_id, status):
        """切换角色状态"""
        return self._change_status("/common/role/changeStatus", role_id, status)

    def select_role_all(self):
        """查询所有角色列表（根据当前用户WebType过滤）"""
        return self.post("/common/role/selectRoleAll")

    def select_menus_by_role_id(self, role_id):
        """根据角色ID查询菜单权限信息"""
        return self.post("/common/role/selectMenuListByRoleId", json={"roleId": role_id})

    def add_role_menu(self, role_id, menu_ids):
        """为角色分配菜单权限"""
        return self.post("/common/role/addRoleMenu", json={
            "roleId": role_id,
            "menuIds": menu_ids,
        })

    def save_contact_config(self, service_item_id, title, content, price_content):
        """保存合同配置（合同服务配置）"""
        return self._save("/platform/contactConfig/save",
            serviceItemId=service_item_id,
            title=title,
            content=content,
            priceContent=price_content,
        )

    def page_contact_configs(self, page_num=1, page_size=10, title=None, service_item_id=None):
        """分页查询合同配置"""
        return self._page("/platform/contactConfig/paging",
            page_num=page_num,
            page_size=page_size,
            title=title,
            serviceItemId=service_item_id,
        )

    def get_contact_config_detail(self, config_id):
        """获取合同配置详情"""
        return self._detail("/platform/contactConfig/detail", config_id)

    def edit_contact_config(self, config_id, service_item_id, title, content=None, price_content=None):
        """编辑合同配置"""
        return self._edit("/platform/contactConfig/edit", config_id,
            serviceItemId=service_item_id,
            title=title,
            content=content,
            priceContent=price_content,
        )

    def delete_contact_config(self, config_id):
        """删除合同配置"""
        return self._delete("/platform/contactConfig/delete", config_id)

    def page_contracts(self, page_num=1, page_size=10, contact_no=None, party_a_name=None):
        """分页查询合同列表"""
        return self._page("/platform/contract/page",
            page_num=page_num,
            page_size=page_size,
            contactNo=contact_no,
            partyAName=party_a_name,
        )

    def page_agreements(self, page_num=1, page_size=10):
        """分页查询协议列表"""
        return self._page("/platform/agreement/page",
            page_num=page_num,
            page_size=page_size,
        )

    def get_agreement_detail(self, agreement_id):
        """获取协议详情"""
        return self._detail("/platform/agreement/detail", agreement_id)

    def edit_agreement(self, agreement_id, title, content=None):
        """编辑协议"""
        return self._edit("/platform/agreement/edit", agreement_id,
            title=title,
            content=content,
        )

    def add_tax_type_config(self, tax_type_name, fixed_display=1):
        """新增税种配置"""
        return self._save("/platform/taxTypeConfig/add",
            taxTypeName=tax_type_name,
            fixedDisplay=fixed_display,
        )

    def edit_tax_type_config(self, config_id, tax_type_name, fixed_display=1):
        """编辑税种配置"""
        return self._edit("/platform/taxTypeConfig/edit", config_id,
            taxTypeName=tax_type_name,
            fixedDisplay=fixed_display,
        )

    def page_tax_type_configs(self, page_num=1, page_size=10, tax_type_name=None, status=None):
        """分页查询税种配置"""
        return self._page("/platform/taxTypeConfig/page",
            page_num=page_num,
            page_size=page_size,
            taxTypeName=tax_type_name,
            status=status,
        )

    def change_tax_type_status(self, config_id, status):
        """修改税种配置启用状态"""
        return self._change_status("/platform/taxTypeConfig/status", config_id, status)
