"""
Implement arithmetic generator routines for generating test input
"""
from random import random, randint, choice


class Number(object):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return str(self.num)


class BinaryExpression(object):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return str(self.left) + " " + self.op + " "  + str(self.right)


class ParenthesizedExpression(object):
    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return "(" + str(self.exp) + ")"


def generate_binary_expr(prob=1, ops=["+", "-", "*", "/"]):
    p = random()
    if p > prob:
        return Number(randint(1, 24))
    left = generate_binary_expr(prob / 1.2, ops=ops)
    right = generate_binary_expr(prob / 1.2, ops=ops)
    op = choice(ops)
    return BinaryExpression(left, op, right)


def generate_random_expr(prob=1, ops=["+", "-", "*", "/"]):
    p = random()
    if p > prob:
        return Number(randint(1, 100))
    elif randint(0, 1) == 0:
        return ParenthesizedExpression(generate_random_expr(prob / 1.2))
    else:
        left = generate_random_expr(prob / 1.2, ops=ops)
        op = choice(ops)
        right = generate_random_expr(prob / 1.2, ops=ops)
        return BinaryExpression(left, op, right)

def make_output_file(filename, expr, length, ops=["+", "-", "*", "/"]):
    with open(filename, 'w') as fd:
        for _ in range(length):
            fd.write(str(expr(ops=ops)) + '\n')
