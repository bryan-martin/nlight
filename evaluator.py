"""
Implement base objects for parsing arithmetic expressions
    - Operators (symbol, precedence, associativity?)
    - Tokenizer (regex?, generator?)
    - Evaluator(token_string):
        return calculation

From reading it appears that implementing various grammars can be accomplished by building up
machinery that operates on the current token while looking ahead at the next token.
The base class should contain tokenstr->current, tokenstr->next, a method to move along the tokens,
and a method to check the type of the next token
"""
import re
import collections


##################################
###           OPERATORS        ###
##################################
class OperatorBase(object):
    def __init__(self, symbol, regex):
        self.symbol = symbol
        self.regex = regex

    def perform(self, *args):
        raise NotImplementedError


class Plus(OperatorBase):
    def perform(self, *args):
        return args[0] + args[1]


class Minus(OperatorBase):
    def perform(self, *args):
        return args[0] - args[1]


class Multiply(OperatorBase):
    def perform(self, *args):
        return args[0] * args[1]


class Divide(OperatorBase):
    def perform(self, *args):
        return args[0] / args[1]


PRECEDENCE = {
    1: {"Plus": Plus("+", r"(?P<Plus>\+)"), "Minus": Minus("-", r"(?P<Minus>-)"),},
    2: {
        "Multiply": Multiply("*", r"(?P<Multiply>\*)"),
        "Divide": Divide("/", r"(?P<Divide>/)"),
    },
}
OPERATOR_REGEX = [
    op.regex for precedence in PRECEDENCE.values() for op in precedence.values()
]

Number = r"(?P<Number>\d+)"
Lparen = r"(?P<Lparen>\()"
Rparen = r"(?P<Rparen>\))"
FACTORS = [Number, Lparen, Rparen]
master_pattern = re.compile("|".join(OPERATOR_REGEX + FACTORS))


##################################
###           LEXER            ###
##################################
Token = collections.namedtuple("Token", ["type", "value"])


def generate_tokens(pattern, text):
    text = text.replace(" ", "")
    scanner = pattern.scanner(text)
    for m in iter(scanner.match, None):
        token = Token(m.lastgroup, m.group())
        yield token


##################################
###           EVALUATORS       ###
##################################
class EvaluatorBase(object):
    """
    Base class for implementing different grammar parsers
    """
    def __init__(self, text):
        self.tokens = generate_tokens(master_pattern, text)
        self.current_token = None
        self.next_token = None
        self._advance()

    def evaluate(self):
        """call top level non-terminal"""
        return self.expr()

    def _advance(self):
        self.current_token, self.next_token = self.next_token, next(self.tokens, None)

    def _accept(self, token_type):
        """method to test and accept look ahead token."""
        if self.next_token and self.next_token.type == token_type:
            self._advance()
            return True
        else:
            return False

    def _expect(self, token_type):
        """method to exactly match and discard the next token on the input."""
        if not self._accept(token_type):
            raise SyntaxError("Expected " + token_type)

    def expr(self):
        raise NotImplementedError


class RecursiveDescentEvaluator(EvaluatorBase):
    """
    Implementation of a recursive descent parser.

    Each method implements a single grammar rule.
    It walks from left to right over grammar rule.
    It will either consume the rule a generate a syntax error

        BNF grammar expr ::= expr + term | expr - term | term
                    term ::= term * factor | term / factor | factor
                    factor::= (expr) | NUM
    """
    def expr(self):
        """
        expr ::= expr + term | expr - term | term
        """
        expr_value = self.term()
        while any([self._accept(operator) for operator in PRECEDENCE[1]]):
            op = PRECEDENCE[1][self.current_token.type]
            right = self.term()
            expr_value = op.perform(expr_value, right)
        return expr_value

    def term(self):
        """
        term ::= term * factor | term / factor | factor
        """
        term_value = self.factor()
        while any([self._accept(operator) for operator in PRECEDENCE[2]]):
            op = PRECEDENCE[2][self.current_token.type]
            term_value = op.perform(term_value, self.factor())
        return term_value

    def factor(self):
        """
        factor::= (expr) | NUM
        """
        if self._accept("Number"):
            return int(self.current_token.value)
        elif self._accept("Lparen"):
            expr_value = self.expr()
            self._expect("Rparen")
            return expr_value
        else:
            raise SyntaxError("Expect Number or Lparen but got {}".format(self.current_token.value))


def calc(expr, evaluator_class=RecursiveDescentEvaluator):
    """
    exposed method to module routines
    """
    e = evaluator_class(expr)
    return e.evaluate()
