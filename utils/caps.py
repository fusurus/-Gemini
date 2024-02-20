import requests
import base64
import cv2

from typing import Tuple


class Captcha:

    def __init__(self):
        self.session = requests.session()

    def generate(self, url: str) -> bool:
        """获取滑块图片"""
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                raise RuntimeError(f"请求失败: {response.status_code}")
            data = response.json()
            self.position_y = data["result"]["positionY"]
            self.uuid = data["result"]["uuid"]
            background_image = data["result"]["backgroundImage"][22:]
            puzzle_image = data["result"]["puzzleImage"][22:]
            with open("backimg.png", "wb") as f:
                f.write(base64.b64decode(background_image))
            with open("puzzimg.png", "wb") as f:
                f.write(base64.b64decode(puzzle_image))
            return True
        except Exception as e:
            print(f"图片验证码请求失败: {e}")
            return False

    def validate(self, url: str) -> Tuple[str, str]:
        """识别滑动距离"""
        try:
            back_rgb = cv2.imread("backimg.png")
            back_gray = cv2.cvtColor(back_rgb, cv2.COLOR_BGR2GRAY)
            puzz_rgb = cv2.imread("puzzimg.png", 0)
            res = cv2.matchTemplate(back_gray, puzz_rgb, cv2.TM_CCOEFF_NORMED)
            loc = cv2.minMaxLoc(res)
            position_x = loc[2][0]
            data = {"positionX": position_x, "positionY": self.position_y, "uuid": self.uuid}
            headers = {"accept": "application/json, text/plain, */*"}
            response = self.session.post(url, json=data, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(f"请求失败: {response.status_code}")
            data = response.json()
            if data["message"] != "验证成功":
                raise RuntimeError("验证失败")
            return data["result"]["cryptograph"], data["result"]["code"]
        except Exception as e:
            print(f"验证失败: {e}")
            return "", ""


if __name__ == "__main__":
    captcha = Captcha()
    captcha.generate("https://sg978.vip/web/rest/captcha/generate")
    cryptograph, code = captcha.validate("https://sg978.vip/web/rest/captcha/validate")
    print(f"cryptograph: {cryptograph}")
    print(f"code: {code}")
