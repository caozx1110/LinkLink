# coding=utf-8
"""
@author: Cao Zhanxiang
@project: 8-Queens.py
@file: MainProgress.py
@date: 2021/10/22
@function: 业务流程类
"""
from LinkBoard import LinkBoard
from LinkGame import LinkGame
from PyQt5.QtCore import QThread, pyqtSignal

# 求解问题的线程
class SolveThread(QThread):
    Solved = pyqtSignal(list)
    Path = []

    def __init__(self, game, rule_flag=0):
        super(SolveThread, self).__init__()
        self.Game = game
        self.RuleFlag = rule_flag

    def run(self) -> None:
        if self.RuleFlag == 0:
            self.Path = self.Game.SolveGameWithLimit()
            self.Solved.emit(self.Path)
        elif self.RuleFlag == 1:
            self.Path = self.Game.SolveGameWithoutLimit()
            self.Solved.emit(self.Path)

# main progress
class MainProgress:
    def __init__(self):
        self.Game = LinkGame()
        self.SThread = SolveThread(self.Game)

    def FormBoard(self, m, n, k, p, obstacle_num=0, init_board=None):
        """
        生成棋盘

        :param init_board:
        :param obstacle_num:
        :param m:
        :param n:
        :param k:
        :param p:
        :return:
        """
        self.Game = LinkGame(m, n, k, p, obstacle_num=obstacle_num, init_board=init_board)

    def SolveGame(self, rule_flag=0):
        """
        求解问题，开启solve thread

        :return:
        """
        self.SThread = SolveThread(self.Game, rule_flag)
        self.SThread.start()


