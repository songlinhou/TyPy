#!/usr/bin/python
# -*- coding: utf-8 -*-


class TypeBase(object):
    __static_types__ = {}
    def __init__(self):
        original_members = ['__static_types__', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__used_keys__', '__weakref__','submit', 'get_members']
        user_defined_members = set(dir(self)) - set(original_members)
        functions,variables= [],[]
        for name in user_defined_members:
            if callable(getattr(self,name)):
                functions.append(name)
            else:
                variables.append(name)
        #print 'func',functions
        #print 'var',variables
        
        
                
        
    def __setattr__(self,attr,value):
        t_value = TypeVar(type(value),value)
        if hasattr (self,attr):
            # need to check the type
            # value is of TypeVar
            prestored = getattr(self,attr)
            
            if type(prestored) == TypeVar:
                # if the attr is an attr defined by self.attr
                if type(value) == TypeVar:
                    if prestored.t_raw == value.t_raw:
                        super(TypeBase,self).__setattr__(attr,t_value)
                        return
                    else:
                        print "value.t == prestored.t:",value.t_raw,prestored.t_raw,prestored.t_raw == value.t_raw
                        raise TypeError("{} should be of type {}, but got {}".format(str(attr), prestored.t, value.t))

                # value is not of TypeVar
                elif type(value) == prestored.t_raw:
                    super(TypeBase,self).__setattr__(attr,t_value)
                    return
                else:
                    raise TypeError("{} should be of type {}, but got {}".format(str(attr), prestored.t, type(value)))
            else:
                if attr in dir(self):
                    # this attr is a class attr, I will just keep it as it is
                    TypeBase.__static_types__[attr] = type(prestored)
                    if type(value) == TypeVar:
                        if value.t_raw == TypeBase.__static_types__[attr]:
                            super(TypeBase,self).__setattr__(attr,value)
                            return
                        else:
                            raise TypeError("{} should be of type {}, but got {}".format(str(attr), TypeBase.__static_types__[attr], value.t_raw))
                    elif type(value) == TypeBase.__static_types__[attr]:
                        super(TypeBase,self).__setattr__(attr,value)
                        return
                    else:
                        raise TypeError("{} should be of type {}, but got {}".format(str(attr), TypeBase.__static_types__[attr], type(value)))
                else:
                    raise TypeError("{} is not defined in instances of {}".format(str(attr), self.__class__))
                        
                
        else:
            super(TypeBase,self).__setattr__(attr,t_value)
        
     

class TypeVar(object):
    def __init__(self,objType,value=None):
        if type(objType) != type and type(objType) != TypeDef:
            raise TypeError("the 1st parameter should be of 'type' type")
        if value is not None:
            if type(value) != objType:
                raise TypeError("expected the type of 'value' to be {}, got {}".format(objType,type(value)))
        self.__objType__ = objType if type(objType) == TypeDef else TypeDef(objType)
        self.__objValue__ = value
        
    def __getattr__(self,name):
        if hasattr(super(TypeVar,self),name):
            return getattr(super(TypeVar,self),name)
        elif hasattr(self.__objValue__,name):
            return getattr(self.__objValue__,name)
        
    def __dir__(self):
        dir_list = dir(super(TypeVar,self))
        dir_list.extend(dir(self.__objValue__))
        return dir_list
     
    @staticmethod
    def var(value):
        return TypeVar.__create__(type(value),value)
    
    @staticmethod
    def __create__(objType,value=None):
        instance = TypeVar(objType,value)
        return instance
        
    
    def _consistent_type(self,obj):
        if type(obj) != TypeDef:
            return self.t_raw == type(obj)
        return self.t_raw == obj.t_raw
    
    def _is_value_and_type_consistent(self):
        if type(self.__objType__) == type:
            return self.__objType__ == type(self.__objValue__)
        if type(self.__objType__) == TypeDef:
            return self.__objType__.t_raw == type(self.__objValue__)
        
    def _is_computable(self,raw_type):
        number_types = [int,float,long,complex]
        if self.t_raw in number_types and raw_type in number_types:
            return True
        else:
            return False
        
    def __get_type_and_value(self,other):
        if type(other) == TypeDef:
            raw_type = other.t_raw
            raw_value = other.v
        else:
            raw_type = type(other)
            raw_value = other
        return raw_type,raw_value
    
    def assign(self,value):
        if value == None:
            self.v = None
            return
        if type(value) == TypeVar:
            if self.t == value.t:
                self.__objValue__ = value.v
                return
            else:
                raise TypeError("Assignment failed. expecting {}, got {}".format(self.t,value.t))
        if self.t_raw == type(value):
            self.__objValue__ = value
        else:
            raise TypeError("Assignment failed. expecting {}, got {}".format(self.t_raw,type(value)))
    
    def __operation_value__(self,value):
        if type(value) != TypeVar:
            ret = TypeVar.__create__(type(value),value)
            return ret
        else:
            return value
        
    def __add__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v + raw_value.v
        else:
            value =  self.v + raw_value
        return self.__operation_value__(value)
        
    def __sub__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v - raw_value.v
        else:
            value =  self.v - raw_value
        return self.__operation_value__(value)
    
    def __mul__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v * raw_value.v
        else:
            value =  self.v * raw_value 
        return self.__operation_value__(value)
    
    def __pow__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        print "raw_type,raw_value",raw_type,raw_value
        if hasattr(raw_value,'v'):
            value =   self.v ** raw_value.v
        else:
            value =   self.v ** raw_value
        return self.__operation_value__(value)
    
    def __truediv__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v / raw_value.v
        else:
            value =  self.v / raw_value
        return self.__operation_value__(value)
    
    def __floordiv__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v // raw_value.v
        else:
            value =  self.v // raw_value
        return self.__operation_value__(value)
    
    def __mod__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v % raw_value.v
        else:
            value =  self.v % raw_value
        return self.__operation_value__(value)
    
    def __lshift__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v << raw_value.v
        else:
            value =  self.v << raw_value
        return self.__operation_value__(value)
    
    def __rshift__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v >> raw_value.v
        else:
            value =  self.v >> raw_value
        return self.__operation_value__(value)
    
    def __and__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v & raw_value.v
        else:
            value =  self.v & raw_value
        return self.__operation_value__(value)
    
    def __or__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v | raw_value.v
        else:
            value =  self.v | raw_value
        return self.__operation_value__(value)
    
    def __eq__(self, other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v == raw_value.v
        else:
            value =  self.v == raw_value
        return self.__operation_value__(value)
    
    def __ne__(self, other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v != raw_value.v
        else:
            value =  self.v != raw_value
        return self.__operation_value__(value)
    
    def __xor__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v ^ raw_value.v
        else:
            value =  self.v ^ raw_value
        return self.__operation_value__(value)
    
    def __lt__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v < raw_value.v
        else:
            value =  self.v < raw_value
        return self.__operation_value__(value)
    
    def __gt__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v > raw_value.v
        else:
            value =  self.v > raw_value
        return self.__operation_value__(value)
    
    def __ge__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v >= raw_value.v
        else:
            value =  self.v >= raw_value
        return self.__operation_value__(value)
    
    def __le__(self,other):
        raw_type,raw_value = self.__get_type_and_value(other)
        if hasattr(raw_value,'v'):
            value =  self.v <= raw_value.v
        else:
            value =  self.v <= raw_value
        return self.__operation_value__(value)
    
    
    def __invert__(self):
        value = ~self.v
        return self.__operation_value__(value)
    
    def __str__(self):
        return str(self.__objValue__)

    def __repr__(self):
        return self.__str__()
    
    @property
    def v(self):
        return self.__objValue__
    
    @property
    def t(self):
        return self.__objType__
    
    @property
    def t_raw(self):
        return self.__objType__.t
    
    def __type__(self):
        return str(self.t)
        
            
class TypeDef(object):
    def __init__(self,objType):
        if type(objType) == type:
            self.__objType__ = objType
        else:
            raise TypeError("the 1st parameter should be of 'type' type")
    def __str__(self):
        return str(self.__objType__)
    def __repr__(self):
        return "Type wrapper for " + repr(self.__objType__)
    
    @property
    def t(self):
        return self.__objType__

    
    