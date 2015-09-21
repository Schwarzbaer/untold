from untold.scripting import eval_script_node

class InvalidExpression(Exception):
    pass

class InvalidOperator(Exception):
    pass

class InvalidArgument(Exception):
    pass

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
    virt_node = eval_script_node(expr_node, state)
    if type(virt_node) in [bool, int, float, str]:
        return virt_node
    elif type(virt_node) == dict:
        try:
            operator = virt_node['op']
            if operator in expr_unary_operators.keys():
                arg = eval_expression(virt_node['arg'])
                return expr_unary_operators[operator](arg, state)
            elif operator in expr_binary_operators.keys():
                argl = eval_expression(virt_node['argl'])
                argr = eval_expression(virt_node['argr'])
                return expr_binary_operators[operator](argl, argr, state)
            else:
                raise InvalidOperator
        except KeyError:
            raise InvalidExpression
    else:
        raise InvalidExpression
