import re
import requests
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.auth.login import isValid


class AchievementParser:
    """成绩解析器类"""

    def __init__(self):
        self.base_url = 'http://oa.csmu.edu.cn:8099/jsxsd/kscj/cjcx_list'
        self.json_file = 'achievement.json'

    def _clean_html_content(self, content: str) -> str:
        """清理HTML内容中的换行符和制表符"""
        content = re.sub(r'\r', '', content)
        content = re.sub(r'\n', '', content)
        content = re.sub(r'\t', '', content)
        return content

    def _extract_table_rows(self, content: str) -> List[str]:
        """提取表格行数据"""
        rows = re.findall('<tr.*?>.*?</tr>', content)
        # 移除表头行
        if len(rows) >= 2:
            rows = rows[2:]
        return rows

    def _clean_row_data(self, row: str) -> str:
        """清理单行数据"""
        replacements = [
            ('align="left"', ""),
            (' ', ""),
            ('<tr>', ""),
            ('</tr>', ""),
            ('</td>', ""),
            ('style=" color:red;"', ""),
            ('<!-- 由于成绩项目基本不会改动，未做对应变化。 -->', ""),
            ('<!--控制绩点显示-->', ""),
            ('<!--控制成绩显示-->', ""),
            ('<!--技能成绩-->', ""),
            ('<!--平时成绩-->', ""),
            ('<!--卷面成绩-->', ""),
            ('<td style=" ">', "<td>"),
            ('<tdstyle="">', "<td>"),
            ('<tdstyle="color:red;">', "<td>"),
            ('</a>', "")
        ]

        for old, new in replacements:
            row = row.replace(old, new)

        return row

    def _parse_row_to_dict(self, row_data: List[str]) -> Dict[str, Any]:
        """将行数据解析为字典格式"""
        if len(row_data) < 16:
            raise ValueError(f"行数据不完整，期望16个字段，实际{len(row_data)}个")

        # 提取成绩信息
        grade_match = re.findall(r'zcj=(\d{2}|通过)', str(row_data[4]))
        grade = grade_match[0] if grade_match else row_data[4]

        return {
            "xnxqmc": row_data[1],   # 学年学期
            "kcbh": row_data[2],     # 课程编号
            "kcmc": row_data[3],     # 课程名称
            "kczcj": grade,          # 课程成绩
            "jncj": row_data[5],     # 技能成绩
            "pscj": row_data[6],     # 平时成绩
            "jmcj": row_data[7],     # 卷面成绩
            "cjbz": row_data[8],     # 成绩标志
            "xf": row_data[9],       # 学分
            "ksxz": row_data[10],    # 考试性质(正常考试，补考)
            "zxs": row_data[11],     # 学时
            "cjjd": row_data[12],    # 绩点
            "khfs": row_data[13],    # 考核方式
            "kcsx": row_data[14],    # 课程属性
            "kcxz": row_data[15],    # 课程性质
        }

    def _save_to_json(self, data: List[Dict[str, Any]]) -> None:
        """保存数据到JSON文件"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_from_json(self) -> Optional[List[Dict[str, Any]]]:
        """从JSON文件加载数据"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def fetch_achievements(self) -> List[Dict[str, Any]]:
        """获取成绩数据"""
        try:
            # 准备请求数据
            data = {"kksj": "", "kcxz": "", "kcmc": "", "xsfs": "max"}

            # 发送请求
            response = requests.post(
                self.base_url,
                data=data,
                cookies=isValid().cookies
            )
            response.raise_for_status()

            # 解析HTML内容
            content = self._clean_html_content(response.text)
            rows = self._extract_table_rows(content)

            achievements = []
            for row in rows:
                try:
                    cleaned_row = self._clean_row_data(row)
                    row_data = cleaned_row.split('<td>')

                    # 移除第一个空元素
                    if row_data and row_data[0] == '':
                        row_data = row_data[1:]

                    if len(row_data) >= 16:
                        achievement = self._parse_row_to_dict(row_data)
                        achievements.append(achievement)

                except (ValueError, IndexError) as e:
                    print(f"解析行数据时出错: {e}")
                    continue

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
