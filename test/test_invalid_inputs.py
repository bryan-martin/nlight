import evaluator
import pytest


def test_lexical_errors():
    with pytest.raises(evaluator.LexicalError):
        answer = evaluator.calc("!1+1")
    with pytest.raises(evaluator.LexicalError):
        answer = evaluator.calc("1+!1")
    with pytest.raises(evaluator.LexicalError):
        answer = evaluator.calc("1+1!")


def test_whitespace():
    assert evaluator.calc(" 1   +   1 ") == 2


def test_syntax_errors():
    with pytest.raises(SyntaxError):
        answer = evaluator.calc("1++1")
    with pytest.raises(SyntaxError):
        answer = evaluator.calc("+1")


def test_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        answer = evaluator.calc("1 / 0")

