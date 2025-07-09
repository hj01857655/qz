import requests
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.auth.session_manager import get_session, ensure_logged_in


class AchievementParser:
    """成绩解析器类"""

    def __init__(self):
        self.base_url = 'http://oa.csmu.edu.cn:8099/jsxsd/kscj/cjcx_list'
        self.json_file = 'achievement.json'

    def _parse_html_table(self, html_content: str) -> List[Dict[str, Any]]:
        """
        使用BeautifulSoup解析HTML表格

        Args:
            html_content: HTML内容

        Returns:
            解析后的成绩数据列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找成绩表格
        table = soup.find('table', {'id': 'dataList'})
        if not table:
            print("❌ 未找到成绩表格")
            return []

        achievements = []
        rows = table.find_all('tr')

        # 跳过表头行
        for i, row in enumerate(rows[1:], 1):  # 从第二行开始
            try:
                cells = row.find_all('td')
                if len(cells) < 16:
                    print(f"⚠️ 第{i}行数据不完整，跳过")
                    continue

                # 提取各个字段的文本内容
                def get_cell_text(cell):
                    """提取单元格文本，处理链接等特殊情况"""
                    # 如果包含链接，提取链接文本
                    link = cell.find('a')
                    if link:
                        return link.get_text(strip=True)
                    return cell.get_text(strip=True)

                # 解析成绩数据
                achievement = {
                    "序号": get_cell_text(cells[0]),
                    "xnxqmc": get_cell_text(cells[1]),    # 开课学期
                    "kcbh": get_cell_text(cells[2]),      # 课程编号
                    "kcmc": get_cell_text(cells[3]),      # 课程名称
                    "kczcj": get_cell_text(cells[4]),     # 总成绩
                    "jncj": get_cell_text(cells[5]),      # 技能成绩
                    "pscj": get_cell_text(cells[6]),      # 平时成绩
                    "jmcj": get_cell_text(cells[7]),      # 卷面成绩
                    "cjbz": get_cell_text(cells[8]),      # 成绩标志
                    "xf": get_cell_text(cells[9]),        # 学分
                    "ksxz": get_cell_text(cells[10]),     # 考试性质
                    "zxs": get_cell_text(cells[11]),      # 总学时
                    "cjjd": get_cell_text(cells[12]),     # 绩点
                    "khfs": get_cell_text(cells[13]),     # 考核方式
                    "kcsx": get_cell_text(cells[14]),     # 课程属性
                    "kcxz": get_cell_text(cells[15]),     # 课程性质
                }



                # 数据清理和验证
                if achievement["kcmc"]:  # 确保课程名称不为空
                    achievements.append(achievement)

            except Exception as e:
                print(f"❌ 解析第{i}行时出错: {e}")
                continue

        return achievements

    def _save_to_json(self, data: List[Dict[str, Any]]) -> None:
        """保存数据到JSON文件"""
        # 确保data目录存在
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)

        json_path = data_dir / self.json_file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_from_json(self) -> Optional[List[Dict[str, Any]]]:
        """从JSON文件加载数据"""
        try:
            data_dir = Path(__file__).parent.parent.parent / "data"
            json_path = data_dir / self.json_file
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def fetch_achievements(self) -> List[Dict[str, Any]]:
        """获取成绩数据"""
        try:
            # 确保已登录
            if not ensure_logged_in():
                print("❌ 登录失败，无法获取成绩数据")
                return []

            # 准备请求数据
            data = {"kksj": "", "kcxz": "", "kcmc": "", "xsfs": "max"}

            # 使用全局session发送请求
            session = get_session()
            response = session.post(self.base_url, data=data, timeout=30)
            response.raise_for_status()



            # 使用BeautifulSoup解析HTML表格
            achievements = self._parse_html_table(response.text)

            # 保存到文件
            self._save_to_json(achievements)
            return achievements

        except requests.RequestException as e:
            print(f"网络请求失败: {e}")
            # 尝试从本地文件加载
            cached_data = self._load_from_json()
            return cached_data if cached_data else []

        except Exception as e:
            print(f"获取成绩数据时发生未知错误: {e}")
            # 尝试从本地文件加载
            cached_data = self._load_from_json()
            return cached_data if cached_data else []


def achievement() -> List[Dict[str, Any]]:
    """
    获取成绩信息的主函数

    Returns:
        List[Dict[str, Any]]: 成绩数据列表
    """
    parser = AchievementParser()
    return parser.fetch_achievements()


if __name__ == "__main__":
    # 测试代码
    results = achievement()
    print(f"成功获取 {len(results)} 条成绩记录")
