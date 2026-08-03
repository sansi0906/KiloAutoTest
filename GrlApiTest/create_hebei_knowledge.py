"""
create_hebei_knowledge.py - 创建河北省知识库数据

为河北省及其下属所有市、区随机创建知识库内容，不同 consultType 随机3条以上。
consultType: 1-智能客服, 2-在线客服, 3-智能问答
"""

import sys
import random
sys.path.insert(0, ".")

from api_clients.jeecgboot_client import JeecgBootClient
from utils.area_helper import get_area_tree

# 配置
BASE_URL = "http://172.16.1.165:9200"
USERNAME = "15522719628"
PASSWORD = "123456"
LOGIN_TYPE = 1
WEB_TYPE = 0

# 河北省区域名称
HEBEI_NAME = "河北省"


def find_hebei_areas(tree):
    """从区域树中找出河北省及其下属市、区"""
    hebei_node = None
    for node in tree:
        if node.get("areaName") == HEBEI_NAME:
            hebei_node = node
            break
    
    if not hebei_node:
        return []
    
    areas = []
    children = hebei_node.get("children", [])
    
    for city in children:
        city_name = city.get("areaName")
        city_code = city.get("areaCode")
        city_level = city.get("level")
        
        if city_level == "city":
            areas.append({
                "code": city_code,
                "name": city_name,
                "level": "city",
            })
            
            # 添加区县
            districts = city.get("children", [])
            for district in districts:
                district_name = district.get("areaName")
                district_code = district.get("areaCode")
                district_level = district.get("level")
                
                if district_level == "county":
                    areas.append({
                        "code": district_code,
                        "name": district_name,
                        "level": "county",
                    })
    
    return areas


def create_knowledge_for_areas():
    """为河北省各市、区创建知识库"""
    client = JeecgBootClient(base_url=BASE_URL)
    
    # 登录
    print("登录中...")
    login_resp = client.login(username=USERNAME, password=PASSWORD, login_type=LOGIN_TYPE, web_type=WEB_TYPE)
    if login_resp.status_code != 200:
        print(f"登录失败: {login_resp.text}")
        return
    
    token = login_resp.json().get("data", {}).get("token")
    if not token:
        print("获取 token 失败")
        return
    
    client.set_token(token)
    print(f"登录成功，token: {token[:20]}...")
    
    # 获取区域树
    print("获取区域树...")
    area_tree = get_area_tree(client)
    hebei_areas = find_hebei_areas(area_tree)
    
    if not hebei_areas:
        print("未找到河北省区域数据")
        return
    
    print(f"找到河北省 {len(hebei_areas)} 个区域（含市、区）")
    print(f"前5个区域: {[a['name'] for a in hebei_areas[:5]]}")
    
    # consultType 随机3条以上：1-智能客服, 2-在线客服, 3-智能问答
    consult_types = [1, 2, 3]
    display_positions = [[0, 1], [1], [0]]  # 0-移动端, 1-PC端
    
    created_count = 0
    failed_count = 0
    
    for area in hebei_areas:
        # 每个区域随机选择2-4条知识库
        num_items = random.randint(2, 4)
        
        for i in range(num_items):
            consult_type = random.choice(consult_types)
            display_position = random.choice(display_positions)
            
            title = f"【{area['name']}】知识库-{random.randint(1000, 9999)}"
            content = f"这是{area['name']}的测试知识库内容，咨询类型：{consult_type}，展示位置：{display_position}。"
            
            applicable_area = [{
                "code": area["code"],
                "name": area["name"],
                "level": area["level"],
            }]
            
            try:
                resp = client.save_knowledge(
                    title=title,
                    content=content,
                    consult_type=consult_type,
                    display_position=display_position,
                    applicable_area=applicable_area,
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("code") in ("0", "00"):
                        created_count += 1
                        print(f"[OK] {title} (consultType={consult_type})")
                    else:
                        failed_count += 1
                        print(f"[FAIL] {title}: {data}")
                else:
                    failed_count += 1
                    print(f"[FAIL] {title}: HTTP {resp.status_code}")
            except Exception as e:
                failed_count += 1
                print(f"[ERROR] {title}: {e}")
    
    print("\n" + "=" * 50)
    print(f"创建完成！成功: {created_count}, 失败: {failed_count}")
    print("=" * 50)


if __name__ == "__main__":
    create_knowledge_for_areas()
