# -*- coding: utf-8 -*-
from abc import ABCMeta
import collections
from aiida.orm import Data

__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file."
__version__ = "0.7.0"
__authors__ = "The AiiDA team."


class BaseType(Data):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        try:
            getattr(self, '_type')
        except AttributeError:
            raise RuntimeError("Derived class must define the _type class member")

        super(BaseType, self).__init__(**self._create_init_args(*args, **kwargs))

    def set_typevalue(self, typevalue):
        _type, value = typevalue
        self._type = _type
        if value:
            self.value = value
        else:
            self.value = _type()

    @property
    def value(self):
        return self.get_attr('value')

    @value.setter
    def value(self, value):
        self._set_attr('value', self._type(value))

    def __str__(self):
        return self.value.__str__()

    def __repr__(self):
        return self.value.__repr__()

    def __eq__(self, other):
        if isinstance(other, BaseType):
            return self.value == other.value
        else:
            return self.value == other

    def __ne__(self, other):
        if isinstance(other, BaseType):
            return self.value != other.value
        else:
            return self.value != other

    def new(self, value=None):
        return self.__class__(typevalue=(self._type, value))

    def _create_init_args(self, *args, **kwargs):
        if args:
            assert not kwargs, "Cannot have positional arguments and kwargs"
            assert len(args) == 1, \
                "Simple data can only take at most one positional argument"

            kwargs['typevalue'] = (self._type, self._type(args[0]))

        elif 'dbnode' not in kwargs:
            if 'typevalue' in kwargs:
                assert kwargs['typevalue'][0] is self._type
                if kwargs['typevalue'][1] is not None:
                    kwargs['typevalue'] = \
                        (self._type, self._type(kwargs['typevalue'][1]))
            else:
                kwargs['typevalue'] = (self._type, None)

        else:
            assert len(kwargs) == 1, \
                "When specifying dbnode it can be the only kwarg"

        return kwargs


class NumericType(BaseType):
    def __add__(self, other):
        if isinstance(other, NumericType):
            return self.new(self.value + other.value)
        else:
            return self.new(self.value + other)

    def __iadd__(self, other):
        assert not self.is_stored
        if isinstance(other, NumericType):
            self.value += other.value
        else:
            self.value += other
        return self

    def __radd__(self, other):
        assert not isinstance(other, NumericType)
        return self.new(other + self.value)

    def __sub__(self, other):
        if isinstance(other, NumericType):
            return self.new(self.value - other.value)
        else:
            return self.new(self.value - other)

    def __isub__(self, other):
        assert not self.is_stored
        if isinstance(other, NumericType):
            self.value -= other.value
        else:
            self.value -= other
        return self

    def __rsub__(self, other):
        assert not isinstance(other, NumericType)
        return self.new(other - self.value)

    def __mul__(self, other):
        if isinstance(other, NumericType):
            return self.new(self.value * other.value)
        else:
            return self.new(self.value * other)

    def __imul__(self, other):
        assert not self.is_stored
        if isinstance(other, NumericType):
            self.value *= other.value
        else:
            self.value *= other
        return self

    def __rmul__(self, other):
        assert not isinstance(other, NumericType)
        return self.new(other * self.value)

    def __pow__(self, power, modulo=None):
        if isinstance(power, NumericType):
            return self.new(self.value ** power.value)
        else:
            return self.new(self.value ** power)

    def __lt__(self, other):
        if isinstance(other, NumericType):
            return self.value < other.value
        else:
            return self.value < other

    def __le__(self, other):
        if isinstance(other, NumericType):
            return self.value <= other.value
        else:
            return self.value <= other

    def __gt__(self, other):
        if isinstance(other, NumericType):
            return self.value > other.value
        else:
            return self.value > other

    def __ge__(self, other):
        if isinstance(other, NumericType):
            return self.value >= other.value
        else:
            return self.value >= other

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)


class Float(NumericType):
    _type = float


class Int(NumericType):
    _type = int


class Str(BaseType):
    _type = str


class Bool(BaseType):
    _type = bool

    def __int__(self):
        return 0 if not self.value else 1


class List(Data, collections.MutableSequence):
    _LIST_KEY = 'list'

    def __getitem__(self, item):
        return self._get_list()[item]

    def __setitem__(self, key, value):
        l = self._get_list()
        l[key] = value
        if not self._using_list_reference():
            self._set_list(l)

    def __delitem__(self, key):
        l = self._get_list()
        del l[key]
        if not self._using_list_reference():
            self._set_list(l)

    def __len__(self):
        return len(self._get_list())

    def __str__(self):
        return self._get_list().__str__()

    def append(self, value):
        l = self._get_list()
        l.append(value)
        if not self._using_list_reference():
            self._set_list(l)

    def extend(self, L):
        l = self._get_list()
        l.extend(L)
        if not self._using_list_reference():
            self._set_list(l)

    def insert(self, i, value):
        l = self._get_list()
        l.insert(i, value)
        if not self._using_list_reference():
            self._set_list(l)

    def remove(self, value):
        del self[value]

    def pop(self, **kwargs):
        l = self._get_list()
        l.pop(**kwargs)
        if not self._using_list_reference():
            self._set_list(l)

    def index(self, value):
        return self._get_list().index(value)

    def count(self, value):
        return self._get_list().count(value)

    def sort(self, cmp=None, key=None, reverse=False):
        l = self._get_list()
        l.sort(cmp, key, reverse)
        if not self._using_list_reference():
            self._set_list(l)

    def reverse(self):
        l = self._get_list()
        l.reverse()
        if not self._using_list_reference():
            self._set_list(l)

    def _get_list(self):
        try:
            return self.get_attr(self._LIST_KEY)
        except AttributeError:
            self._set_list(list())
            return self.get_attr(self._LIST_KEY)

    def _set_list(self, list_):
        if not isinstance(list_, list):
            raise TypeError("Must supply list type")
        self._set_attr(self._LIST_KEY, list_)

    def _using_list_reference(self):
        """
        This function tells the class if we are using a list reference.  This
        means that calls to self.get_list return a reference rather than a copy
        of the underlying list and therefore self._set_list need not be called.
        This knwoledge is essential to make sure this class is performant.

        Currently the implementation assumes that if the node needs to be
        stored then it is using the attributes cache which is a reference.

        :return: True if using self._get_list returns a reference to the
            underlying sequence.  False otherwise.
        :rtype: bool
        """
        return self._to_be_stored

def get_true_node():
    """
    Return a Bool Data node, with value True

    Cannot be done as a singleton in the module, because it would be generated
    at import time, with the risk that (e.g. in the tests, or at the very first use
    of AiiDA) a user is not yet defined in the DB (but a user is mandatory in the
    DB before you can create new Nodes in AiiDA).
    """
    TRUE = Bool(typevalue=(bool, True))
    return TRUE

def get_false_node():
    """
    Return a Bool Data node, with value False

    Cannot be done as a singleton in the module, because it would be generated
    at import time, with the risk that (e.g. in the tests, or at the very first use
    of AiiDA) a user is not yet defined in the DB (but a user is mandatory in the
    DB before you can create new Nodes in AiiDA).
    """
    FALSE = Bool(typevalue=(bool, False))
    return FALSE
