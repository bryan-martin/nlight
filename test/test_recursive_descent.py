import evaluator
from common_input_loader import load_inputs, load_op_inputs
import pytest


test_input, truth_data = load_op_inputs('binary', '+')
@pytest.mark.parametrize("expr_bin_plus,truth_bin_plus", zip(test_input, truth_data))
def test_recursive_descent_binary_plus(expr_bin_plus, truth_bin_plus):
    answer = evaluator.calc(expr_bin_plus, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert answer == truth_bin_plus

test_input, truth_data = load_op_inputs('binary', '-')
@pytest.mark.parametrize("expr_bin_minus,truth_bin_minus", zip(test_input, truth_data))
def test_recursive_descent_binary_minus(expr_bin_minus, truth_bin_minus):
    answer = evaluator.calc(expr_bin_minus, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert answer == truth_bin_minus

test_input, truth_data = load_op_inputs('binary', '*')
@pytest.mark.parametrize("expr_bin_mult,truth_bin_mult", zip(test_input, truth_data))
def test_recursive_descent_binary_mult(expr_bin_mult, truth_bin_mult):
    answer = evaluator.calc(expr_bin_mult, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_bin_mult) < 0.0000001

test_input, truth_data = load_op_inputs('binary', '/')
@pytest.mark.parametrize("expr_bin_div,truth_bin_div", zip(test_input, truth_data))
def test_recursive_descent_binary_div(expr_bin_div, truth_bin_div):
    answer = evaluator.calc(expr_bin_div, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_bin_div) < 0.0000001

test_input, truth_data = load_inputs('binary')
@pytest.mark.parametrize("expr_bin,truth_bin", zip(test_input, truth_data))
def test_recursive_descent_binary_all_ops(expr_bin, truth_bin):
    answer = evaluator.calc(expr_bin, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_bin) < 0.0000001

test_input, truth_data = load_op_inputs('random', '+')
@pytest.mark.parametrize("expr_rand_plus,truth_rand_plus", zip(test_input, truth_data))
def test_recursive_descent_random_plus(expr_rand_plus, truth_rand_plus):
    answer = evaluator.calc(expr_rand_plus, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_rand_plus) < 0.0000001

test_input, truth_data = load_op_inputs('random', '-')
@pytest.mark.parametrize("expr_rand_minus,truth_rand_minus", zip(test_input, truth_data))
def test_recursive_descent_random_minus(expr_rand_minus, truth_rand_minus):
    answer = evaluator.calc(expr_rand_minus, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_rand_minus) < 0.0000001

test_input, truth_data = load_op_inputs('random', '*')
@pytest.mark.parametrize("expr_rand_mult,truth_rand_mult", zip(test_input, truth_data))
def test_recursive_descent_random_mult(expr_rand_mult, truth_rand_mult):
    answer = evaluator.calc(expr_rand_mult, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_rand_mult) < 0.0000001

test_input, truth_data = load_op_inputs('random', '/')
@pytest.mark.parametrize("expr_rand_div,truth_rand_div", zip(test_input, truth_data))
def test_recursive_descent_random_div(expr_rand_div, truth_rand_div):
    answer = evaluator.calc(expr_rand_div, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_rand_div) < 0.0000001

test_input, truth_data = load_inputs('random')
@pytest.mark.parametrize("expr_rand,truth_rand", zip(test_input, truth_data))
def test_recursive_descent_random_all_ops(expr_rand, truth_rand):
    answer = evaluator.calc(expr_rand, evaluator_class=evaluator.RecursiveDescentEvaluator)
    assert abs(answer - truth_rand) < 0.0000001