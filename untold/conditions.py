# TODO:
# Scripting!!!
# Give operators saner names. That way, inequality operators can be
#   merged as well.
# Some further possible operators:
#   Booleans: NOT, XOR, m (or more, or fewer) out of n
#   Range matching for numerical values
#   One of these variables has one of these values
#     Implicitly included:
#       Variable has value in this list
#       Value is in one of these variables
#   {cond_list: [list of conditions]}


class InvalidCondition(Exception):
    pass


class InvalidOperator(Exception):
    pass


def is_equal(cond_node, state):
    varl = eval_condition(cond_node['varl'], state)
    varr = eval_condition(cond_node['varr'], state)
    return varl == varr


def is_not_equal(cond_node, state):
    varl = eval_condition(cond_node['varl'], state)
    varr = eval_condition(cond_node['varr'], state)
    return varl != varr


def is_greater_than(cond_node, state):
    varl = eval_condition(cond_node['varl'], state)
    varr = eval_condition(cond_node['varr'], state)
    return varl > varr


def is_greater_than_or_equal(cond_node, state):
    varl = eval_condition(cond_node['varl'], state)
    varr = eval_condition(cond_node['varr'], state)
    return varl >= varr


def is_lesser_than(cond_node, state):
    varl = eval_condition(cond_node['varl'], state)
    varr = eval_condition(cond_node['varr'], state)
    return varl < varr


def is_lesser_than_or_equal(cond_node, state):
    varl = eval_condition(cond_node['varl'], state)
    varr = eval_condition(cond_node['varr'], state)
    return varl <= varr


operators = {
    '==': is_equal,
    '!=': is_not_equal,
    '>': is_greater_than,
    '>=': is_greater_than_or_equal,
    '<': is_lesser_than,
    '<=': is_lesser_than_or_equal,
}


def eval_condition(cond_node, state):
    # Return literals as such
    if type(cond_node) in [bool, int, float, str]:
        return cond_node
    elif cond_node is None:
        return None
    # Constants and variables
    elif 'const' in cond_node.keys():
        return cond_node['const']
    elif 'var' in cond_node.keys():
        return state.get(cond_node['var'], None)
    # Binary operators
    elif 'op' in cond_node.keys():
        op = cond_node['op']
        if op in operators:
            return operators[op](cond_node, state)
        else:
            raise InvalidOperator
    else:
        raise InvalidCondition
