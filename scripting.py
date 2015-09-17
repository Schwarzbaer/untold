import random

from conditions import eval_condition

# Scripting elements -------------------------------------------------

# Common features of list-bearing keywords, specifically:
# IF

def eval_list_node(node_list, state):
    virt_list = []
    for list_node in node_list:
        if 'if' in list_node.keys():
            cond_node = list_node['if']
            if eval_condition(cond_node, state):
                virt_list.append(list_node)
            else:
                pass
        else:
            # No 'if' keyword encountered
            virt_list.append(list_node)
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
        if eval_condition(condition, state):
            virt_node = case_node.copy()
            del virt_node['case']
            virt_node.update(leaf)
            return virt_node
    raise CaseWithoutActiveCond

# CHOICE
# {choice: [{weights: 1},
#           {weights: 1}]}

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

# Managerial

script_funcs = {
    'case': eval_case_node,
    'choice': eval_choice_node,
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
