# coding=utf-8
"""
@author: Cao Zhanxiang
@project: 8-Queens.py
@file: LinkGame.py
@date: 2021/10/19
@function: solve the game
"""
from LinkBoard import LinkBoard
import copy
from utils import *


class BoardState:
    # TODO: 当前棋盘状态，父亲节点，累积cost， action（来自之前路径的搜索）
    def __init__(self, board: LinkBoard, parent=None, action=None):
        """

        :param board: 棋盘状态
        :param parent: 父亲节点
        :param action: (units_list, path, cost)
        """
        self.Board = board
        self.Parent = parent
        self.Action = action
        if self.Parent is None:
            self.Cost = 0
        else:
            self.Cost = self.Parent.Cost + self.Action[2]

    def __eq__(self, other):
        return self.Board == other.Board

    def __lt__(self, other):
        return self.Cost + self.Board.RemainMinCost() < other.Cost + other.Board.RemainMinCost()


class LinkGame:

    def __init__(self, m=0, n=0, k=0, p=0, obstacle_num=0, init_board=None):
        self.InitBoard = LinkBoard(m, n, k, p, obstacle_num, init_board)

    def SolveGameWithLimit(self):
        """
        解决初始状态下的问题，基本连连看规则，即限制转弯次数<=2

        :return:
        """

        # TODO: 可以在每一轮消除之后都尝试去消除仅有one-pair的对子
        # TODO: 可以在搜到底之后判断是否为两个仅有一对的形成的交叉死局
        # DFS
        stack = Stack()
        closing_list = []
        # 死局list
        dead_list = []
        stack.push(self.TryEliminateOnePair(self.InitBoard))

        while True:
            # 栈空
            if stack.empty():
                break
            # 取出
            state = stack.pop()
            closing_list.append(state.UnitsBoard)
            # print(state)
            # 如果清空棋盘
            if state.IsEmpty():
                # print(state.Path)
                print("Empty!")
                return state.Path

            # 可能选择
            PEList = self.PossibleEliminates(state)
            if PEList:
                for ul, path, _ in PEList:
                    # 新状态
                    new_state = self.Eliminate(state, unit_list=ul, path=path)
                    if new_state.UnitsBoard not in closing_list:
                        stack.push(new_state)
                    else:
                        pass
                        # print("Repeat")
            else:
                dead_list.append(state)
                print("unsolved, save the unit_list")

        if dead_list:
            # 找到剩余数量最少的一个state
            remain_num_list = [dead_list[i].RemainUnitNum() for i in range(len(dead_list))]
            min_idx = remain_num_list.index(min(remain_num_list))
            print(dead_list[min_idx])
            print(dead_list[min_idx].Path)
            return dead_list[min_idx].Path

    def SolveGameWithoutLimit(self):
        """
        不限制拐弯次数

        :return:
        """
        BQueue = PriorityQueue(BoardState(self.InitBoard))
        closing_set = set()

        while not BQueue.empty():
            state = BQueue.pop()
            # print(state.Cost)
            closing_set.add(state.Board.HashFunc())

            if state.Board.IsEmpty():
                path_list = []
                temp = state
                while temp.Parent is not None:
                    path_list.append(temp.Action)
                    temp = temp.Parent
                path_list.reverse()
                print("Empty!")
                return path_list

            PEList = self.PossibleEliminates(state.Board, rule_flag=1)
            if PEList:
                for ul, path, cost in PEList:
                    new_state = BoardState(self.Eliminate(state.Board, unit_list=ul, path=path, rule_flag=1), parent=state, action=(ul, path, cost))
                    if new_state.Board.HashFunc() not in closing_set:
                        BQueue.push(new_state)
                    else:
                        # print("repeat")
                        pass
            else:
                print("不会出现没有路径的情况")

        print("无解？（怎么可能）")


    def Eliminate(self, state, from_row=0, from_col=0, to_row=0, to_col=0, unit1=None, unit2=None, unit_list=None,
                  path=None, rule_flag=0):
        """
        生成下一个状态用

        :param rule_flag: flag = 0表示基础规则; flag = 1时，表示不限制拐弯次数
        :param state: 当前状态
        :param path: 路径
        :return: 下一个状态
        """
        # 支持多种输入方式
        if unit1 is not None and unit2 is not None:
            from_row, from_col, to_row, to_col = unit1[0], unit1[1], unit2[0], unit2[1]
        # 支持多种输入方式
        if unit_list is not None:
            from_row, from_col, to_row, to_col = unit_list[0][0], unit_list[0][1], unit_list[1][0], unit_list[1][1]

        state_copy = copy.deepcopy(state)

        kind = state_copy.UnitsBoard[from_row][from_col].Kind
        if state_copy.UnitsBoard[from_row][from_col] - state_copy.UnitsBoard[to_row][to_col]:
            # 更新PosOfKind列表
            state_copy.PosOfKinds[kind].remove((from_row, from_col))
            state_copy.PosOfKinds[kind].remove((to_row, to_col))
            # 添加路径, 在Normal规则下使用，不限制拐弯次数时，使用节点的父节点来记录路径
            if rule_flag == 0:
                state_copy.Path.append((unit_list, path))
            return state_copy
        else:
            return None

    def PossibleEliminates(self, state, rule_flag=0):
        """
        获取可能的消除的坐标和路径的列表：[(unit_list, Path)]

        :param state: 当前state
        :param rule_flag: flag = 0表示基础规则; flag = 1时，表示不限制拐弯次数
        :return: 可能消除的对子的列表
        """
        PEList = []
        for i in range(1, len(state.PosOfKinds)):
            for j in range(len(state.PosOfKinds[i]) - 1):
                for k in range(j + 1, len(state.PosOfKinds[i])):
                    # 如果可以消除
                    if rule_flag == 0:
                        Flag, Path, Cost = state.LinkPathNorm(unit1=state.PosOfKinds[i][j],
                                                              unit2=state.PosOfKinds[i][k])
                    else:
                        Flag, Path, Cost = state.LinkPathWithoutLimit(unit1=state.PosOfKinds[i][j],
                                                                      unit2=state.PosOfKinds[i][k])
                    if Flag:
                        PEList.append(([state.PosOfKinds[i][j], state.PosOfKinds[i][k]], Path, Cost))

        return PEList

    def TryEliminateOnePair(self, state: LinkBoard):
        """
        尝试消除现在棋盘上的某一种类中仅有一对的对子

        :return:
        """
        state_copy = copy.deepcopy(state)
        PathList = []
        # IsOK用于消除由于其他one-pair导致的阻挡而导致的one-pair未被消除的情况
        IsOK = True
        while IsOK:
            IsOK = False
            for i in range(len(state_copy.PosOfKinds)):
                if len(state_copy.PosOfKinds[i]) == 2:
                    ul = state_copy.PosOfKinds[i]
                    Flag, Path, _ = state_copy.LinkPathNorm(unit_list=ul)
                    if Flag:
                        # TODO: return Path
                        IsOK = True
                        # Path 添加：(unit_list, unit_list)
                        state_copy = self.Eliminate(state_copy, unit_list=ul, path=Path)

        return state_copy


if __name__ == '__main__':
    # game = LinkGame(4, 5, 7, 6, init_board=[[0, 0, 0, 0, 0, 0, 0],
    #                                            [0, 4, 1, 5, 0, 2, 0],
    #                                            [0, 0, 0, 3, 2, 0, 0],
    #                                            [0, 3, 3, 5, 1, 4, 0],
    #                                            [0, 6, 0, 3, 6, 0, 0],
    #                                            [0, 0, 0, 0, 0, 0, 0]])
    game = LinkGame(5, 5, 10, 10, obstacle_num=4)
    # game = LinkGame()
    print(game.InitBoard)

    print(game.SolveGameWithoutLimit())
