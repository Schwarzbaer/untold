import random

# Expressions --------------------------------------------------------

class InvalidExpression(Exception):
    def __init__(self, supplementary = "", expr = ""):
        self.supplementary = supplementary
        self.expr = expr
        
    def __str__(self):
        return repr(self.expr)

class InvalidOperator(Exception):
    pass

class InvalidArgument(Exception):
    def __init__(self, arg = ""):
        self.arg = arg
        
    def __str__(self):
        return repr(self.arg)

def is_base_type(val):
    if type(val) in [bool, float, int, str, list]:
        return True
    if val == None:
        return True
    return False

# -------------------------------------------------------------------

def expr_const(arg, state):
    return arg

def expr_get(arg, state):
    return state.get(arg, None)

def expr_get_n(argl, argr, state):
    try:
        l = state[argl]
        if type(l) != list:
            raise InvalidOperator
        else:
            return l[argr]
    except KeyError:
        raise InvalidArgument

def expr_plus(argl, argr, state):
    if not type(argl) in [int, float]:
        raise InvalidArgument
    if not type(argr) in [int, float]:
        raise InvalidArgument
    return argl + argr

def expr_equal(argl, argr, state):
    return argl == argr

def expr_unequal(argl, argr, state):
    return argl != argr

def expr_smaller(argl, argr, state):
    return argl < argr

def expr_smaller_equal(argl, argr, state):
    return argl <= argr

def expr_larger(argl, argr, state):
    return argl > argr

def expr_larger_equal(argl, argr, state):
    return argl >= argr

def expr_or(argl, argr, state):
    return argl or argr

def expr_and(argl, argr, state):
    return argl and argr

def expr_select_m_from_set(argl, argr, state):
    # FIXME: assert type(argl)==int and type(argr)==list
    # assert len(argr) < argl (or easy choice if argl = len
    new_set = set()
    while len(new_set) < argl:
        new_set.add(random.choice(argr))
    return list(new_set)

def expr_in(argl, argr, state):
    # FIXME: asserts
    return argl in argr

def add_to_set(argl, argr, state):
    new_set = set(argr)
    new_set.add(argl)
    return list(new_set)

def remove_from_set(argl, argr, state):
    new_set = set(argr)
    new_set.remove(argl)
    return list(new_set)

expr_unary_operators = {
    'const': expr_const,
    'get': expr_get,
    }

expr_binary_operators = {
    'get-n': expr_get_n,
    '+': expr_plus,
    '==': expr_equal,
    '!=': expr_unequal,
    '<': expr_smaller,
    '<=': expr_smaller_equal,
    '>': expr_larger,
    '>=': expr_larger_equal,
    # Boolean logic
    'or': expr_or,
    'and': expr_and,
    # Set processing
    'select-m-from-set': expr_select_m_from_set,
    'in': expr_in,
    }
