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
    """
    Operators hierarchy base class
    """

    def __init__(self, token, precedence, pattern):
        """
        Constructor
        :param token: operator token in mathematical expressions, eg '+' for Add
        :param precedence: operator relative precedence
        :param pattern: regex string for token
        """
        self.token = token
        self.precedence = precedence
        self.pattern = pattern

    def __eq__(self, other):
        if other is None:
            return False
        return self.precedence == other.precedence

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if other is None:
            return False
        if other.precedence > self.precedence:
            return True
        return False

    def __le__(self, other):
        if other is None:
            return False
        if other.precedence >= self.precedence:
            return True
        return False

    def __gt__(self, other):
        if other is None:
            return True
        if self.precedence > other.precedence:
            return True
        return False

    def __ge__(self, other):
        if other is None:
            return True
        if self.precedence >= other.precedence:
            return True
        return False

    def eval(self, *args):
        """ Override this in Operator subclasses"""
        raise NotImplementedError()


class Plus(OperatorBase):
    """Addition"""

    def __init__(self):
        super(Plus, self).__init__('+', 1, r'(?P<Plus>\+)')

    def eval(self, *args):
        return args[0] + args[1]


class Minus(OperatorBase):
    """Subtraction"""

    def __init__(self):
        super(Minus, self).__init__('-', 1, r'(?P<Minus>-)')

    def eval(self, *args):
        return args[0] - args[1]


class Multiply(OperatorBase):
    """Multiplication"""

    def __init__(self):
        super(Multiply, self).__init__('*', 2, r'(?P<Multiply>\*)')

    def eval(self, *args):
        return args[0] * args[1]


class Divide(OperatorBase):
    """Division"""

    def __init__(self):
        super(Divide, self).__init__('/', 2, r'(?P<Divide>/)')

    def eval(self, *args):
        return args[0] / args[1]


##################################
###           LEXER            ###
##################################
SUPPORTED_OPERATORS = [Plus(), Minus(), Multiply(), Divide()]
OPERATORS = {op.token: op for op in SUPPORTED_OPERATORS}
SUPPORTED_PATTERNS = [op.pattern for op in SUPPORTED_OPERATORS]
NUM     = r'(?P<Number>\d+)'
OPAREN  = r'(?P<OpenParen>\()'
CPAREN  = r'(?P<CloseParen>\))'
FACTORS = [NUM, OPAREN, CPAREN]
master_pattern = re.compile('|'.join(SUPPORTED_PATTERNS + FACTORS))
Token = collections.namedtuple('Token', ['type', 'value'])

def generate_tokens(pattern, text):
    text = text.replace(' ', '')
    scanner = pattern.scanner(text)
    for m in iter(scanner.match, None):
        token = Token(m.lastgroup, m.group())
        yield token


##################################
###           EVALUATORS       ###
##################################
class MalformedExpressionError(Exception):
    """Exception raised in case of malformed expression"""


class EvaluatorBase(object):
    """
    Base class of evaluator algorithms. Defines common methods of algorithms.
    - _next
    - _consume
    - _error
    - _expect
    - _accept
    - _eval_leaf
    - _eval_node
    """

    def __init__(self, expr):
        """
        :param expr: expression to be evaluated
        """
        assert expr is not None, "Expression to recognize cannot be None, should at least be ''"
        self.tokens = generate_tokens(master_pattern, expr)
        self.current_token = None
        self.next_token = None
        self._consume()

    def _consume(self):
        """
        Consume one token. When next() returns None, _consume is still allowed, but has no effect.
        :return: None
        """
        self.current_token, self.next_token = self.next_token, next(self.tokens, None)

    def _error(self, msg=None):
        """
        Stops the parsing process and reports an error.
        """
        raise MalformedExpressionError(msg)

    def _accept(self, token_type):
        """
        Look ahead and return if type is expected.
        """
        if self.next_token and self.next_token.type == token_type:
            self._consume()
            return True
        else:
            return False

    def _expect(self, token_type):
        """
        Check if _next() is expected. Call _error if not.
        :param token_type: expected token type
        """
        if not self._accept(token_type):
            raise SyntaxError('Expected ' + token_type)

    def _eval_leaf(self, token):
        """
        Convert a "value" token to its numerical value. Call _error() if casting fails
        :param token: stringified value
        :return: int or float depending on the token
        """
        try:
            return int(token.value)
        except ValueError:
            self._error("'%s' cannot be cast to a number" % token.value)

    def _eval_node(self, operator, *args):
        """
        Compute the operation (operator, operands)
        :param operator: operator
        :param args: operands
        :return: result
        """
        return operator.eval(*args)

    def evaluate(self):
        """Override in subclasses"""
        raise NotImplementedError()


class PrecedenceClimbingEvaluator(EvaluatorBase):
    """
    "Precedence climbing" implementation, See article.
    It implements the following grammar parsing:
        E --> Exp(0)
        Exp(p) --> P { B Exp(q) }
        P --> Exp(q) | "(" E ")" | NUM
        B --> "+" | "-" | "*" | "/"
    Article's methods name are kept:
    - Eparser => evaluate
    - Exp => _exp
    - P => _p
    """

    def evaluate(self):
        val = self._exp(0)
        return val

    def _exp(self, precedence):
        t = self._p()
        while self.next_token and OPERATORS[self.next_token.value].precedence >= precedence:
            op = OPERATORS[self.next_token.value]
            self._consume()
            q = op.precedence
            t1 = self._exp(q)
            t = self._eval_node(op, t, t1)
        return t

    def _p(self):
        if self.next_token.type == '(':
            self._consume()
            t = self._exp(0)
            self._expect(')')
            return t
        elif self.next_token and self.next_token.type == "Number":  # must be digits at this point
            t = self._eval_leaf(self.next_token)
            self._consume()
            return t
        else:
            self._error()


class RecursiveDescentEvaluator(EvaluatorBase):
    """
    BNF grammar expr ::= expr + term | expr - term | term
                term ::= term * factor | term / factor | factor
                factor::= (expr) | NUM
    """
    def evaluate(self):
        return self.expr()

    def expr(self):
        '''
        expression ::= term { ( +|-) term } *
        '''

        # it first expect a term according to grammar rule
        expr_value = self.term()

        # then if it's either + or -, we try to consume the right side
        #
        # If it's not + or -, then it is treated as no right side
        while self._accept('Plus') or self._accept('Minus'):
            # get the operation, + or -
            op = self.current_token.type
            right = self.term()
            if op == 'Plus':
                expr_value += right
            elif op == 'Minus':
                expr_value -= right
            else:
                raise SyntaxError('Should not arrive here ' + op)

        return expr_value

    def term(self):
        '''
        term    ::= factor { ('*'|'/') factor } *
        '''

        # it first expect a factor
        term_value = self.factor()

        # then if it's either * or /, we try to consume the right side
        #
        # If it's not + or -, then it is treated as no right side
        while self._accept('Multiply') or self._accept('Divide'):
            op = self.current_token.type

            if op == 'Multiply':
                term_value *= self.factor()
            elif op == 'Divide':
                term_value /= self.factor()
            else:
                raise SyntaxError('Should not arrive here ' + op)

        return term_value

    def factor(self):
        '''
        factor  ::= NUM | (expr)

        '''

        # it can be a number
        if self._accept('Number'):
            return int(self.current_token.value)
        # or (expr)
        elif self._accept('('):
            # we consumed ( in previous _accept
            #
            # then we try to evaluate the expr, and store the value
            expr_value = self.expr()

            # then it should be ), otherwise raise an exception
            self._expect(')')

            # return the previous saved value
            return expr_value
        else:
            raise SyntaxError('Expect NUMBER or LPAREN')



def calc(expr, evaluator_class=PrecedenceClimbingEvaluator):
    """
    exposed method to module routines
    """
    return evaluator_class(expr).evaluate()
