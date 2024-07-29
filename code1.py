import ddddocr
import time


###识别技术
def code_ocr(username,session):
    try:
        image_url = 'CSMU_code'+username+'.png'
        res = session.get('http://oa.csmu.edu.cn:8099/jsxsd/verifycode.servlet?t='+str(time.time()))
        # 不知道啥原因。
        cookies = res.cookies.items()
        if res.status_code == 200:
            open(image_url, mode='wb').write(res.content)  # 将内容写入图片
        # del res
        image = open(image_url, 'rb')
        ocr = ddddocr.DdddOcr()
        code = ocr.classification(image.read())
        image.close()
        print(code)
        return code
    except:
        return "验证码有问题"