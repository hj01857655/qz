#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建数据库和表结构

初始化教务系统所需的数据库
"""

import pymysql
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_config import load_config

logger = logging.getLogger(__name__)

def create_database():
    """创建数据库"""
    try:
        config = load_config()
        
        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=config['mysql']['host'],
            user=config['mysql']['user'],
            password=config['mysql']['password'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            with connection.cursor() as cursor:
                # 创建数据库
                database_name = config['mysql']['database']
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ 数据库 '{database_name}' 创建成功")
                
                # 选择数据库
                cursor.execute(f"USE `{database_name}`")
                
                # 创建用户表
                create_users_table = """
                CREATE TABLE IF NOT EXISTS `users` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `username` varchar(50) NOT NULL,
                    `password` varchar(255) NOT NULL,
                    `remember_me` tinyint(1) DEFAULT 0,
                    `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `username` (`username`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_users_table)
                print("✅ 用户表创建成功")
                
                # 创建成绩表
                create_grades_table = """
                CREATE TABLE IF NOT EXISTS `grades` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `user_id` int(11) NOT NULL,
                    `semester` varchar(20) NOT NULL,
                    `course_code` varchar(20) NOT NULL,
                    `course_name` varchar(100) NOT NULL,
                    `total_score` varchar(10) DEFAULT NULL,
                    `skill_score` varchar(10) DEFAULT NULL,
                    `usual_score` varchar(10) DEFAULT NULL,
                    `exam_score` varchar(10) DEFAULT NULL,
                    `score_flag` varchar(10) DEFAULT NULL,
                    `credits` decimal(3,1) DEFAULT NULL,
                    `exam_type` varchar(20) DEFAULT NULL,
                    `total_hours` int(11) DEFAULT NULL,
                    `grade_point` decimal(3,2) DEFAULT NULL,
                    `assessment_method` varchar(20) DEFAULT NULL,
                    `course_attribute` varchar(20) DEFAULT NULL,
                    `course_nature` varchar(20) DEFAULT NULL,
                    `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    KEY `user_id` (`user_id`),
                    KEY `semester` (`semester`),
                    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_grades_table)
                print("✅ 成绩表创建成功")
                
                # 创建课程表
                create_schedule_table = """
                CREATE TABLE IF NOT EXISTS `schedule` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `user_id` int(11) NOT NULL,
                    `semester` varchar(20) NOT NULL,
                    `week` varchar(10) DEFAULT NULL,
                    `time_slot` varchar(20) NOT NULL,
                    `monday` text DEFAULT NULL,
                    `tuesday` text DEFAULT NULL,
                    `wednesday` text DEFAULT NULL,
                    `thursday` text DEFAULT NULL,
                    `friday` text DEFAULT NULL,
                    `saturday` text DEFAULT NULL,
                    `sunday` text DEFAULT NULL,
                    `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    KEY `user_id` (`user_id`),
                    KEY `semester` (`semester`),
                    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_schedule_table)
                print("✅ 课程表创建成功")
                
                # 提交事务
                connection.commit()
                print("✅ 所有表创建完成")
                
        return True
        
    except Exception as e:
        logger.exception("创建数据库失败")
        print(f"❌ 创建数据库失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        from database.db_config import get_db_connection
        
        conn = get_db_connection()
        if conn:
            print("✅ 数据库连接测试成功")
            conn.close()
            return True
        else:
            print("❌ 数据库连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 教务系统数据库初始化")
    print("=" * 40)
    
    # 创建数据库和表
    if create_database():
        print("\n📊 数据库结构创建完成")
        
        # 测试连接
        if test_database_connection():
            print("\n🎉 数据库初始化成功！")
            print("\n📖 使用说明:")
            print("1. 数据库已创建并可以正常使用")
            print("2. 现在可以启动GUI应用: python gui/app.py")
            print("3. 用户数据将自动保存到数据库中")
            return 0
        else:
            print("\n❌ 数据库连接测试失败")
            return 1
    else:
        print("\n❌ 数据库初始化失败")
        print("请检查:")
        print("1. MySQL服务是否启动")
        print("2. 配置文件中的数据库密码是否正确")
        print("3. 用户是否有创建数据库的权限")
        return 1

if __name__ == "__main__":
    sys.exit(main())
