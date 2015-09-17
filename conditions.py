# Conditions ---------------------------------------------------------

class InvalidCondition(Exception):
    pass

def eval_condition(cond_node, state):
    # Returns True or False
    # True, False: Return just that
    # {var: varname, val: value} # DONE: Exact match: TODO: value in list-in-state-variable
    # {var: varname, val: [value]} # TODO: Both list-in-state-variable and conditional-value can be lists
    # {var: varname, val_gt: value1, val_lt: value2} # TODO
    # {cond_list: [list of conditions]} # TODO
    if type(cond_node) in [bool, int, float, str]:
        return cond_node
    # FIXME: This should be folded into the one above, but NoneType
    # is undefined despite type(None) == NoneType. WTF is going on?
    elif cond_node == None:
        return None
    elif 'const' in cond_node.keys():
        return cond_node['const']
    elif 'var' in cond_node.keys():
        return state.get(cond_node['var'], None)
    elif 'op' in cond_node.keys():
        op = cond_node['op']
        varl = eval_condition(cond_node['varl'], state)
        varr = eval_condition(cond_node['varr'], state)
        if op == '==':
            return varl == varr
        elif op == '!=':
            return varl != varr
        elif op == '<=':
            return varl <= varr
        elif op == '>=':
            return varl >= varr
        elif op == '<':
            return varl < varr
        elif op == '>':
            return varl > varr
    else:
        # This is temporary, until the new syntax is implemented.
        raise InvalidCondition
