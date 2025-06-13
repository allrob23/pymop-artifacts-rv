import inspect

def getKwOrPosArg(argKw, argPos, kw):
    '''
    tries to get the keyword argument;
    if not found looks for the positional one.
    '''
    if argKw in kw['kwargs']:
        return kw['kwargs'].get(argKw)
    
    if len(kw['args']) > argPos:
        return kw['args'][argPos]

    return None

def getStackTrace():
    '''
    returns the stack trace of the current execution point.
    '''
    stack = inspect.stack()

    return stack

def parseStackTrace(stack):
    '''
    returns the stack trace in a readable format.
    format= path:line -> path:line
    '''
    stack_trace = ''
    for i, line in enumerate(stack):
        stack_trace += f"{line.filename}:{line.lineno} \n{'-> ' if i < len(stack) - 1 else ''}"

    return stack_trace

def has_self_in_args(func):
    try:
        if hasattr(func, '__code__'):
            params = func.__code__.co_varnames[:func.__code__.co_argcount]

            if params and len(params) > 0 and params[0] == 'self':
                return True

        # This one is more reliable than func.__code__.co_varnames but slower
        params = list(inspect.signature(func).parameters.values())
        if params and params[0].name == 'self':
            return True
    
    # inspect.signature sometimes raise the following error
    # when getting signature of builtin functions:
    # ValueError: <built-in function enable> builtin has invalid signature
    except ValueError:
        pass
    
    return False