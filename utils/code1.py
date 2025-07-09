import ddddocr
import time
import requests
import os
import warnings

# 抑制ONNX Runtime警告
os.environ['ORT_LOGGING_LEVEL'] = '3'  # 只显示错误级别的日志
warnings.filterwarnings('ignore', category=UserWarning, module='onnxruntime')

# PIL兼容性补丁
try:
    from PIL import Image
    # 为了兼容新版本的Pillow，添加ANTIALIAS别名
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass


def clean_old_captcha_files(captcha_dir, max_age_hours=24):
    """
    清理旧的验证码文件

    Args:
        captcha_dir: 验证码目录
        max_age_hours: 文件最大保留时间（小时）
    """
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in captcha_dir.glob("captcha_*.png"):
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                file_path.unlink()
                print(f"🗑️ 清理旧验证码文件: {file_path.name}")
    except Exception as e:
        print(f"⚠️ 清理验证码文件时出错: {e}")


def code_ocr(username, session, max_retries=3):
    """
    识别验证码

    Args:
        username: 用户名
        session: 会话对象
        max_retries: 最大重试次数

    Returns:
        验证码字符串或None
    """
    import os
    from pathlib import Path

    # 确保验证码目录存在
    captcha_dir = Path(__file__).parent.parent / "data" / "captcha"
    captcha_dir.mkdir(parents=True, exist_ok=True)

    # 清理旧的验证码文件
    clean_old_captcha_files(captcha_dir)

    import random

    for attempt in range(max_retries):
        try:
            print(f"🔍 正在获取验证码... (尝试 {attempt + 1}/{max_retries})")

            # 添加随机延迟，避免请求过于频繁
            if attempt > 0:
                delay = random.uniform(3, 8)  # 3-8秒随机延迟
                print(f"⏳ 等待 {delay:.1f} 秒避免请求过于频繁...")
                time.sleep(delay)

            # 生成验证码图片文件名
            timestamp = int(time.time())
            image_path = captcha_dir / f'captcha_{username}_{timestamp}.png'

            # 先访问主页面建立会话
            try:
                main_page = session.get(
                    'http://oa.csmu.edu.cn:8099/jsxsd',
                    timeout=10
                )
                print(f"🌐 主页面访问状态: {main_page.status_code}")

                # 访问主页面后稍作等待
                time.sleep(random.uniform(1.5, 3))

            except Exception as e:
                print(f"⚠️ 访问主页面失败: {e}")

            # 获取验证码图片，添加更多参数模拟浏览器行为
            timestamp_ms = int(time.time() * 1000)
            response = session.get(
                'http://oa.csmu.edu.cn:8099/jsxsd/verifycode.servlet',
                params={
                    't': str(timestamp_ms),
                    '_': str(timestamp_ms + random.randint(1, 999))
                },
                headers={
                    'Referer': 'http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                },
                timeout=15
            )

            # 检查响应状态码
            if response.status_code == 200:
                print(f"🔍 验证码响应大小: {len(response.content)} 字节")
                print(f"🔍 响应Content-Type: {response.headers.get('Content-Type', 'Unknown')}")

                # 检查响应内容是否为空
                if len(response.content) == 0:
                    print("⚠️ 服务器返回空的验证码内容")
                    continue

                # 检查是否是HTML错误页面
                if response.headers.get('Content-Type', '').startswith('text/html'):
                    print("⚠️ 服务器返回HTML页面而不是图片")
                    print(f"🔍 响应内容前100字符: {response.text[:100]}")
                    continue

                # 保存验证码图片
                with open(image_path, mode='wb') as file:
                    file.write(response.content)

                print(f"✅ 验证码图片已保存: {image_path}")

                # 等待文件写入完成
                time.sleep(0.1)

                # 检查文件是否存在且有内容
                if not image_path.exists():
                    print(f"⚠️ 验证码文件不存在: {image_path}")
                    continue

                file_size = image_path.stat().st_size
                print(f"🔍 验证码文件大小: {file_size} 字节")

                if file_size == 0:
                    print("⚠️ 验证码图片文件为空")
                    continue

                # 使用ddddocr识别验证码
                with open(image_path, 'rb') as image_file:
                    try:
                        ocr = ddddocr.DdddOcr()  # 创建OCR对象
                        image_bytes = image_file.read()

                        print(f"🔍 读取到的图片数据大小: {len(image_bytes)} 字节")

                        if len(image_bytes) == 0:
                            print("⚠️ 验证码图片数据为空")
                            continue

                        code = ocr.classification(image_bytes)

                        # 验证码基本格式检查
                        if code and len(code) >= 4:
                            print(f"🎯 验证码识别成功: {code}")

                            # 保留文件用于调试，不立即删除
                            # try:
                            #     os.remove(image_path)
                            # except:
                            #     pass

                            return code
                        else:
                            print(f"⚠️ 验证码格式异常: {code} (长度: {len(code) if code else 0})")

                    except Exception as ocr_error:
                        print(f"❌ OCR识别失败: {ocr_error}")

                        # 如果是PIL相关错误，尝试使用备用方法
                        if "ANTIALIAS" in str(ocr_error):
                            print("🔧 检测到PIL兼容性问题，尝试修复...")
                            try:
                                # 重新导入并设置兼容性
                                from PIL import Image
                                if not hasattr(Image, 'ANTIALIAS'):
                                    Image.ANTIALIAS = Image.LANCZOS
                                    print("✅ PIL兼容性补丁已应用")
                            except Exception as patch_error:
                                print(f"❌ 兼容性补丁失败: {patch_error}")

                # 保留失败的图片文件用于调试
                # try:
                #     if image_path.exists():
                #         os.remove(image_path)
                # except:
                #     pass

            else:
                print(f"❌ 获取验证码失败，状态码: {response.status_code}")

        except requests.exceptions.Timeout:
            print("⏰ 获取验证码超时")
        except requests.exceptions.RequestException as e:
            print(f"🌐 网络请求异常: {e}")
        except Exception as e:
            print(f"❌ 验证码识别过程中出现问题: {e}")

            # 如果是PIL相关错误，提供解决建议
            if "ANTIALIAS" in str(e):
                print("\n💡 解决建议:")
                print("1. 运行: pip install 'Pillow==9.5.0'")
                print("2. 或运行: pip install --upgrade ddddocr")
                print("3. 重启程序")

        # 短暂延迟后重试
        if attempt < max_retries - 1:
            print("⏳ 等待1秒后重试...")
            time.sleep(1)

    print(f"❌ 验证码识别失败，已尝试 {max_retries} 次")
    return None
