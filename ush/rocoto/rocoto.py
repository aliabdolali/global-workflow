#!/usr/bin/env python3

'''
    MODULE:
        rocoto.py

    ABOUT:
        Helper module to create tasks, metatasks, and dependencies
'''

def create_metatask(task_dict, metatask_dict):
    '''
    create a Rocoto metatask given a dictionary containing task and metatask information
    :param metatask_dict: metatask key-value parameters
    :type metatask_dict: dict
    :param task_dict: task key-value parameters
    :type task_dict: dict
    :return: Rocoto metatask
    :rtype: list
    '''

    # Grab metatask info from the metatask_dict
    metataskname = metatask_dict.get('metataskname', 'demometatask')
    varname = metatask_dict.get('varname', 'demovar')
    varval = metatask_dict.get('varval', 1)
    vardict = metatask_dict.get('vardict', None)

    strings = []

    strings.append(f'<metatask name="{metataskname}">\n')
    strings.append('\n')
    strings.append(f'\t<var name="{varname}">{str(varval)}</var>\n')
    if vardict is not None:
        for key in vardict.keys():
            value = str(vardict[key])
            strings.append(f'\t<var name="{key}">{value}</var>\n')
    strings.append('\n')
    tasklines = create_task(task_dict)
    for tl in tasklines:
        strings.append(f'{tl}') if tl == '\n' else strings.append(f'\t{tl}')
    strings.append('\n')
    strings.append('</metatask>\n')

    return strings


def create_task(task_dict):
    '''
    create a Rocoto task given a dictionary containing task information
    :param task_dict: task key-value parameters
    :type task_dict: dict
    :return: Rocoto task
    :rtype: list
    '''

    # Grab task info from the task_dict
    taskname = task_dict.get('taskname', 'demotask')
    cycledef = task_dict.get('cycledef', 'democycle')
    maxtries = task_dict.get('maxtries', 3)
    final = task_dict.get('final', False)
    command = task_dict.get('command', 'sleep 10')
    jobname = task_dict.get('jobname', 'demojob')
    account = task_dict.get('account', 'batch')
    queue = task_dict.get('queue', 'debug')
    partition = task_dict.get('partition', None)
    walltime = task_dict.get('walltime', '00:01:00')
    log = task_dict.get('log', 'demo.log')
    native = task_dict.get('native', None)
    memory = task_dict.get('memory', None)
    resources = task_dict.get('resources', None)
    envar = task_dict.get('envar', None)
    dependency = task_dict.get('dependency', None)

    str_maxtries = str(maxtries)
    str_final = ' final="true"' if final else ''
    envar = envar if isinstance(envar, list) else [envar]

    strings = []

    strings.append(f'<task name="{taskname}" cycledefs="{cycledef}" maxtries="{str_maxtries}"{str_final}>\n')
    strings.append('\n')
    strings.append(f'\t<command>{command}</command>\n')
    strings.append('\n')
    strings.append(f'\t<jobname><cyclestr>{jobname}</cyclestr></jobname>\n')
    strings.append(f'\t<account>{account}</account>\n')
    strings.append(f'\t<queue>{queue}</queue>\n')
    if partition is not None:
        strings.append(f'\t<partition>{partition}</partition>\n')
    if resources is not None:
        strings.append(f'\t{resources}\n')
    strings.append(f'\t<walltime>{walltime}</walltime>\n')
    if memory is not None:
        strings.append(f'\t<memory>{memory}</memory>\n')
    if native is not None:
        strings.append(f'\t<native>{native}</native>\n')
    strings.append('\n')
    strings.append(f'\t<join><cyclestr>{log}</cyclestr></join>\n')
    strings.append('\n')

    if envar[0] is not None:
        for e in envar:
            strings.append(f'\t{e}\n')
        strings.append('\n')

    if dependency is not None:
        strings.append('\t<dependency>\n')
        for d in dependency:
            strings.append(f'\t\t{d}\n')
        strings.append('\t</dependency>\n')
        strings.append('\n')

    strings.append('</task>\n')

    return strings


def add_dependency(dep_dict):
    '''
    create a simple Rocoto dependency given a dictionary with dependency information
    :param dep_dict: dependency key-value parameters
    :type dep_dict: dict
    :return: Rocoto simple dependency
    :rtype: str
    '''

    dep_condition = dep_dict.get('condition', None)
    dep_type = dep_dict.get('type', None)

    if dep_type in ['task', 'metatask']:

        string = add_task_tag(dep_dict)

    elif dep_type in ['data']:

        string = add_data_tag(dep_dict)

    elif dep_type in ['cycleexist']:

        string = add_cycle_tag(dep_dict)

    elif dep_type in ['streq', 'strneq']:

        string = add_streq_tag(dep_dict)

    else:

        msg = f'Unknown dependency type {dep_dict["type"]}'
        raise KeyError(msg)

    if dep_condition is not None:
        string = f'<{dep_condition}>{string}</{dep_condition}>'

    return string


def add_task_tag(dep_dict):
    '''
    create a simple task or metatask tag
    :param dep_dict: dependency key-value parameters
    :type dep_dict: dict
    :return: Rocoto simple task or metatask dependency
    :rtype: str
    '''

    dep_type = dep_dict.get('type', None)
    dep_name = dep_dict.get('name', None)
    dep_offset = dep_dict.get('offset', None)

    if dep_name is None:
        msg = f'a {dep_type} name is necessary for {dep_type} dependency'
        raise KeyError(msg)

    string = '<'
    string += f'{dep_type}dep {dep_type}="{dep_name}"'
    if dep_offset is not None:
        string += f' cycle_offset="{dep_offset}"'
    string += '/>'

    return string

def add_data_tag(dep_dict):
    '''
    create a simple data tag
    :param dep_dict: dependency key-value parameters
    :type dep_dict: dict
    :return: Rocoto simple task or metatask dependency
    :rtype: str
    '''

    dep_type = dep_dict.get('type', None)
    dep_data = dep_dict.get('data', None)
    dep_offset = dep_dict.get('offset', None)

    if dep_data is None:
        msg = f'a data value is necessary for {dep_type} dependency'
        raise KeyError(msg)

    if not isinstance(dep_data, list):
        dep_data = [dep_data]

    if not isinstance(dep_offset, list):
        dep_offset = [dep_offset]

    assert len(dep_data) == len(dep_offset)

    strings = ['<datadep>']
    for data, offset in zip(dep_data, dep_offset):
        if '@' in data:
            offset_str = '' if  offset in [None, ''] else f' offset="{offset}"'
            offset_string_b = f'<cyclestr{offset_str}>'
            offset_string_e = '</cyclestr>'
        else:
            offset_string_b = ''
            offset_string_e = ''

        strings.append(f'{offset_string_b}{data}{offset_string_e}')

    strings.append('</datadep>')

    return ''.join(strings)

def add_cycle_tag(dep_dict):
    '''
    create a simple cycle exist tag
    :param dep_dict: dependency key-value parameters
    :type dep_dict: dict
    :return: Rocoto simple task or metatask dependency
    :rtype: str
    '''

    dep_type = dep_dict.get('type', None)
    dep_offset = dep_dict.get('offset', None)

    if dep_offset is None:
        msg = f'an offset value is necessary for {dep_type} dependency'
        raise KeyError(msg)

    string = f'<cycleexistdep cycle_offset="{dep_offset}"/>'

    return string

def add_streq_tag(dep_dict):
    '''
    create a simple string comparison tag
    :param dep_dict: dependency key-value parameters
    :type dep_dict: dict
    :return: Rocoto simple task or metatask dependency
    :rtype: str
    '''

    dep_type = dep_dict.get('type', None)
    dep_left = dep_dict.get('left', None)
    dep_right = dep_dict.get('right', None)

    fail = False
    msg = ''
    if dep_left is None:
        msg += f'a left value is necessary for {dep_type} dependency'
        fail = True
    if dep_right is None:
        if fail:
            msg += '\n'
        msg += f'a right value is necessary for {dep_type} dependency'
        fail = True
    if fail:
        raise KeyError(msg)

    string = f'<{dep_type}><left>{dep_left}</left><right>{dep_right}</right></{dep_type}>'

    return string


def _traverse(o, tree_types=(list, tuple)):
    '''
    Traverse through a list of lists or tuples and yeild the value
    Objective is to flatten a list of lists or tuples
    :param o: list of lists or not
    :type o: list, tuple, scalar
    :param tree_types: trees to travers
    :type tree_types: tuple
    :return: value in the list or tuple
    :rtype: scalar
    '''

    if isinstance(o, tree_types):
        for value in o:
            for subvalue in _traverse(value, tree_types):
                yield subvalue
    else:
        yield o


def create_dependency(dep_condition=None, dep=None):
    '''
    create a compound dependency given a list of dependendies, and compounding condition
    the list of dependencies are created using add_dependency
    :param dep_condition: dependency condition
    :type dep_condition: boolean e.g. and, or, true, false
    :param dep: dependency
    :type dep: str or list
    :return: Rocoto compound dependency
    :rtype: list
    '''

    dep = dep if isinstance(dep, list) else [dep]

    strings = []

    if dep_condition is not None:
        strings.append(f'<{dep_condition}>')

    if dep[0] is not None:
        for d in dep:
            if dep_condition is None:
                strings.append(f'{d}')
            else:
                for e in _traverse(d):
                    strings.append(f'\t{e}')

    if dep_condition is not None:
        strings.append(f'</{dep_condition}>')

    return strings


def create_envar(name=None,value=None):
    '''
    create an Rocoto environment variable given name and value
    returns the environment variable as a string
    :param name: name of the environment variable
    :type name: str
    :param value: value of the environment variable
    :type value: str or float or int or unicode
    :return: Rocoto environment variable key-value pair
    :rtype: str
    '''

    string = ''
    string += '<envar>'
    string += f'<name>{name}</name>'
    string += f'<value>{str(value)}</value>'
    string += '</envar>'

    return string


def create_cycledef(group=None, start=None, stop=None, step=None):
    '''
    create an Rocoto cycle definition
    returns the environment variable as a string
    :param group: cycle definition group name
    :type group: str
    :param start: cycle start datetime
    :type start: str
    :param end: cycle end datetime
    :type stop: str
    :param step: cycle interval (timedelta)
    :type interval: str
    :param value: value of the environment variable
    :type value: str or float or int or unicode
    :return: Rocoto cycledef variable string
    :rtype: str
    '''

    string = ''
    string += f'<cycledef group="{group}">'
    string += f'{start} {stop} {step}'
    string += '</cycledef>'

    return string


def create_entity(name=None, value=None):
    '''
    create an XML ENTITY variable given name and value
    returns the variable as a string
    :param name: name of the variable
    :type name: str
    :param value: value of the variable
    :type value: str or float or int or unicode
    :return: XML entity variable key-value pair
    :rtype: str
    '''

    return f'<!ENTITY {name} "{value}">'

