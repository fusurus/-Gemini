import requests
import random
# 导入滑动识别模块

#from captcha import Captcha

# https://0027cp.vip/mobile5

class LotteryAPI:

    headers = {
        'authority': 'sg978.vip',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'cookie': 'ssid1=cfd648e0cb13ec4926ea5c170e3ee5dd; random=4547; lang=zh_CN'
    }

    # 创建一个会话
    session = requests.session()

    def __init__(self, domain='sg978.vip') -> None:
        self.domain = domain
        

    # 前置条件    
    def __setup(self):
        try:
            from utils.captcha import Captcha
            captchas = Captcha()
            if flag := captchas.generate(f'https://{self.domain}/web/rest/captcha/generate'):
                self.cryptograph, self.code =captchas.validate(f'https://{self.domain}/web/rest/captcha/validate')
                return True
        except Exception as err:
            print('滑动验证失败, 请重试', err)
            return False
         
    def weblogin(self, username, password):
        """
        登录 
        username: 用户名
        password: 密码
        """
        try:
            if self.__setup():
                url = f'https://{self.domain}/web/rest/weblogin'
                data = {
                    'code': self.code,
                    'cryptograph': self.cryptograph,
                    'password': password,
                    'username': username
                }
                resp = self.session.post(url, json=data, headers=self.headers)
                print(resp.text)
                return resp.json()
        except Exception:
            return None
    
    def userinfo(self):
        """用户信息"""
        try:
            url = f'https://{self.domain}/web/rest/member/userInfo'
            resp = self.session.get(url)
            #print(resp.text)
            return resp.json()
        except Exception:
            return None
    
    def odds(self, lottery='PK10JSC'):
        """获取赔率"""
        try:
            url = f'https://{self.domain}/web/rest/member/odds/load?lottery={lottery}'
            resp = self.session.get(url)
            #print(resp.text)
            return resp.json()
        except Exception:
            return None
    
    def lastResult(self, lottery='PK10JSC'):
        """最新开奖结果"""
        try:
            url = f'https://{self.domain}/web/rest/member/lastResult?lottery={lottery}'
            resp = self.session.get(url)
            #print(resp.text)
            return resp.json()
        except Exception:
            return None
    
    def multiplePeriod(self, lottery='PK10JSC'):
        """周期开奖时间"""
        try:
            url = f'https://{self.domain}/web/rest/member/multiplePeriod'
            data = {
                'periodRequests': [
                    {
                        'lottery': lottery
                    }
                ]
            }
            resp = self.session.post(url, json=data)

            return resp.json()
        except Exception:
            return None
    
    def accountbalance(self):
        """账户余额"""
        try:
            url = f'https://{self.domain}/web/rest/member/accountbalance'
            resp = self.session.get(url)
            #print(resp.text)
            return resp.json()
        except Exception:
            return None
    
    def bets(self, drawNumber:str, ranks:list, contents:str, odds:float, amount:int, lottery="PK10JSC"):
        """
        投注
        
        lottery: 彩种
        drawNumber: 期号
        rank: 名次
        contents: 投注内容
        odds: 赔率
        amount: 投注金额
        """
        try:
            url = f'https://{self.domain}/web/rest/member/dragon/bet'

            bets = []
            for rank in ranks:
                betsContent = {'lottery': lottery, 'drawNumber': drawNumber, 'game': f'B{rank}', 'contents': contents, 'amount': amount, 'odds': odds}
                bets.append(betsContent)
            p = {'bets': bets}
            resp = self.session.post(url, json=p, headers=self.headers)
            return resp.json()
        except Exception:
            return None

Lottery = LotteryAPI()


if __name__ == '__main__':
    lotteryAPI =LotteryAPI()
    lotteryAPI.weblogin('fsrs1188', 'aA159632')
    print(lotteryAPI.accountbalance())
    lotteryAPI.bets('32430874', '1', 'X', 1.939, '20')
    lotteryAPI.userinfo()
    lotteryAPI.odds()
    lotteryAPI.lastResult()
    lotteryAPI.multiplePeriod()
    