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
                #print(virt_node['varl'], virt_node['varr'])
                argl = eval_expression(virt_node['varl'], state)
                argr = eval_expression(virt_node['varr'], state)
                res = expr_binary_operators[operator](argl, argr, state)
                return res
            else:
                raise InvalidOperator
        except KeyError:
            raise InvalidExpression(expr_node)
    else:
        raise InvalidExpression(expr_node)

# Scripting elements -------------------------------------------------

# Common features of list-bearing keywords, specifically:
# IF

def eval_list_node(node_list, state):
    virt_list = []
    idx = -1
    for list_node in node_list:
        idx += 1
        virt_node = list_node.copy()
        virt_node.update({'_idx': idx})
        if 'if' in virt_node.keys():
            cond_node = virt_node['if']
            if eval_expression(cond_node, state):
                virt_list.append(virt_node)
            else:
                pass
        else:
            # No 'if' keyword encountered
            virt_list.append(virt_node)
    return virt_list

# CASE structure
# {case: [{cond: True, foo: 1}],
#  bar: 1}
# returns
# {foo: 1, bar: 1}
# Returns the first foo-containing node for which cond is true

class CaseWithoutActiveCond(Exception):
    pass

def eval_case_node(case_node, state):
    options = eval_list_node(case_node['case'], state)
    for leaf in options:
        condition = leaf['cond']
        if eval_expression(condition, state):
            virt_node = case_node.copy()
            del virt_node['case']
            virt_node.update(leaf)
            return virt_node
    raise CaseWithoutActiveCond

# CHOICE
# {choice: [{weight: 1},
#           {weight: 1}]}

class UnknownWeightType(Exception):
    pass

def eval_weight(weight_node, state):
    if type(weight_node) == int:
        return float(weight_node)
    elif type(weight_node) == float:
        return weight_node
    else:
        raise UnknownWeightType

def eval_choice_node(choice_node, state):
    options = eval_list_node(choice_node['choice'], state)
    weights = [eval_weight(leaf.get('weight', 1.0), state)
               for leaf in options]
    total_weights = sum(weights)
    c = random.random()
    idx = 0
    w_sum = weights[0] / total_weights
    # FIXME: This should never run beyond the list elements, but maybe I should try/except it anyway?
    while w_sum < c:
        idx += 1
        w_sum += weights[idx] / total_weights
    virt_node = choice_node.copy()
    del virt_node['choice']
    virt_node.update(choice_node['choice'][idx])
    # pprint(virt_node)
    return virt_node

# CHOICE-F
# {choice-f: {storage: foobarbaz,
#             choices: [{weight: 1},
#                       {weight: 1}]}

def eval_choice_f_node(choice_f_node, state):
    storage = choice_f_node['choice-f']['storage']
    if state.get(storage, None) != None:
        choice_idx = state.get(storage)
        virt_node = choice_f_node.copy()
        del virt_node['choice-f']
        virt_node.update(choice_f_node['choice-f']['choices'][choice_idx].copy())
        return virt_node
    else:
        options = eval_list_node(choice_f_node['choice-f']['choices'], state)
        weights = [eval_weight(leaf.get('weight', 1.0), state)
                   for leaf in options]
        total_weights = sum(weights)
        c = random.random()
        idx = 0
        w_sum = weights[0] / total_weights
        # FIXME: This should never run beyond the list elements, but maybe I should try/except it anyway?
        while w_sum < c:
            idx += 1
            w_sum += weights[idx] / total_weights
        virt_node = choice_f_node.copy()
        #print(virt_node)
        del virt_node['choice-f']
        virt_node.update(options[idx])
        state[storage] = virt_node['_idx']
        # pprint(virt_node)
        return virt_node

# Managerial

script_funcs = {
    'case': eval_case_node,
    'choice': eval_choice_node,
    'choice-f': eval_choice_f_node,
}

func_tags = set(script_funcs.keys())

def node_has_script_elements(node):
    return any([script_tag in node for script_tag in script_funcs.keys()])

def eval_script_node(node, state):
    cont = node_has_script_elements(node)
    while cont:
        node_tags = set(node.keys())
        tag = next((tag for tag in node_tags if tag in func_tags), False)
        if tag:
            node = script_funcs[tag](node, state)
        else:
            cont = False
    return node
