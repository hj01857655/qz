import ddddocr
import time
import requests  # 确保requests库已导入


'''
识别验证码
username: 用户名
session: 会话
'''
def code_ocr(username, session):
    try:
        image_url = 'CSMU_code' + username + '.png'
        response = session.get('http://oa.csmu.edu.cn:8099/jsxsd/verifycode.servlet?t=' + str(time.time()))
        
        # 检查响应状态码
        if response.status_code == 200:
            with open(image_url, mode='wb') as file:
                file.write(response.content)  # 将内容写入图片

            with open(image_url, 'rb') as image:
                ocr = ddddocr.DdddOcr()
                code = ocr.classification(image.read())
                print(code)
                return code
        else:
            print("获取验证码失败，状态码：", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("请求异常：", e)
        return None
    except Exception as e:
        print("验证码识别过程中出现问题：", e)
        return None
