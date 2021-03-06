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
import argparse

##################################
###           OPERATORS        ###
##################################
class OperatorBase(object):
    """
    This base class allows for registering the char associated with the operator or the "symbol"
    as well as the regex string to match it. Overwrite perform() to implement the operator execution
    How to implement:
        op.perform() is going to be called by evaluator methods. To implement perform correctly,
        associativity of the operator needs to be understood. "+" and "*" are associative. This means
        a*b*c == (a*b)*c == a*(b*c), left, right, either is correct. This is the property of associativity.
        "-" and "/" on the other hand are inherently left-associative. These operators are non-associative and
        enjoy only notional associativity. Therefore a-b-c == (a-b)-c != a-(b-c).
        The op.perform() method is called with a left and a right positional arguement. If operator is
        left, associative, these must be "switched". See implementation of Minus and Divide
    """
    def __init__(self, symbol, regex):
        self.symbol = symbol
        self.regex = regex

    def perform(self, *args):
        raise NotImplementedError


class Plus(OperatorBase):
    def perform(self, *args):
        """called as Plus.perform(left, right)"""
        return args[0] + args[1]


class Minus(OperatorBase):
    def perform(self, *args):
        """inherently left-associative. Therefore (right - left) is correct"""
        return args[1] - args[0]


class Multiply(OperatorBase):
    def perform(self, *args):
        """called as Multiply.perform(left, right)"""
        return args[0] * args[1]


class Divide(OperatorBase):
    """inherently left-associative. Therefore (right / left) is correct"""
    def perform(self, *args):
        return args[1] / args[0]


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

Number = r"(?P<Number>\d+(\.\d*)?)"
Lparen = r"(?P<Lparen>\()"
Rparen = r"(?P<Rparen>\))"
MISMATCH = r"(?P<Mismatch>.)"
FACTORS = [Number, Lparen, Rparen]
master_pattern = re.compile("|".join(OPERATOR_REGEX + FACTORS + [MISMATCH]))


##################################
###           LEXER            ###
##################################
class LexicalError(Exception):
    """custom error handling for lexer errors"""


Token = collections.namedtuple("Token", ["type", "value"])


def generate_tokens(pattern, text):
    text = text.replace(" ", "")
    for match_obj in master_pattern.finditer(text):
        token_type = match_obj.lastgroup
        value = match_obj.group()
        if token_type == "Number":
            value = float(value) if '.' in value else int(value)
        elif token_type == "Mismatch":
            raise LexicalError("{} is not a valid symbol".format(value))
        token = Token(token_type, value)
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
        """
        Increment the current and next token pointers
        """
        self.current_token, self.next_token = self.next_token, next(self.tokens, None)

    def _accept(self, token_type):
        """
        If the next token is of token_type, advance or 'consume' the token
        Returns (bool): Indication of match True or False
        """
        if self.next_token and self.next_token.type == token_type:
            self._advance()
            return True
        else:
            return False

    def _expect(self, token_type):
        """
        Used to enforce the grammar. If the next token does not match a type the expression is invalid.
        method to exactly match and discard the next token on the input.
        """
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

        BNF grammar expr ::= term | term + expr | term - expr
                    term ::= factor | factor * term | factor / term
                    factor::= NUM | (expr)
    """
    def expr(self):
        """
        BNF grammar expr ::= term | {term + expr | term - expr}
        This deals with the lowest precedence operators "+" and "-"
        """
        expr_value = self.term()  # expr ::= term
        # This while loop implements {term op expr} so if the next token in any operator of lowest precedence we do the following:
        # 1)get the op
        # 2)get the left hand operand or the term
        # 3)accumulate the expr value with the result of op(left, right)
        # This is equivalent to expr ::= {term + expr | term - expr}
        while any([self._accept(operator) for operator in PRECEDENCE[1]]):
            op = PRECEDENCE[1][self.current_token.type]
            left = self.term()
            expr_value = op.perform(left, expr_value)
        return expr_value

    def term(self):
        """
        term ::= factor | {factor * term | factor / term}
        This deals with the next lowest precedence operators "*" and "/"
        """
        term_value = self.factor()  # term :== factor
        # This while loop implements {factor op expr} so if the next token in any operator of second lowest precedence we do the following:
        # 1)get the op
        # 2)get the left hand operand or the factor
        # 3)accumulate the expr value with the result of op(left, right)
        # This is equivalent to expr ::= {term + expr | term - expr}
        while any([self._accept(operator) for operator in PRECEDENCE[2]]):
            op = PRECEDENCE[2][self.current_token.type]
            left = self.factor()
            term_value = op.perform(left, term_value)
        return term_value

    def factor(self):
        """
        factor::= NUM | (expr)
        This deals with the non-terminal chars "NUM", "(", and ")".
        Also terminate recursion or SyntaxError here.
        """
        if self._accept("Number"):
            return float(self.current_token.value)  # factor ::= NUM
        # This statement is breaking down factor ::= "(" expr ")"
        elif self._accept("Lparen"):
            expr_value = self.expr()   # This terminates the recursion
            self._expect("Rparen")
            return expr_value
        else:
            if self.current_token:
                raise SyntaxError("Expect Number or Lparen but got {}".format(self.current_token.value))
            elif self.next_token:  # required if the very first token in syntactically incorrect.
                raise SyntaxError("Expect Number or Lparen but got {}".format(self.next_token.value))


def calc(expr, evaluator_class=RecursiveDescentEvaluator):
    """
    exposed method to module routines
    """
    e = evaluator_class(expr)
    return e.evaluate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A simple calculator for mathematical expressions. Supports operators +-/*")
    parser.add_argument('expression', nargs='+', help="Expression to evaluate")
    expression = ''.join(parser.parse_args().expression)
    res = calc(expression)
    print(res)
