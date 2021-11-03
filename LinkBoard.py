# coding=utf-8
"""
@author: Cao Zhanxiang
@project: PyClass
@file: LinkBoard.py
@date: 2021/9/29
@function: the board
"""
from LinkUnit import LinkUnit
import numpy as np
import random
import copy
import math
from utils import *


class Point:
    """
    用于做棋盘内的搜索
    定义行动的代价
    """
    Goal: tuple

    def __init__(self, coor, parent=None, direct=None):
        # 考虑到不需要节点的kind信息，不使用LinkUnit作为坐标的单元，类型是否相同放在外面判断
        self.Coor = coor
        self.Parent = parent
        self.Direction = direct
        if self.Parent is None:
            self.Cost = 0
        else:
            if self.Parent.Direction is None:
                self.Cost = 0
            elif self.Direction == self.Parent.Direction:
                self.Cost = self.Parent.Cost
            else:
                self.Cost = self.Parent.Cost + 1

    def __eq__(self, other):
        return self.Coor == other.Coor and self.Direction == other.Direction

    def __lt__(self, other):
        return self.Cost + (not(self.Coor[0] == self.Goal[0] or self.Coor[1] == self.Goal[1])) < \
               other.Cost + (not(other.Coor[0] == other.Goal[0] or other.Coor[1] == other.Goal[1]))


class LinkBoard:
    DirDic = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1),
              (-1, 0): 'U', (1, 0): 'D', (0, -1): 'L', (0, 1): 'R'}

    def __init__(self, m=0, n=0, k=0, p=0, obstacle_num=0, init_board=None):
        self.Rows = m + 2
        self.Cols = n + 2
        self.k = k
        self.p = p
        # 由上一个棋盘状态转换到这一个棋盘状态的Path
        # 元素格式：(unit_path, unit_path)
        self.Path = []
        self.UnitsBoard = []
        # the pos of every kind
        self.PosOfKinds = [[] for i in range(p + 1)]

        if init_board is None:
            self.GenerateRandomBoard(m, n, k, p, obstacle_num)
        else:
            # TODO: 手动生成的棋盘
            self.UnitsBoard = [[LinkUnit(init_board[i][j], i, j)
                                for j in range(len(init_board[0]))]
                               for i in range(len(init_board))]

        self.GetPosOfKinds()
        # self.UnitsBoard = np.array(units_list)

        # supplement the board with a round of empty units
        # LinkUnit.BoardRows = m + 2
        # LinkUnit.BoardCols = n + 2

        self.Score = 0

    def __eq__(self, other):
        return self.UnitsBoard == other.UnitsBoard

    def __repr__(self):
        return "[\n" + "\n".join(["[" + ",\t".join(
            [str(self.UnitsBoard[i][j]) for j in range(len(self.UnitsBoard[i]))]) + "]"
                                  for i in range(len(self.UnitsBoard))]) + "\n]" + "\n"

    def IsEmpty(self):
        """
        判断是否为空
        
        :return: bool
        """
        for i in range(1, len(self.PosOfKinds)):
            if self.PosOfKinds[i]:
                return False
        return True

    def RemainUnitNum(self):
        """
        计算剩余unit的个数

        :return: 个数
        """
        num = 0
        for i in range(1, len(self.PosOfKinds)):
            num += len(self.PosOfKinds[i])
        return num // 2

    def RemainMinCost(self):
        """
        启发函数，看当前状态最少需要多少cost，若不在同行或同列，则cost至少为1
        :return: h(n)
        """
        MinCost = 0
        for i in range(1, len(self.PosOfKinds)):
            temp = len(self.PosOfKinds[i])
            for j in range(len(self.PosOfKinds[i]) - 1):
                for k in range(j + 1, len(self.PosOfKinds[i])):
                    if self.PosOfKinds[i][j][0] == self.PosOfKinds[i][k][0] or \
                            self.PosOfKinds[i][j][1] == self.PosOfKinds[i][k][1]:
                        temp -= 2
            MinCost += max(temp, 0)
        return MinCost // 2

    def GenerateRandomBoard(self, m, n, k, p, obstacle_num=0):
        """
        在一个m*n的棋盘中，散落着2k个图案（2k ≤ m*n），这些图案共有p类

        :param obstacle_num: 障碍物数量
        :param m: the board rows
        :param n: the board cols
        :param k: 2k units
        :param p: the units' kinds
        :return: None
        """
        if obstacle_num + 2 * k > m * n or p > k:
            print("Error in m, n, k, p, ObstacleNum")
            raise ValueError

        # init the board with the empty units, the periphery of the board are a round of empty units
        self.UnitsBoard = np.array([[LinkUnit(0, j, i) for i in range(n + 2)] for j in range(m + 2)])
        # lu is 0 dim ndarray, then the element idx is (), the element is lu[()]
        # self.UnitsBoard[1: -1, 1: -1] are without the round of the board
        # [lu[()] for lu in np.nditer(self.UnitsBoard[1: -1, 1: -1], op_flags=['readwrite'], flags=['refs_ok']) if lu[()
        # ].IsEmpty()]
        for i in range(1, k + 1):
            if i <= p:
                random.choice([lu[()] for lu in
                               np.nditer(self.UnitsBoard[1: -1, 1: -1], op_flags=['readwrite'], flags=['refs_ok']) if
                               lu[()].IsEmpty()]).ChangeKind(i)
                random.choice([lu[()] for lu in
                               np.nditer(self.UnitsBoard[1: -1, 1: -1], op_flags=['readwrite'], flags=['refs_ok']) if
                               lu[()].IsEmpty()]).ChangeKind(i)
            else:
                temp_kind = random.randint(1, p)
                random.choice([lu[()] for lu in
                               np.nditer(self.UnitsBoard[1: -1, 1: -1], op_flags=['readwrite'], flags=['refs_ok']) if
                               lu[()].IsEmpty()]).ChangeKind(temp_kind)
                random.choice([lu[()] for lu in
                               np.nditer(self.UnitsBoard[1: -1, 1: -1], op_flags=['readwrite'], flags=['refs_ok']) if
                               lu[()].IsEmpty()]).ChangeKind(temp_kind)

        for i in range(obstacle_num):
            random.choice(
                [lu[()] for lu in np.nditer(self.UnitsBoard[1: -1, 1: -1], op_flags=['readwrite'], flags=['refs_ok']) if
                 lu[()].IsEmpty()]).ChangeKind(-1)

        self.UnitsBoard = self.UnitsBoard.tolist()

    def GetPosOfKinds(self):
        """
        according to the board, get the pos of every kind, the dim 2 array, the row show the kind

        e.g.: kind 0 [[(1, 2), (2, 3)]
             kind 1 [(2, 1), (3, 4)]]

        :return: None
        """
        for i in range(self.Rows):
            for j in range(self.Cols):
                kind = self.UnitsBoard[i][j].Kind
                if kind >= 0:
                    self.PosOfKinds[kind].append((i, j))

    # TODO: 修改
    def Neighbors(self, coor):
        """
        get the neighbor of the unit

        :param coor:
        :return: the list of the (coor_x, coor_y, direction)
        """
        return [(coor[0] + i, coor[1] + j, self.DirDic[(i, j)]) for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                if 0 <= coor[0] + i < self.Rows and 0 <= coor[1] + j < self.Cols]

    def LinkTurn0(self, from_row=0, from_col=0, to_row=0, to_col=0):
        """
        判断转向0次的路径是否为空，即直接连接

        Note： 判断前需要判断两者kind是否相同，且kind应该要大于0

        :param from_col: 第一个unit
        :param from_row: 第一个unit
        :param to_col: 第二个unit
        :param to_row: 第二个unit
        :return: 返回是否能消除以及消除的路径，路径形式：[(方向: str <'U', 'D', 'L', 'R'>, 步长=0), ...]
        """
        if (from_row, from_col) == (to_row, to_col):
            return False, None
        # 纵向可能消除
        if from_row == to_row:
            Flag = True
            for c in range(min(from_col, to_col) + 1, max(from_col, to_col)):
                if not self.UnitsBoard[from_row][c].IsEmpty():
                    Flag = False
            # 纵向能够消除
            if Flag:
                return True, ['R' if to_col > from_col else 'L'] * abs(to_col - from_col)
        # 横向可能消除
        elif from_col == to_col:
            Flag = True
            for r in range(min(from_row, to_row) + 1, max(from_row, to_row)):
                if not self.UnitsBoard[r][from_col].IsEmpty():
                    Flag = False
            # 横向能够消除
            if Flag:
                return True, ['D' if to_row > from_row else 'U'] * abs(to_row - from_row)

        return False, None

    def LinkTurn1(self, from_row=0, from_col=0, to_row=0, to_col=0):
        """
        判断转向1次路径，是否能走通

        Note： 判断前需要判断两者kind是否相同，且kind应该要大于0

        :param from_col: 第一个unit
        :param from_row: 第一个unit
        :param to_col: 第二个unit
        :param to_row: 第二个unit
        :return: 返回是否能消除以及消除的路径，路径形式：[(方向: str <'U', 'D', 'L', 'R'>, 步长=0), ...]
        """
        if from_row == to_row or from_col == to_col:
            return False, None

        # 转折点为空
        if self.UnitsBoard[from_row][to_col].IsEmpty():
            # 不转弯两段是否能走通
            Flag1, Path1 = self.LinkTurn0(from_row, from_col, from_row, to_col)
            Flag2, Path2 = self.LinkTurn0(from_row, to_col, to_row, to_col)
            if Flag1 and Flag2:
                if Path1[-1][0] != Path2[0][0]:
                    return True, Path1 + Path2

        # 转折点为空
        if self.UnitsBoard[to_row][from_col].IsEmpty():
            # 不转弯两段是否能走通
            Flag1, Path1 = self.LinkTurn0(from_row, from_col, to_row, from_col)
            Flag2, Path2 = self.LinkTurn0(to_row, from_col, to_row, to_col)
            if Flag1 and Flag2:
                if Path1[-1][0] != Path2[0][0]:
                    return True, Path1 + Path2

        return False, None

    def LinkTurn2(self, from_row=0, from_col=0, to_row=0, to_col=0):
        """
        判断转向2次路径，是否能走通

        Note： 判断前需要判断两者kind是否相同，且kind应该要大于0

        :param from_col: 第一个unit
        :param from_row: 第一个unit
        :param to_col: 第二个unit
        :param to_row: 第二个unit
        :return: 返回是否能消除以及消除的路径，路径形式：[(方向: str <'U', 'D', 'L', 'R'>, 步长=0), ...]
        """
        if (from_row, from_col) == (to_row, to_col):
            return False, None

        # 在两点形成的井字网格上
        for i, j in [(from_row, c) for c in range(self.Cols)] + [(r, from_col) for r in range(self.Rows)] + \
                    [(to_row, c) for c in range(self.Cols)] + [(r, to_col) for r in range(self.Rows)]:
            # 如果转折点为空
            if self.UnitsBoard[i][j].IsEmpty():
                # 一边能转0次通，一边能转1次通
                Flag1, Path1 = self.LinkTurn0(from_row, from_col, i, j)
                Flag2, Path2 = self.LinkTurn1(i, j, to_row, to_col)
                if Flag1 and Flag2:
                    if Path1[-1][0] != Path2[0][0]:
                        return True, Path1 + Path2

                Flag1, Path1 = self.LinkTurn1(from_row, from_col, i, j)
                Flag2, Path2 = self.LinkTurn0(i, j, to_row, to_col)
                if Flag1 and Flag2:
                    if Path1[-1][0] != Path2[0][0]:
                        return True, Path1 + Path2

        return False, None

    def LinkPathNorm(self, from_row=0, from_col=0, to_row=0, to_col=0, unit1=None, unit2=None, unit_list=None):
        # 支持多种输入方式
        if unit1 is not None and unit2 is not None:
            from_row, from_col, to_row, to_col = unit1[0], unit1[1], unit2[0], unit2[1]
        # 支持多种输入方式
        if unit_list is not None:
            from_row, from_col, to_row, to_col = unit_list[0][0], unit_list[0][1], unit_list[1][0], unit_list[1][1]

        # Kind不同，无法连接
        if self.UnitsBoard[from_row][from_col] != self.UnitsBoard[to_row][to_col]:
            return False, None, None
        # 拐0次
        Flag, Path = self.LinkTurn0(from_row, from_col, to_row, to_col)
        if Flag:
            return Flag, Path, 0
        else:
            # 拐1次
            Flag, Path = self.LinkTurn1(from_row, from_col, to_row, to_col)
            if Flag:
                return Flag, Path, 1
            else:
                # 拐2次
                Flag, Path = self.LinkTurn2(from_row, from_col, to_row, to_col)
                if Flag:
                    return Flag, Path, 2
                else:
                    return False, None, None

    def LinkPathWithoutLimit(self, from_row=0, from_col=0, to_row=0, to_col=0, unit1=None, unit2=None, unit_list=None):
        # 支持多种输入方式
        if unit1 is not None and unit2 is not None:
            from_row, from_col, to_row, to_col = unit1[0], unit1[1], unit2[0], unit2[1]
        # 支持多种输入方式
        if unit_list is not None:
            from_row, from_col, to_row, to_col = unit_list[0][0], unit_list[0][1], unit_list[1][0], unit_list[1][1]

        # 尝试转折0， 1， 2次
        Flag, Path, Cost = self.LinkPathNorm(from_row, from_col, to_row, to_col)
        if Flag:
            return Flag, Path, Cost
        else:
            # 开节点表
            Point.Goal = (to_row, to_col)
            PQueue = PriorityQueue(Point((from_row, from_col)))
            # 闭节点表
            closing_list = []
            # 循环
            while not PQueue.empty():
                # 取出点
                point = PQueue.pop()
                closing_list.append(point)
                # 判断是否为目标点
                if point.Coor == (to_row, to_col):
                    # 是的话返回path
                    path = []
                    temp = point
                    while temp.Parent is not None:
                        path.append(temp.Direction)
                        temp = temp.Parent
                    path.reverse()
                    return True, path, point.Cost

                # 周围的点
                neighbors = self.Neighbors(point.Coor)
                for i, j, dire in neighbors:
                    if self.UnitsBoard[i][j].IsEmpty() or (i, j) == (to_row, to_col):
                        # 新的节点
                        new_point = Point((i, j), point, dire)
                        if new_point not in closing_list:
                            PQueue.push(new_point)
                        else:
                            pass
        return False, None, None

    def HashFunc(self):
        # 考虑到障碍物和空白，+1 +1
        p = self.p + 2
        Hash = 0
        for i in range(1, self.Rows - 1):
            for j in range(1, self.Cols - 1):
                Hash += self.UnitsBoard[i][j].Kind * (p ** ((i - 1) * (self.Cols - 2) + (j - 1)))
        return Hash


if __name__ == '__main__':
    Board = LinkBoard(4, 5, 7, 6, init_board=[[0, 0, 0, 0, 0, 0, 0],
                                              [0, 4, 1, 5, 0, 2, 0],
                                              [0, 0, 0, 3, 2, 0, 0],
                                              [0, 3, 3, 5, 1, 4, 0],
                                              [0, 6, 0, 3, 6, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0]])
    print(Board.LinkPathNorm(unit_list=[(1, 1), (1, 4)]))
    # Board = LinkBoard()
    print(Board)
    print(Board.LinkPathWithoutLimit(2, 3, 3, 5))

