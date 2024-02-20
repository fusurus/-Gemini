import contextlib
import requests
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
QLabel, QPushButton, QLineEdit, QStyleFactory, QTableWidget, QMessageBox, QStatusBar, QTableWidgetItem, QAbstractItemView, QHeaderView)
from PyQt6.QtGui import QFont, QIcon, QBrush, QColor
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, Qt
import sys
from utils.lotteryAPI import Lottery
import os
import time
import random


deformation = {
            'PK10JSC': '极速赛车',
            'LUCKYSB': '极速飞艇'
        }

odds = None

isStop = False

 
class WinDows(QWidget):
    
    def __init__(self) -> None:
        super().__init__()
        # 设置窗口风格
        self.setStyle(QStyleFactory.create('Fusion'))
        # 设置字体和大小
        self.setFont(QFont('微软雅黑', 14))
        # 设置窗口图标
        self.setWindowIcon(QIcon('my-彩色.png'))
        # 设置窗口标题
        self.setWindowTitle('彩娱乐')
        # 限制最宽
        self.setFixedWidth(1060)
        # 限制最高
        self.setFixedHeight(600)
        
        VBox = QVBoxLayout()
        
        VBox.addLayout(self.create_login_box())
        VBox.addLayout(self.create_table_box())
        # 添加小部件
        VBox.addWidget(self.create_statusbar_box())
        
        self.setLayout(VBox)
        
    # 程序退出事件
    def closeEvent(self, event):
        """程序退出事件"""
        reply = QMessageBox.question(self, '彩娱乐', '您确定要退出程序吗?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
    
    # 创建登录控件
    def create_login_box(self):
        """创建登录控件"""
        # 垂直布局
        HBox = QHBoxLayout()
        # 账号
        lable_u = QLabel('账号:')
        self.edit_u = QLineEdit('hhb1188')
        self.edit_u.setMaxLength(12)
        self.edit_u.setPlaceholderText('请输入账户')
        box_list = [lable_u, self.edit_u]
        # 密码
        lable_p = QLabel('密码:')

        self.edit_p = QLineEdit('159632aA')
        self.edit_p.setEchoMode(self.edit_p.EchoMode.Password)
        self.edit_p.setMaxLength(12)
        self.edit_p.setPlaceholderText('请输入密码')
        box_list.extend((lable_p, self.edit_p))
        # 登录按钮
        self.btn_login = QPushButton('登录')
        self.btn_login.clicked.connect(self.event_onButtonClick)
        box_list.append(self.btn_login)

        self.btn_add = QPushButton('添加')
        self.btn_add.clicked.connect(self.event_btn_add)
        box_list.append(self.btn_add)

        for box in box_list:
            HBox.addWidget(box)

        # 添加弹簧
        HBox.addStretch()

        self.btn_start = QPushButton('启动')
        self.btn_start.setEnabled(False)  # 设置无法点击 
        self.btn_start.clicked.connect(self.event_onStartClick)
        HBox.addWidget(self.btn_start)
        return HBox
    
    # 启动事件
    def event_onStartClick(self):
        """启动事件"""

        if self.btn_start.text() == '启动':
            self._extracted_from_event_onStartClick_5()
        else:
            self.btn_start.setText('启动')
            self.thread[1].stop()
            self.thread[2].stop()


    def _extracted_from_event_onStartClick_5(self):
        self.btn_start.setText('停止')
        self.thread = {1: WorkerLoop(lottery='PK10JSC')}
        self.thread[2] = WorkerLoop(lottery='LUCKYSB')
        self.thread[1].any_signal.connect(self._signalCallback)
        self.thread[2].any_signal.connect(self._signalCallback)
        self.thread[1].start()
        self.thread[2].start()
    
    # 信号回调
    def _signalCallback(self, val):
        from utils.dialog import TableWidget
        while True:
                result = Lottery.lastResult(val['lottery'])
                if result:
                    break
        result = Lottery.lastResult(val['lottery'])
        numBer = result['result']['drawNumber']
        draws = result['result']['result']
        lottery = val['lottery']

        if 'bet' in val:        # 投注 
            self.lab_state.setText(f"{deformation[lottery]} | {numBer} | {draws}")
            self._beting(val['lottery'], val['number'], draws)   # 投注到网站

        elif 'draw' in val:   # 开奖
            print(lottery, numBer, draws)
            # 把开奖信息写到状态栏的标签
            self.lab_state.setText(f"{deformation[lottery]} | {numBer} | {draws}")
            # 判断中挂
            self._WinorNot(deformation[lottery], numBer, draws)
            
        
    # 投注
    def _beting(self, lottery, number, draws):

        if not os.path.exists('./resources/data.json'):
            return
        if isStop:
            return
        # 打开硬盘的文件，是否需要投注
        with open('./resources/data.json', 'r', encoding='utf-8') as fileLine:
            for line in fileLine:
                line_list = line.split('\t')
                if len(line_list) != 5:
                    continue
                if line_list[0] != deformation[lottery]:
                    continue

                uid = line_list[4].strip()

                # 遍历表格 检索是否已投注

                flag, tags, pos, index= self._traverseTable(lottery, number-1, uid)    # 返回逻辑， 期数， 投注位置


                amounts = line_list[3].split('-')        # 投注金额 分割

                betContent_list = self.card_dealer(int(line_list[2]))          # 投注号码

                rank = random.randint(1, 10)        # 投注位置

                # 是否首次投注？
                if index is None:    
                    tags = 0
                    index = 0

                elif flag:
                    tags = 0
                    index = 0
    
                else:
                    index += 1
                    tags += 1

                if tags >= len(amounts):
                    tags = 0
                    index = 0

                amount = int(amounts[tags].strip())

                betContent = '-'.join(str(i) for i in betContent_list)

                Lottery.bets(lottery=lottery, drawNumber=number, ranks=rank, odds=odds, contents=betContent, amount=amount)

                infos = [deformation[lottery], number, rank, betContent, tags, amount, '等待开奖', time.strftime('%H:%M:%S'), uid, str(index)]
                # 插入到表格
                self._insertTable(infos)

    # 发牌器
    def card_dealer(self, number):
        list1 =[]                          
        # list1 = [i+1 for i in range(TOTAL_NUMBER)] # 初始化原牌堆，方法无所谓，完整而不重复即可
        for i in range(10):
            list1.append(i+1)
        list2 = []                                  # 新牌堆开始时为空
        for i in range(number):
            x = random.choice(list1)
            list2.append(x)         # 从原牌堆中随机抽取一张牌放到新牌堆中
            list1.remove(list2[i])   # 从原牌堆中删除刚才抽到的那张牌
        list2.sort()

        return list2
    
    # 遍历表格中挂状态
    def _traverseTable(self, lottery, number, uid):
        """
        遍历表格
        lottery: 彩种
        number: 期号
        """
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        for row in range(rows):
            for _ in range(columns):
                _lottery = self.table.item(row, 0).text()
                _number = self.table.item(row, 1).text()
                _pos = self.table.item(row,2).text()
                if self.table.item(row, 8) is None:
                    uid = ''
                else:
                    _uid = self.table.item(row, 8).text()
                    _index = int(self.table.item(row, 9).text())
                if _lottery == deformation[lottery] and _number == str(number) and _uid == uid:
                    stauts = self.table.item(row, 6).text()
                    idx = self.table.item(row, 4).text()
                    if stauts == '中':
                        return True, int(idx), _pos, _index
                    return False, int(idx), _pos, _index
        return True, 0, None, None
    
    # 插入表格
    def _insertTable(self, items):
        rows = self.table.rowCount()
        self.table.insertRow(rows)      # 插入新的一行
        for loumn, item in enumerate(items):
            info = QTableWidgetItem(str(item))
            self.table.setItem(rows, loumn, info)
            info.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.scrollToItem(info, QAbstractItemView.ScrollHint.PositionAtBottom)
    
    # 中或者挂
    def _WinorNot(self, lottery, number, drawResult):
        """
        lottery: 投注彩种
        number: 当前期号
        drawResult: 开奖结果
        """
        if self.table.rowCount() == 0:
            return

        rows = self.table.rowCount()
        column = self.table.columnCount()

        for row in range(rows):
            for _ in range(column):
                _lottery = self.table.item(row, 0).text()       # 投注彩种
                _number = self.table.item(row, 1).text()        # 投注期号
                if _lottery == lottery and _number == number:
                    _pos = self.table.item(row, 2).text()       # 投注位置
                    _content = self.table.item(row, 3).text()   # 投注内容
                    if self._determine(_pos, _content, drawResult):

                        item = QTableWidgetItem('中')
                        item.setBackground(QBrush(QColor(0,128,0)))

                    else:
                        item = QTableWidgetItem('挂')
                        item.setBackground(QBrush(QColor(200,0,0)))

                    self.table.setItem(row, 6, item)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # 跟踪显示
                    self.table.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtBottom)
                    
        self.table.repaint()
        
    # 决定是否中奖
    def _determine(self, pos, content, result):
        content_list = content.split('-')
        result_list = result.split(',')

        for ct in content_list:
            if result_list[int(pos)-1] == ct:
                return True
        return False
    
    
    # 鼠标添加事件
    def event_btn_add(self):
        """鼠标添加事件"""
        from utils.dialog import AlertDialog
        alert = AlertDialog()
        alert.exec()
    
    # 创建表格控件
    def create_table_box(self):
        """创建标签控件"""
        HBox = QHBoxLayout()

        self.table = QTableWidget(0, 10)
        # 不能被编辑
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 隐藏索引
        self.table.verticalHeader().setVisible(False)
        # 设置字体色
        self.table.setAlternatingRowColors(True)
        # 设置样式颜色
        self.table.setStyleSheet(f"""
        ::section {{
            background-color: #962D2E;
            color: white;
            border: none;
        }}
        """
        )
        # 设置表头固定宽度
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setFont(QFont('微软雅黑', 14))
        HBox.addWidget(self.table)
        
        title_list = ['投注彩种', '投注期号', '投注位置', '投注号码', '投注期数', '投注金额', '投注状态', '投注时间', 'uid', 'index']
        
        self.table.setHorizontalHeaderLabels(title_list)
        # self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 260)
        self.table.setColumnWidth(4, 60)
        self.table.setColumnWidth(7, 160)
        self.table.setColumnHidden(8, True)
        self.table.setColumnHidden(9, True)
        return HBox
    
    # 登录点击事件
    def event_onButtonClick(self):
        """登录点击事件"""
        global odds
        username = self.edit_u.text()
        password = self.edit_p.text()

        if not username or not password:
            QMessageBox.information(self, '彩娱乐', '账号或者密码不能为空')
            return

        result = Lottery.weblogin(username, password)
        if not result:
            return

        if result['message'] == '登录成功':
            self._login_success()
        else:
            QMessageBox.information(self, '彩娱乐', result['message'])

    def _login_success(self):
        self.btn_start.setEnabled(True)
        self.btn_login.setEnabled(False)

        try:
            odds = Lottery.odds()['result']['B1_1']
        except Exception:
            odds = Lottery.odds('LUCKYSB')['result']['B1_1']

        self.lab_state.setText('登录成功' + ' | 赔率:' + str(odds))

        self.worker1 = WorkerUpdate()
        self.worker1.start()
        self.worker1.UpdateSignal.connect(self._update_label_status)

    # 创建状态栏控件 
    def create_statusbar_box(self):
        """创建状态栏控件"""
        barBox = QStatusBar()
        
        self.lab_state = QLabel()
        self.lab_state.setText('未登录')
        
        self.lab_balance = QLabel()
        self.lab_balance.setText('余额:')
        
        self.lab_betting = QLabel()
        self.lab_betting.setText('下注:')
        
        self.lab_result = QLabel()
        self.lab_result.setText('输赢:')

        self.lab_water = QLabel()
        self.lab_water.setText('流水:')
        
        barBox.addPermanentWidget(self.lab_state, stretch=2)
        barBox.addPermanentWidget(self.lab_balance, stretch=1)
        barBox.addPermanentWidget(self.lab_betting, stretch=1)
        barBox.addPermanentWidget(self.lab_result, stretch=1)
        barBox.addPermanentWidget(self.lab_water, stretch=1)

        return barBox
    
    # 更新标签状态
    def _update_label_status(self, val):
        global isStop

        # try:
        #     self.lab_balance.setText('余额:' + str(val['accounts'][0]['balance']))
        #     self.lab_betting.setText('下注:' + str(val['accounts'][0]['betting']))
        #     self.lab_result.setText('输赢:' + str(val['accounts'][0]['result']))
        #     if int(val['accounts'][0]['result']) >= 400:
        #         isStop = True
        #     water = str(round(int(Lottery.todayreport()) * 0.02, 2))
        #     self.lab_water.setText(f'流水：{water}')
        # except Exception:
        #     self.lab_balance.setText('余额:' + str(val['accounts'][0]['balance']))
        
        #########################################################################
        try:
            self.lab_balance.setText('余额:' + str(val['balance']))
            self.lab_betting.setText('下注:' + str(val['betting']))
            self.lab_result.setText('输赢:' + str(val['result']))
            water = str(round(int(Lottery.todayreport()) * 0.02, 2))
            self.lab_water.setText(f'流水：{water}')
        except Exception:
            self.lab_balance.setText('余额:' + str(val['balance']))
    

# 更新用户信息
class WorkerUpdate(QThread):
    """更新用户信息"""
    UpdateSignal =  pyqtSignal(dict)
    
    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            with contextlib.suppress(Exception):
                if result := Lottery.accountbalance():
                    self.UpdateSignal.emit(result['result'])
                self.sleep(5)
        
    def stop(self):
        self.ThreadActive = False
        self.quit()



# 循环倒计时
class WorkerLoop(QThread):
    """开奖循环"""
    any_signal = pyqtSignal(dict)

    def __init__(self, lottery):
        super().__init__()
        self._lottery = lottery
        self._active = True
        self._mutex = QMutex()

    def run(self):
        while self._active:
            try:
                self._mutex.lock()

                # 获取开奖信息
                result = Lottery.multiplePeriod(self._lottery)
                draw_number = int(result['result'][0]['drawNumber'])
                close_time = int(result['result'][0]['closeTime']) / 1000
                current_time = int(result['result'][0]['currentTime']) / 1000
                status = int(result['result'][0]['status'])
                draw_time = int(result['result'][0]['drawTime']) / 1000 + 20

                # 可投注阶段
                if close_time - current_time > 5 and status == 1:
                    self._emit_signal('bet', draw_number)

                # 开奖阶段
                while draw_time > current_time:
                    current_time += 1
                    self.sleep(1)

                self._emit_signal('draw', draw_number)

            except Exception as e:
                print(e)

            finally:
                self._mutex.unlock()

    def stop(self):
        self._active = False
        self.exit()

    def _emit_signal(self, signal_type, draw_number):
        data = {'lottery': self._lottery, signal_type: True, 'number': draw_number}
        self.any_signal.emit(data)

    
def run():
    if not os.path.exists('resources'):
        os.mkdir('resources')
    app = QApplication(sys.argv)
    window = WinDows()
    window.show()
    sys.exit(app.exec())
