"""
Implement arithmetic generator routines for generating test input
"""
import subprocess
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


def make_test_inputs(ops=["+", "-", "*", "/"]):
    for op in ops:
        make_output_file('binary_{}_test_input.txt'.format(str(ord(op))), generate_binary_expr, 100, ops=[op])
        make_output_file('random_{}_test_input.txt'.format(str(ord(op))), generate_random_expr, 100, ops=[op])
    make_output_file('binary_test_input.txt', generate_binary_expr, 100, ops=ops)
    make_output_file('random_test_input.txt', generate_random_expr, 100, ops=ops)


def make_truth_file(source_file, filename):
    with open(source_file, 'r') as rx_fd:
        with open(filename, 'w') as wx_fd:
            for line in rx_fd:
                proc = subprocess.run('calc "{}"'.format(line.strip()), shell=True, capture_output=True)
                output = proc.stdout.decode('ascii').replace("~", "")
                wx_fd.write(output.strip() + "\n")


def make_truth_data(ops=["+", "-", "*", "/"]):
    for op in ops:
        make_truth_file('binary_{}_test_input.txt'.format(str(ord(op))), 'binary_{}_test_truth.txt'.format(str(ord(op))))
        make_truth_file('random_{}_test_input.txt'.format(str(ord(op))), 'random_{}_test_truth.txt'.format(str(ord(op))))
    make_truth_file('binary_test_input.txt', 'binary_test_truth.txt')
    make_truth_file('random_test_input.txt', 'random_test_truth.txt')
