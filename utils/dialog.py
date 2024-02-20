import sys
import os
from PyQt6.QtWidgets import QDialog, QTableWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QApplication, QComboBox
from PyQt6.QtGui import QFont
import uuid


class AlertDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('方案设置')
        self.setFont(QFont('微软雅黑', 12))
        self.setFixedWidth(750)
        self.setFixedHeight(450)
        VBox = QVBoxLayout()
        
        table = TableWidget()
        VBox.addWidget(table)
        
       
        btn_add = QPushButton('添加')
        btn_add.clicked.connect(table._addRow)
        
        btn_save = QPushButton('保存')
        btn_save.clicked.connect(table._event_save_item)

        btn_remove = QPushButton('移除')
        btn_remove.clicked.connect(table._removeRow)
        
        VBox.addWidget(btn_add)
        VBox.addWidget(btn_save)
        VBox.addWidget(btn_remove)
        #  设置总体布局
        self.setLayout(VBox)



class TableWidget(QTableWidget):
    
    def __init__(self) -> None:
        super().__init__(0, 5)
        self.rows = 0
        Labels = ['投注彩种', '模式名称', '投注码量', '投注金额','uid']
        self.setCellWidget(0,0, self._combox())
        self.setHorizontalHeaderLabels(Labels)
        self.setColumnHidden(4, True)
        self.verticalHeader().setDefaultSectionSize(30)
        self.horizontalHeader().setDefaultSectionSize(160)
        self._load_datas()
        
    def _addRow(self):
            rowCount = self.rowCount()
            self.insertRow(rowCount)
            self.setCellWidget(rowCount, 0, self._combox())
            item = QTableWidgetItem('随机投注')
            self.setItem(rowCount,1,item)
            # self.combox.addItem('极速赛车')
            # self.combox.addItem('极速飞艇')
    
    def _combox(self):
        combox = QComboBox()
        combox.addItem('极速赛车')
        combox.addItem('极速飞艇')
        return combox

    
    def _removeRow(self):
        if self.rowCount() > 0:
            self.removeRow(self.rowCount() - 1)
    

    def _event_save_item(self):
        if self.rowCount() <= 0:
            return
        items = []
        rowCount = self.rowCount()
        columnCount = self.columnCount()

        for rowIndex, x in enumerate(range(rowCount), start=1):
            old_list = []
            for j in range(columnCount):
                if j == 0:
                    old_list.append(self.cellWidget(x, 0).currentText())
                elif j == 4:
                    old_list.append(str(uuid.uuid1()))
                elif self.item(x, j):
                    old_list.append(self.item(x, j).text())

            items.append(old_list)

        self._toDatas(items)
    
    # 加载数据
    def _load_datas(self):
        if not os.path.exists('./resources/data.json'):
            return
        with open('./resources/data.json', 'r', encoding='utf-8') as fo:
            file = fo.read()
            if not file:
                return
            column_list = file.split('\n')

            for row, line_list in enumerate(column_list):
                if not line_list:
                    continue
                self.insertRow(self.rows)
                for colum, colum_str in enumerate(line_list.split('\t')):
                    if colum == 0:
                        self.setCellWidget(row, colum, self._addCombox(colum_str))
                    item = QTableWidgetItem(colum_str)
                    self.setItem(row, colum, item)
                self.rows += 1
    
    def _addCombox(self, val):
        combox = QComboBox()
        combox.addItem(val)
        if val == '极速飞艇':
            combox.addItem('极速赛车')
        else:
            combox.addItem('极速飞艇')
        return combox
    
    
    # 保存数据
    def _toDatas(self, items):
        # 把原有的内容清除
        os.remove('./resources/data.json')
        # 写入新的内容
        for item in items:
            with open('./resources/data.json', 'a', encoding='utf-8') as fw:
                fw.write('\t'.join(item) + '\n')

    
    
    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AlertDialog()
    demo.show()
    sys.exit(app.exec())
