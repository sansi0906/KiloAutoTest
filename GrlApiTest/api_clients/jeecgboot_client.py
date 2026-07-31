"""
jeecgboot_client.py - JeecgBoot 业务 API 客户端
=================================================
继承 BaseClient，封装用户登录、登出、验证码发送等业务接口
所有接口路径基于 OpenAPI 规范（/v3/api-docs）
"""

from api_clients.base_client import BaseClient


class JeecgBootClient(BaseClient):
    def login(self, username, password, login_type=1, web_type=0):
        """用户密码登录

        Args:
            username: 用户名
            password: 密码
            login_type: 登录类型，1=密码登录，0=短信验证码登录
            web_type: 终端类型，0=管理后台，1=用户端

        Returns:
            Response 对象，响应体包含 code、message、data.token
        """
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
        """短信验证码登录

        Args:
            username: 用户名
            sms_code: 短信验证码
            web_type: 终端类型，0=管理后台，1=用户端

        Returns:
            Response 对象
        """
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
        """用户登出

        登出时携带 token 请求头，登出后自动清除本地 Token

        Returns:
            Response 对象
        """
        token = self.token
        self.clear_token()
        return self.post("/sys/logout", headers={"token": token} if token else {})

    def send_code(self, phone, web_type=0):
        """发送短信验证码

        Args:
            phone: 手机号，需符合 1[3-9]XXXXXXXXX 格式
            web_type: 终端类型，0=管理后台，1=用户端

        Returns:
            Response 对象
        """
        return self.post(
            "/sys/sendCode",
            json={"phone": phone, "webType": web_type},
        )

    def save_platform_user(self, user_name, real_name, sex=1, role_group_id=5, status=1):
        """创建平台用户

        Args:
            user_name: 登录账号（手机号格式）
            real_name: 真实姓名
            sex: 性别，0=女，1=男
            role_group_id: 角色组ID
            status: 状态，1=启用，0=禁用

        Returns:
            Response 对象
        """
        return self.post(
            "/platform/user/save",
            json={
                "userName": user_name,
                "realName": real_name,
                "sex": sex,
                "roleGroupId": role_group_id,
                "status": status,
            },
        )

    def page_users(self, page_num=1, page_size=10, user_name=None, role_group_id=None, status=None):
        """分页查询平台用户

        Args:
            page_num: 页码（从1开始）
            page_size: 每页条数（1-100）
            user_name: 用户名/手机号模糊匹配
            role_group_id: 角色组ID筛选
            status: 状态筛选，1=启用，0=禁用

        Returns:
            Response 对象
        """
        payload = {
            "pageNum": page_num,
            "pageSize": page_size,
        }
        if user_name is not None:
            payload["userName"] = user_name
        if role_group_id is not None:
            payload["roleGroupId"] = role_group_id
        if status is not None:
            payload["status"] = status
        return self.post("/platform/user/page", json=payload)

    def reset_pwd(self, user_id):
        """重置平台用户密码

        Args:
            user_id: 用户ID

        Returns:
            Response 对象
        """
        return self.post(
            "/platform/user/resetPwd",
            json={"id": user_id},
        )

    def edit_user(self, user_id, user_name, real_name, sex=1, role_group_id=5, status=1):
        """编辑平台用户

        Args:
            user_id: 用户ID
            user_name: 登录账号（手机号格式）
            real_name: 真实姓名
            sex: 性别，0=女，1=男
            role_group_id: 角色组ID
            status: 状态，1=启用，0=禁用

        Returns:
            Response 对象
        """
        return self.post(
            "/platform/user/edit",
            json={
                "id": user_id,
                "userName": user_name,
                "realName": real_name,
                "sex": sex,
                "roleGroupId": role_group_id,
                "status": status,
            },
        )

    def get_user_detail(self, user_id):
        """获取平台用户详情

        Args:
            user_id: 用户ID

        Returns:
            Response 对象
        """
        return self.post(
            "/platform/user/detail",
            json={"id": user_id},
        )

    def delete_user(self, user_id):
        """删除平台用户

        Args:
            user_id: 用户ID

        Returns:
            Response 对象
        """
        return self.post(
            "/platform/user/delete",
            json={"id": user_id},
        )

    def change_user_status(self, user_id, status):
        """修改平台用户状态

        Args:
            user_id: 用户ID
            status: 状态，1=启用，0=禁用

        Returns:
            Response 对象
        """
        return self.post(
            "/platform/user/changeStatus",
            json={"id": user_id, "status": status},
        )

    def get_api_definition(self, definition_id=None):
        """获取 API 定义列表或指定定义

        Args:
            definition_id: 可选，指定 API 定义 ID

        Returns:
            Response 对象
        """
        if definition_id:
            return self.get(f"/sys/api/definition/{definition_id}")
        return self.get("/sys/api/definition")

    def get_api_case(self, case_id=None):
        """获取 API 用例列表或指定用例

        Args:
            case_id: 可选，指定 API 用例 ID

        Returns:
            Response 对象
        """
        if case_id:
            return self.get(f"/sys/api/case/{case_id}")
        return self.get("/sys/api/case")

    def save_api_case(self, payload):
        """创建或更新 API 用例

        Args:
            payload: 用例数据字典

        Returns:
            Response 对象
        """
        return self.post("/sys/api/case", json=payload)

    def get_area_tree(self):
        """获取全国省市区街道四级区域树

        Returns:
            Response 对象，响应体包含 code, data.areaTreeJson
        """
        return self.post("/common/area/treeAll")

    def add_service_item(self, item_name, billing_method, subtitle=None, icon_url=None, item_desc=None):
        """新增服务项目

        Args:
            item_name: 服务项目名称（最长10个字符）
            billing_method: 收费方式，1-免费，2-收费
            subtitle: 副标题（可选，最长100个字符）
            icon_url: 图标地址（可选，文件路径或图片链接）
            item_desc: 服务项目描述（可选，最长2000个字符）

        Returns:
            Response 对象
        """
        payload = {
            "itemName": item_name,
            "billingMethod": billing_method,
        }
        if subtitle is not None:
            payload["subtitle"] = subtitle
        if icon_url is not None:
            payload["iconUrl"] = icon_url
        if item_desc is not None:
            payload["itemDesc"] = item_desc
        return self.post("/platform/serviceItem/add", json=payload)

    def page_service_items(self, page_num=1, page_size=10, item_name=None, billing_method=None, is_display=None, start_time=None, end_time=None):
        """分页查询服务项目

        Args:
            page_num: 页码（从1开始）
            page_size: 每页条数（1-100）
            item_name: 服务项目名称（模糊匹配）
            billing_method: 收费方式，1-免费，2-收费
            is_display: 是否展示，1-展示，0-不展示
            start_time: 创建时间-开始（可选）
            end_time: 创建时间-结束（可选）

        Returns:
            Response 对象
        """
        payload = {
            "pageNum": page_num,
            "pageSize": page_size,
        }
        if item_name is not None:
            payload["itemName"] = item_name
        if billing_method is not None:
            payload["billingMethod"] = billing_method
        if is_display is not None:
            payload["isDisplay"] = is_display
        if start_time is not None:
            payload["startTime"] = start_time
        if end_time is not None:
            payload["endTime"] = end_time
        return self.post("/platform/serviceItem/paging", json=payload)

    def list_display_service_items(self, is_display=None):
        """获取展示状态的服务项目列表

        Args:
            is_display: 是否展示，1-展示，0-不展示（可选，不传则查询全部）

        Returns:
            Response 对象
        """
        payload = {}
        if is_display is not None:
            payload["isDisplay"] = is_display
        return self.post("/platform/serviceItem/listDisplay", json=payload)

    def update_service_item_status(self, item_id, is_display):
        """切换服务项目展示状态

        Args:
            item_id: 服务项目ID
            is_display: 是否展示，1-展示，0-不展示

        Returns:
            Response 对象
        """
        return self.post("/platform/serviceItem/updateStatus", json={
            "id": item_id,
            "isDisplay": is_display,
        })

    def edit_service_item(self, item_id, item_name, billing_method, subtitle=None, icon_url=None, item_desc=None):
        """编辑服务项目

        Args:
            item_id: 服务项目ID
            item_name: 服务项目名称（最长10个字符）
            billing_method: 收费方式，1-免费，2-收费
            subtitle: 副标题（可选，最长100个字符）
            icon_url: 图标地址（可选，文件路径或图片链接）
            item_desc: 服务项目描述（可选，最长2000个字符）

        Returns:
            Response 对象
        """
        payload = {
            "id": item_id,
            "itemName": item_name,
            "billingMethod": billing_method,
        }
        if subtitle is not None:
            payload["subtitle"] = subtitle
        if icon_url is not None:
            payload["iconUrl"] = icon_url
        if item_desc is not None:
            payload["itemDesc"] = item_desc
        return self.post("/platform/serviceItem/edit", json=payload)

    def execute_api_case(self, case_id):
        """执行 API 用例

        Args:
            case_id: 用例 ID

        Returns:
            Response 对象
        """
        return self.post(f"/sys/api/case/execute/{case_id}")

    def get_area_tree(self):
        """获取全国省市区街道四级区域树

        Returns:
            Response 对象，响应体包含 code, data.areaTreeJson
        """
        return self.post("/common/area/treeAll")

    def get_pricing_tree(self, service_item_id):
        """获取指定服务项目的定价树结构

        Args:
            service_item_id: 服务项目ID

        Returns:
            Response 对象，响应体包含 code, data.servicePricingTree
        """
        return self.post("/platform/pricing/tree", json={"serviceItemId": service_item_id})

    def get_pricing_tree_by_areas(self, service_item_id, area_list):
        """根据区域列表获取服务定价树

        Args:
            service_item_id: 服务项目ID
            area_list: 区域列表，每个元素包含 code, level, name

        Returns:
            Response 对象
        """
        return self.post("/platform/pricing/treeByAreas", json={
            "serviceItemId": service_item_id,
            "areaList": area_list,
        })

    def update_pricing(self, service_item_id, amount, area_list):
        """更新服务定价（批量更新区县定价）

        Args:
            service_item_id: 服务项目ID
            amount: 价格金额
            area_list: 区域列表，每个元素包含 code, level, name

        Returns:
            Response 对象
        """
        return self.post("/platform/pricing/updatePricing", json={
            "serviceItemId": service_item_id,
            "amount": amount,
            "areaList": area_list,
        })

    def import_pricing(self, service_item_id, service_item_name, file_path):
        """导入服务定价数据（Excel文件）

        Args:
            service_item_id: 服务项目ID
            service_item_name: 服务项目名称
            file_path: Excel文件路径

        Returns:
            Response 对象
        """
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
        """新增知识库

        Args:
            title: 标题（最长50个字符）
            content: 内容（最长2000个字符）
            consult_type: 咨询类型，1-智能客服, 2-在线客服, 3-智能问答
            display_position: 展示位置数组，[0-移动端, 1-PC端]
            applicable_area: 适用区域列表，每个元素包含 code, level, name

        Returns:
            Response 对象
        """
        return self.post("/platform/knowledge/save", json={
            "title": title,
            "content": content,
            "consultType": consult_type,
            "displayPosition": display_position,
            "applicableArea": applicable_area,
        })

    def page_knowledge(self, page_num=1, page_size=10, title=None, consult_type=None, display_position=None, status=None):
        """分页查询知识库

        Args:
            page_num: 页码（从1开始）
            page_size: 每页条数（1-100）
            title: 标题（模糊查询）
            consult_type: 咨询类型，1-智能客服, 2-在线客服, 3-智能问答
            display_position: 展示位置，0-移动端, 1-PC端
            status: 状态，1-启用, 0-禁用

        Returns:
            Response 对象
        """
        payload = {
            "pageNum": page_num,
            "pageSize": page_size,
        }
        if title is not None:
            payload["title"] = title
        if consult_type is not None:
            payload["consultType"] = consult_type
        if display_position is not None:
            payload["displayPosition"] = display_position
        if status is not None:
            payload["status"] = status
        return self.post("/platform/knowledge/page", json=payload)

    def get_knowledge_detail(self, knowledge_id):
        """获取知识库详情

        Args:
            knowledge_id: 知识库ID

        Returns:
            Response 对象
        """
        return self.post("/platform/knowledge/detail", json={"id": knowledge_id})

    def edit_knowledge(self, knowledge_id, title, content, consult_type, display_position, applicable_area):
        """编辑知识库

        Args:
            knowledge_id: 知识库ID
            title: 标题（最长50个字符）
            content: 内容（最长2000个字符）
            consult_type: 咨询类型，1-智能客服, 2-在线客服, 3-智能问答
            display_position: 展示位置数组，[0-移动端, 1-PC端]
            applicable_area: 适用区域列表，每个元素包含 code, level, name

        Returns:
            Response 对象
        """
        return self.post("/platform/knowledge/edit", json={
            "id": knowledge_id,
            "title": title,
            "content": content,
            "consultType": consult_type,
            "displayPosition": display_position,
            "applicableArea": applicable_area,
        })

    def change_knowledge_status(self, knowledge_id, status):
        """修改知识库状态

        Args:
            knowledge_id: 知识库ID
            status: 状态，1-启用, 0-禁用

        Returns:
            Response 对象
        """
        return self.post("/platform/knowledge/changeStatus", json={"id": knowledge_id, "status": status})

    def delete_knowledge(self, knowledge_id):
        """删除知识库

        Args:
            knowledge_id: 知识库ID

        Returns:
            Response 对象
        """
        return self.post("/platform/knowledge/delete", json={"id": knowledge_id})

    def add_business_scope(self, scope_name, remark=None):
        """新增经营范围

        Args:
            scope_name: 经营范围名称（最长20个字符）
            remark: 备注（可选，最长200个字符）

        Returns:
            Response 对象
        """
        payload = {"scopeName": scope_name}
        if remark is not None:
            payload["remark"] = remark
        return self.post("/platform/businessScope/add", json=payload)

    def page_business_scopes(self, page_num=1, page_size=10, scope_name=None, is_enabled=None):
        """分页查询经营范围

        Args:
            page_num: 页码（从1开始）
            page_size: 每页条数（1-100）
            scope_name: 经营范围名称（模糊匹配）
            is_enabled: 状态，1-启用, 0-禁用

        Returns:
            Response 对象
        """
        payload = {"pageNum": page_num, "pageSize": page_size}
        if scope_name is not None:
            payload["scopeName"] = scope_name
        if is_enabled is not None:
            payload["isEnabled"] = is_enabled
        return self.post("/platform/businessScope/paging", json=payload)

    def get_business_scope_detail(self, scope_id):
        """获取经营范围详情

        Args:
            scope_id: 经营范围ID

        Returns:
            Response 对象
        """
        return self.post("/platform/businessScope/detail", json={"id": scope_id})

    def edit_business_scope(self, scope_id, scope_name, remark=None):
        """编辑经营范围

        Args:
            scope_id: 经营范围ID
            scope_name: 经营范围名称（最长20个字符）
            remark: 备注（可选，最长200个字符）

        Returns:
            Response 对象
        """
        payload = {"id": scope_id, "scopeName": scope_name}
        if remark is not None:
            payload["remark"] = remark
        return self.post("/platform/businessScope/edit", json=payload)

    def update_business_scope_status(self, scope_id, is_enabled):
        """修改经营范围状态

        Args:
            scope_id: 经营范围ID
            is_enabled: 状态，1-启用, 0-禁用

        Returns:
            Response 对象
        """
        return self.post("/platform/businessScope/updateStatus", json={"id": scope_id, "isEnabled": is_enabled})

    def delete_business_scope(self, scope_id):
        """删除经营范围

        Args:
            scope_id: 经营范围ID

        Returns:
            Response 对象
        """
        return self.post("/platform/businessScope/del", json={"id": scope_id})