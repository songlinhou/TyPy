#!/usr/bin/python
# -*- coding: utf-8 -*-

from typy import TypeVar


def __get_default_vars(func):
    import inspect
    a = inspect.getargspec(func)
    return zip(a.args[-len(a.defaults):],a.defaults)

def Typed(user_func):
    def __typed_function__(*user_func_args,**user_func_kargs):
        #print "enter decorator"
        ret_type = 0
        type_dict = None
        default_vars = __get_default_vars(user_func)
        for (k,v) in default_vars:
            if k == 'types':
                type_dict = v
                if 'return' in type_dict.keys():
                    # return type of this function is defined
                    ret_type = type_dict['return']
                    #print "rettype=",ret_type
                    break
        remains = set(type_dict.keys()) - set(user_func.__code__.co_varnames)
        #print 'remains',remains
        if remains != set(['return']) and len(remains) != 0:
            raise AttributeError("some keys in 'types' do not match the names of parameters")
        
        for id,arg in enumerate(user_func_args):
            varname = user_func.__code__.co_varnames[id]
            if varname in type_dict.keys():
                # this parameter is strongly typed
                if type(arg) == TypeVar:
                    if arg.t_raw != type_dict[varname]:
                        raise AttributeError("expecting {} to be of {}, but got {}".format(varname,type_dict[varname],arg.t_raw))
                elif type(arg) != type_dict[varname]:
                    raise AttributeError("expecting {} to be of {}, but got {}".format(varname,type_dict[varname],type(arg)))
        
        for karg in user_func_kargs.keys():
            karg_value = user_func_kargs[karg]
            if karg in type_dict.keys():
                # this parameter is strongly typed
                if type(karg_value) == TypeVar:
                    if arg.t_raw != type_dict[karg]:
                        raise AttributeError("expecting {} to be of {}, but got {}".format(varname,type_dict[varname],arg.t_raw))
                elif type(arg) != type_dict[varname]:
                    raise AttributeError("expecting {} to be of {}, but got {}".format(varname,type_dict[varname],type(arg)))
        
        
        #print "user_func_args:",user_func_args
        #print "user_func_kargs:",user_func_kargs
        output = user_func(*user_func_args,**user_func_kargs)
        output_type = type(output)
        if output is None:
            output_type = None
        if type(output) == TypeVar:
            output_type = output.t_raw
        
        
        
        if ret_type != 0:
            if ret_type is None:
                if output is not None:
                    raise AttributeError("function should have no return value, got {}".format(output_type))
            if output_type != ret_type:
                raise AttributeError("expecting return type to be of {}, but got {}".format(ret_type,output_type))
        #print "exit decorator"
        return output
    return __typed_function__
    