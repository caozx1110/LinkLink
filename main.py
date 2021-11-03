# coding=utf-8
"""
@author: Cao Zhanxiang
@project: 8-Queens.py
@file: main.py
@date: 2021/10/22
@function: UI main
"""
# pyinstaller -F -w -n LinkLink -i "./img/LinkLink.ico" main.py
import random
import sys
import time

from StartMenuUI import *
from BoardUI import *
# from InitBoardUI import *
from MainProgress import MainProgress
from PyQt5.QtCore import QThread, pyqtSignal, QPoint
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QStyleFactory
from PyQt5.QtGui import QIcon, QPixmap, QBrush, QColor, QPalette, QMouseEvent
from PyQt5.Qt import QAbstractItemView, Qt, QSize
import resource_rc

# 消除动画的线程
class EliminateThread(QThread):
    EliminateFinished = pyqtSignal()
    DirDic = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

    def __init__(self, game=None, unit_path=None):
        super(EliminateThread, self).__init__()
        self.Game = game
        self.UnitAndPath = unit_path
        self.TotalCost = 0

    def Eliminate(self, unit_path):
        x, y = unit_path[0][0]
        path = unit_path[1]
        if self.Game.RuleFlag == 1:
            self.Game.lbl_CurrentCost.setText("当前代价：" + str(unit_path[2]))
            self.TotalCost += unit_path[2]
            self.Game.lbl_TotalCost.setText("总代价：" + str(self.TotalCost))
        # show path
        self.Game.tbw_Board.item(x, y).setBackground(QColor(0, 120, 215))
        self.Game.tbw_Board.viewport().update()
        for p in path:
            x += self.DirDic[p][0]
            y += self.DirDic[p][1]
            self.Game.tbw_Board.item(x, y).setBackground(QColor(0, 120, 215))
            # 更新界面
            self.Game.tbw_Board.viewport().update()
            time.sleep(0.02)

        time.sleep(0.3)
        # 消除
        x1, y1 = unit_path[0][0]
        x2, y2 = unit_path[0][1]
        self.Game.tbw_Board.item(x1, y1).setIcon(QIcon(":/img/img/0.png"))
        self.Game.tbw_Board.item(x2, y2).setIcon(QIcon(":/img/img/0.png"))
        self.Game.tbw_Board.viewport().update()

        # 恢复颜色
        x, y = unit_path[0][0]
        self.Game.tbw_Board.item(x, y).setBackground(QColor(255, 255, 255, 0))
        for p in path:
            x += self.DirDic[p][0]
            y += self.DirDic[p][1]
            self.Game.tbw_Board.item(x, y).setBackground(QColor(255, 255, 255, 0))
        # table设置透明
        tbw_pal = QPalette()
        tbw_pal.setBrush(QPalette.Base, QBrush(QColor(255, 255, 255, 60)))
        self.Game.tbw_Board.setPalette(tbw_pal)
        # 更新
        self.Game.tbw_Board.viewport().update()

    def run(self) -> None:
        for up in self.UnitAndPath:
            self.Eliminate(up)
            time.sleep(0.3)

        self.EliminateFinished.emit()

# main window
class MainWindow(QtWidgets.QWidget, Ui_StartMenuUI):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.BW: BoardWindow
        # self.IW: InitWindow
        self.setWindowIcon(QIcon(':/img/img/LinkLink.ico'))

        # 背景
        self.Pal = QtGui.QPalette()
        self.Pal.setBrush(QPalette.Background, QBrush(QPixmap(":/img/img/background.png").scaled(self.size())))  # 背景图片
        self.Pal.setColor(QPalette.Background, QColor(240, 240, 240))  # 背景颜色
        self.setPalette(self.Pal)
        # self.setAutoFillBackground(True)
        # 主题
        QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
        # 透明度
        self.setWindowOpacity(0.92)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.Pal.setBrush(QPalette.Background, QBrush(QPixmap(":/img/img/background.png").scaled(self.size())))  # 背景图片
        self.setPalette(self.Pal)

    def slot_cbx_Rule_currentIndexChanged(self):
        """
        设定规则槽函数

        :return:
        """
        if self.cbx_Rule.currentIndex() == 1:
            self.ledt_m.setText('5')
            self.ledt_n.setText('5')
            self.ledt_k.setText('12')
            self.ledt_p.setText('12')
        if self.cbx_Rule.currentIndex() == 0:
            self.ledt_m.setText('8')
            self.ledt_n.setText('8')
            self.ledt_k.setText('25')
            self.ledt_p.setText('20')

    def slot_pbt_FormBoard_clicked(self):
        """
        点击生成棋盘槽函数

        :return:
        """
        # 获取输入的m, n, k, p, ObstacleNum, RuleFlag
        try:
            m = int(self.ledt_m.text())
            n = int(self.ledt_n.text())
            k = int(self.ledt_k.text())
            p = int(self.ledt_p.text())
            obstacle_num = int(self.ledt_ObstacleNum.text())
            rule_flag = self.cbx_Rule.currentIndex()

            self.BW = BoardWindow(self, m, n, k, p, obstacle_num, rule_flag)
            self.BW.show()
            self.hide()
        except ValueError:
            self.lbl_Info.setText("Error in m, n, k, p...")
            return None
        else:
            self.lbl_Info.setText("")

    # def slot_pbt_InitBoard_clicked(self):
    #     """
    #     初始化棋盘参数
    #     :return:
    #     """
    #     # 获取输入的m, n, k, p, ObstacleNum, RuleFlag
    #     try:
    #         m = int(self.ledt_m.text())
    #         n = int(self.ledt_n.text())
    #         k = int(self.ledt_k.text())
    #         p = int(self.ledt_p.text())
    #         obstacle_num = int(self.ledt_ObstacleNum.text())
    #         rule_flag = self.cbx_Rule.currentIndex()
    #
    #         # self.IW = InitWindow(self, m, n, k, p, obstacle_num, rule_flag)
    #         self.IW.show()
    #         self.hide()
    #     except ValueError:
    #         self.lbl_Info.setText("Error in m, n, k, p...")
    #         return None
    #     else:
    #         self.lbl_Info.setText("")


# board UI
class BoardWindow(QtWidgets.QWidget, Ui_BoardUI):
    def __init__(self, parent, m=5, n=5, k=12, p=10, obstacle_num=0, rule_flag=0, init_board=None):
        super(BoardWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/img/img/LinkLink.ico'))

        self.Parent = parent

        # record
        self.m = m
        self.n = n
        self.k = k
        self.p = p
        self.ObstacleNum = obstacle_num
        self.RuleFlag = rule_flag

        # MainProgress
        self.Mp = MainProgress()
        self.Mp.FormBoard(m, n, k, p, obstacle_num, init_board)
        self.EThread = EliminateThread()

        # UI
        # 透明度
        self.setWindowOpacity(0.92)
        # 主题
        QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
        # 隐藏表头
        self.tbw_Board.horizontalHeader().setHidden(True)
        self.tbw_Board.verticalHeader().setHidden(True)
        # 隐藏线
        self.tbw_Board.setShowGrid(False)
        # 不可编辑
        self.tbw_Board.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置点击背景颜色仍为白色
        self.tbw_Board.setStyleSheet("QTableWidget{selection-background-color:white;}")
        # 不可点击
        # self.tbw_Board.setEnabled(False)
        self.ShowBoard()

        # table设置透明
        tbw_pal = QPalette()
        tbw_pal.setBrush(QPalette.Base, QBrush(QColor(255, 255, 255, 60)))
        self.tbw_Board.setPalette(tbw_pal)

        # 背景
        self.Pal = QtGui.QPalette()
        self.Pal.setBrush(QPalette.Background, QBrush(QPixmap(":/img/img/background.png").scaled(self.size())))  # 背景图片
        self.Pal.setColor(QPalette.Background, QColor(240, 240, 240))  # 背景颜色
        self.setPalette(self.Pal)
        # self.setAutoFillBackground(True)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.Pal.setBrush(QPalette.Background, QBrush(QPixmap(":/img/img/background.png").scaled(self.size())))  # 背景图片
        self.setPalette(self.Pal)

    def ShowBoard(self):
        # UI处理
        # 清空
        self.tbw_Board.clear()
        # 设置行列数
        self.tbw_Board.setRowCount(self.m + 2)
        self.tbw_Board.setColumnCount(self.n + 2)
        # 设置总大小和各个格子大小
        self.tbw_Board.setFixedSize((self.n + 2) * 50 + 2, (self.m + 2) * 50 + 2)
        for i in range(self.m + 2):
            self.tbw_Board.setRowHeight(i, 50)
        for j in range(self.n + 2):
            self.tbw_Board.setColumnWidth(j, 50)
        # icon size
        self.tbw_Board.setIconSize(QSize(45, 45))
        # 放置图片
        for i in range(self.m + 2):
            for j in range(self.n + 2):
                # label = QLabel()
                # kind = self.Mp.Game.InitBoard.UnitsBoard[i][j].Kind
                # if kind > 0:
                #     label.setPixmap(QPixmap(":/img/img/" + str(kind) + ".png"))
                #     self.Game.setCellWidget(i, j, label)
                # else:
                #     self.Game.setCellWidget(i, j, label)
                item = QTableWidgetItem()
                kind = self.Mp.Game.InitBoard.UnitsBoard[i][j].Kind
                if 40 >= kind >= -1:
                    item.setIcon(QIcon(QPixmap(":/img/img/" + str(kind) + ".png")))
                    self.tbw_Board.setItem(i, j, item)
                else:
                    self.tbw_Board.setItem(i, j, item)
                    # self.Game.item(i, j).setBackground(QColor(0, 120, 215))

        # 设置窗口大小
        # self.setMinimumSize(self.minimumSize())

    def slot_pbt_SolveGame_clicked(self):
        """
        点击求解问题槽函数

        :return:
        """
        self.lbl_Info.setText("Solving...")
        self.pbt_ChangeBoard.setEnabled(False)
        self.pbt_SolveGame.setEnabled(False)
        # 开始求解问题
        # TODO:可以把求解放在生成的时候操作
        self.Mp.SolveGame(rule_flag=self.RuleFlag)
        # connect
        self.Mp.SThread.Solved.connect(self.GameSolved)

    def slot_pbt_ChangeBoard_clicked(self):
        self.lbl_Info.setText("Info...")
        self.pbt_SolveGame.setEnabled(True)
        self.Mp.FormBoard(self.m, self.n, self.k, self.p, self.ObstacleNum)
        self.lbl_CurrentCost.setText("当前代价：0")
        self.lbl_TotalCost.setText("总代价：0")
        self.ShowBoard()

    def GameSolved(self, Path):
        """
        问题求解完成的槽函数

        :param Path: solve thread 返回的路径
        :return:
        """
        # 启动消除的动画线程
        self.lbl_Info.setText("Solved!")
        self.EThread = EliminateThread(self, Path)
        self.EThread.start()
        self.EThread.EliminateFinished.connect(self.EliminateFinished)

    def EliminateFinished(self):
        """
        消除完毕

        :return:
        """
        self.lbl_Info.setText("Eliminated!")
        self.pbt_ChangeBoard.setEnabled(True)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        try:
            self.Parent.Parent.show()
        except:
            self.Parent.show()
        self.close()

# class ImgLabel(QLabel):
#     Released = pyqtSignal(QPoint)
#
#     def __init__(self, parent, kind=1):
#         super(ImgLabel, self).__init__(parent)
#         self.setMaximumSize(50, 50)
#         self.setMinimumSize(50, 50)
#         # 记录初始位置
#         self.InitPos = self.pos()
#         self.Flag = True
#
#         self._startPos = self.pos()
#         self._endPos = self.pos()
#         self._isTracking = False
#         self.Kind = kind
#         self.setPixmap(QPixmap(':/img/img/' + str(self.Kind) + '.png'))
#
#     def setKind(self, kind: int):
#         self.Kind = kind
#         self.setPixmap(QPixmap(':/img/img/' + str(self.Kind) + '.png'))
#
#     # 重写鼠标移动事件
#     def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
#         # if e.button() == Qt.LeftButton:
#         self._endPos = e.pos() - self._startPos
#         self.move(self.pos() + self._endPos)
#
#     # 重写鼠标按下事件
#     def mousePressEvent(self, e: QMouseEvent):
#         # 记录初始位置
#         if self.Flag:
#             self.InitPos = self.pos()
#             self.Flag = False
#         self._isTracking = True
#         self._startPos = QPoint(e.x(), e.y())
#
#     # 重写鼠标松开事件
#     def mouseReleaseEvent(self, e: QMouseEvent):
#         self._isTracking = False
#         self._startPos = None
#         self._endPos = None
#         self.parent().lbl_Info.setText("1")
#         self.Released.emit(QPoint(int(e.windowPos().x()), int(e.windowPos().y())))
#
# class InitWindow(QtWidgets.QWidget, Ui_InitBoardUI):
#     def __init__(self, parent, m=5, n=5, k=12, p=10, obstacle_num=0, rule_flag=0):
#         super(InitWindow, self).__init__()
#         self.setupUi(self)
#
#         self.Parent = parent
#         self.BW: BoardWindow
#
#         # 放置在最顶层
#         self.lbl_Img1.raise_()
#         self.lbl_Img2.raise_()
#         # connect
#         self.lbl_Img1.Released.connect(self.slot_lbl_Img1_Released)
#         self.lbl_Img2.Released.connect(self.slot_lbl_Img2_Released)
#
#         # record
#         self.m = m
#         self.n = n
#         self.k = k
#         self.p = p
#         self.ObstacleNum = obstacle_num
#         self.RuleFlag = rule_flag
#
#         # m x n
#         self.InitBoard = [[0] * n] * m
#
#         # 生成待填列表
#         self.ToAddList = []
#         for i in range(1, p + 1):
#             self.ToAddList.append(i)
#         for i in range(p + 1, k):
#             self.ToAddList.append(random.randint(1, p))
#
#         # 隐藏表头
#         self.tbw_Board.horizontalHeader().setHidden(True)
#         self.tbw_Board.verticalHeader().setHidden(True)
#         # 隐藏线
#         # self.tbw_Board.setShowGrid(False)
#         # 不可编辑
#         self.tbw_Board.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         # 设置点击背景颜色仍为白色
#         self.tbw_Board.setStyleSheet("QTableWidget{selection-background-color:white;}")
#
#         # 清空
#         self.tbw_Board.clear()
#         # 设置行列数
#         self.tbw_Board.setRowCount(self.m + 2)
#         self.tbw_Board.setColumnCount(self.n + 2)
#         # 设置总大小和各个格子大小
#         self.tbw_Board.setFixedSize((self.n + 2) * 50 + 2, (self.m + 2) * 50 + 2)
#         for i in range(self.m + 2):
#             self.tbw_Board.setRowHeight(i, 50)
#         for j in range(self.n + 2):
#             self.tbw_Board.setColumnWidth(j, 50)
#         # icon size
#         self.tbw_Board.setIconSize(QSize(45, 45))
#
#     def GetRowCol(self, pos):
#         """
#         获取鼠标指针对应的行列数
#
#         :param pos: QPoint
#         :return:
#         """
#         tbw_Pos = self.tbw_Board.pos()
#         row = (pos.y() - tbw_Pos.y()) //50
#         col = (pos.x() - tbw_Pos.x()) // 50
#         return row, col
#
#     def IsPosLegal(self, row, col):
#         return 0 <= row < self.m + 2 and 0 <= col < self.n + 2
#
#     def slot_lbl_Img1_Released(self, pos):
#         init_row, init_col = self.GetRowCol(self.lbl_Img1.InitPos)
#         row, col = self.GetRowCol(pos)
#         # pos合法,且对应位置为空
#         if self.IsPosLegal(row, col) and self.InitBoard[row][col] == 0:
#             self.InitBoard[row][col] = self.lbl_Img1.Kind
#             # self.
#             # 如果是来自表格内的转移，原单元格设为0
#             if self.IsPosLegal(init_row, init_col):
#                 self.InitBoard[init_row][init_col] = 0
#         else:
#             self.lbl_Img1.move(self.lbl_Img1.InitPos)
#
#     def slot_lbl_Img2_Released(self, pos):
#         self.lbl_Img2.move(self.lbl_Img2.InitPos)
#         pass
#
#     def slot_pbt_Sure_clicked(self):
#         # TODO: None -> self.InitBoard
#         try:
#             self.BW = BoardWindow(self, self.m, self.n, self.k, self.p, self.ObstacleNum, self.RuleFlag, self.InitBoard)
#             self.BW.show()
#             self.hide()
#         except:
#             self.lbl_Info.setText("Init board is illegal...")
#
#     def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
#         self.Parent.show()
#         self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    self = MainWindow()
    self.show()
    sys.exit(app.exec_())
