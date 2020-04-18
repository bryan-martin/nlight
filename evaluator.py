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
    Use the ._accept() method to test and accept look ahead token.
    Use the ._expect() method to exactly match and discard the next token on the input.
        or raise a SyntaxError if it doesn't match
    """

    def __init__(self, text):
        self.tokens = generate_tokens(master_pattern, text)
        self.current_token = None
        self.next_token = None
        self._advance()

    def evaluate(self):
        # expr is the top level grammar. So we invoke that first.
        # it will invoke other function to consume tokens according to grammar rule.
        return self.expr()

    def _advance(self):
        self.current_token, self.next_token = self.next_token, next(self.tokens, None)

    def _accept(self, token_type):
        # if there is next token and token type matches
        if self.next_token and self.next_token.type == token_type:
            self._advance()
            return True
        else:
            return False

    def _expect(self, token_type):
        if not self._accept(token_type):
            raise SyntaxError("Expected " + token_type)


class RecursiveDescentEvaluator(EvaluatorBase):
    """
    Implementation of a recursive descent parser.

    Each method implement a single grammar rule.
    It walks from left to right over grammar rule.
    It either consume the rule a generate a syntax error
    """

    def __init__(self, text):
        self.tokens = generate_tokens(master_pattern, text)
        self.current_token = None
        self.next_token = None
        self._advance()

    def evaluate(self):
        # expr is the top level grammar. So we invoke that first.
        # it will invoke other function to consume tokens according to grammar rule.
        return self.expr()

    def _advance(self):
        self.current_token, self.next_token = self.next_token, next(self.tokens, None)

    def _accept(self, token_type):
        # if there is next token and token type matches
        if self.next_token and self.next_token.type == token_type:
            self._advance()
            return True
        else:
            return False

    def _expect(self, token_type):
        if not self._accept(token_type):
            raise SyntaxError("Expected " + token_type)

    def expr(self):
        """
        expression ::= term { ( +|-) term } *
        """

        # it first expect a term according to grammar rule
        expr_value = self.term()

        # then if it's either + or -, we try to consume the right side
        #
        # If it's not + or -, then it is treated as no right side
        while any([self._accept(operator) for operator in PRECEDENCE[1]]):
            # get the operation, + or -
            op = PRECEDENCE[1][self.current_token.type]
            right = self.term()
            expr_value = op.perform(expr_value, right)
        return expr_value

    def term(self):
        """
        term    ::= factor { ('*'|'/') factor } *
        """

        # it first expect a factor
        term_value = self.factor()

        # then if it's either * or /, we try to consume the right side
        #
        # If it's not + or -, then it is treated as no right side
        while any([self._accept(operator) for operator in PRECEDENCE[2]]):
            op = PRECEDENCE[2][self.current_token.type]
            term_value = op.perform(term_value, self.factor())
        return term_value

    def factor(self):
        """
        factor  ::= NUM | (expr)

        """

        # it can be a number
        if self._accept("Number"):
            return int(self.current_token.value)
        # or (expr)
        elif self._accept("Lparen"):
            # we consumed ( in previous _accept
            #
            # then we try to evaluate the expr, and store the value
            expr_value = self.expr()

            # then it should be ), otherwise raise an exception
            self._expect("Rparen")

            # return the previous saved value
            return expr_value
        else:
            raise SyntaxError("Expect NUMBER or LPAREN")


def calc(expr, evaluator_class=RecursiveDescentEvaluator):
    """
    exposed method to module routines
    """
    e = evaluator_class(expr)
    return e.evaluate()
