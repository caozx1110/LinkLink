# coding=utf-8
"""
@author: Cao Zhanxiang
@project: PyClass
@file: LinkUnit.py
@date: 2021/9/29
@function: the unit of the link game
"""


# the unit of the board
class LinkUnit:
    # BoardRows = 0
    # BoardCols = 0

    def __init__(self, kind: int, row: int, col: int):
        # Kind = 0 mean the Unit has been eliminated
        self.Kind = kind
        self.Row = row
        self.Col = col

    def __eq__(self, other):
        """
        rebuild the "=="

        :param other: the other unit
        :return: whether the two units is equal
        """
        if type(other) == type(self):
            if self.Kind == other.Kind:
                return True
            else:
                return False
        else:
            raise TypeError

    def __ne__(self, other):
        """
        rebuild the "!="

        :param other: the other unit
        :return: whether the two units is not equal
        """
        if type(other) == type(self):
            if self.Kind == other.Kind:
                return False
            else:
                return True
        else:
            raise TypeError

    def __sub__(self, other):
        """
        if the kind of self and other are equal, then eliminate the two units

        :param other: the other unit
        :return: whether the units are eliminated
        """
        if type(other) == type(self):
            if self.Kind == other.Kind:
                self.Kind = 0
                other.Kind = 0
                return True
            else:
                return False
        else:
            raise TypeError

    def __repr__(self):
        """
        rebuild the print content

        :return: the print content
        """
        return str(self.Kind)

    def IsEmpty(self):
        """
        judge if the unit is empty

        :return: IsEmpty
        """
        if self.Kind == 0:
            return True
        else:
            return False

    def ChangeKind(self, kind: int):
        """
        change the kind

        :param kind: the kind to change
        :return: None
        """
        self.Kind = kind

    def Eliminate(self):
        """
        eliminate self

        :return: None
        """
        self.ChangeKind(0)

    def Location(self):
        """
        location in the board

        :return: self.Row, self.Col
        """
        return self.Row, self.Col
