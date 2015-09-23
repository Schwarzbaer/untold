from untold.scripting import eval_script_node

class InvalidExpression(Exception):
    def __init__(self, supplementary = "", expr = ""):
        self.supplementary = supplementary
        self.expr = expr
        
    def __str__(self):
        return repr(self.expr)

class InvalidOperator(Exception):
    pass

class InvalidArgument(Exception):
    pass

def is_base_type(val):
    return type(val) in [bool, float, int, str]

# -------------------------------------------------------------------

def expr_const(arg, state):
    return arg

def expr_get(arg, state):
    try:
        return state[arg]
    except KeyError:
        raise InvalidArgument

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
    argl_evald = eval_expression(argl, state)
    if not type(argl_evald) in [int, float]:
        raise InvalidArgument
    argr_evald = eval_expression(argl, state)
    if not type(argr_evald) in [int, float]:
        raise InvalidArgument
    return argl_evald + argr_evald

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
    }

def eval_expression(expr_node, state):
    if is_base_type(expr_node):
        return expr_node
    virt_node = eval_script_node(expr_node, state)
    if type(virt_node) == dict:
        try:
            operator = virt_node['op']
            if operator in expr_unary_operators.keys():
                arg = eval_expression(virt_node['var'], state)
                return expr_unary_operators[operator](arg, state)
            elif operator in expr_binary_operators.keys():
                argl = eval_expression(virt_node['varl'], state)
                argr = eval_expression(virt_node['varr'], state)
                return expr_binary_operators[operator](argl, argr, state)
            else:
                raise InvalidOperator
        except KeyError:
            raise InvalidExpression(expr_node)
    else:
        raise InvalidExpression(expr_node)
