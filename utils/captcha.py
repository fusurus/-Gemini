import requests
import base64
import cv2



class Captcha:
    def __init__(self):
        self.ss = requests.session()
    def generate(self, url):
        """获取滑块图片"""
        try:
            resq = self.ss.get(url)
            print(url)
            if resq.status_code == 200:
                # 获取到Y坐标
                self.positionY = resq.json()['result']['positionY']
                # 获取到uuid
                self.uuid = resq.json()['result']['uuid']
                backgroundImage = resq.json()['result']['backgroundImage'][22:]
                puzzleImage = resq.json()['result']['puzzleImage'][22:]
                # 保存背景图片 进行base64解码
                with open('backimg.png', 'wb') as fwbk:
                    fwbk.write(base64.b64decode(backgroundImage))
                # 保存滑块图 进行base64解码
                with open('puzzimg.png', 'wb') as fwbk:
                    fwbk.write(base64.b64decode(puzzleImage))
                return True
        except Exception as err:
            print('图片验证码请求失败:', err)
            return False


    def validate(self, url):
        """识别滑动距离"""
        try:
            # 读取背景图的RGB码
            back_rgb = cv2.imread('./backimg.png')
            # 灰度处理
            back_gray = cv2.cvtColor(back_rgb, cv2.COLOR_BGR2GRAY) # 6
            # 读取滑块的RGB码
            puzz_rgb = cv2.imread('./puzzimg.png', 0)
            # 匹配滑块在背景图的位置
            res = cv2.matchTemplate(back_gray, puzz_rgb, cv2.TM_CCOEFF_NORMED) # 5
            # 获取位置
            loc = cv2.minMaxLoc(res)
            # 获取X的坐标
            positionX = loc[2][0]
            data = {
                'positionX': positionX,
                'positionY': self.positionY,
                'uuid': self.uuid
                }
            headers = {
                'accept': 'application/json, text/plain, */*'
                }
            resq = self.ss.post(url, json=data, headers=headers)
            print(resq.text)
            if resq.status_code == 200 and resq.json()['message'] == '验证成功':
                cryptograph = resq.json()['result']['cryptograph']
                code = resq.json()['result']['code']
                return cryptograph, code
        except Exception as err:
            print('验证失败', err)



if __name__ == '__main__':
    captchas = Captcha()
    captchas.generate('https://sg978.vip/web/rest/captcha/generate')
    captchas.validate('https://sg978.vip/web/rest/captcha/validate')