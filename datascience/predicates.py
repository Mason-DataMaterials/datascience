"""Predicate functions."""

import functools
import numbers
import numpy as np

__all__ = ['are']


class are:
    """Predicate functions. The class is named "are" for calls to where.

    For example, given a table, predicates can be used to pick rows as follows.

    >>> from datascience import Table
    >>> t = Table().with_columns([
    ...    'Sizes', ['S', 'M', 'L', 'XL'],
    ...    'Waists', [30, 34, 38, 42],
    ... ])
    >>> t.where('Sizes',  are.equal_to('L'))
    Sizes | Waists
    L     | 38
    >>> t.where('Waists', are.above(38))
    Sizes | Waists
    XL    | 42
    >>> t.where('Waists', are.above_or_equal_to(38))
    Sizes | Waists
    L     | 38
    XL    | 42
    >>> t.where('Waists', are.below(38))
    Sizes | Waists
    S     | 30
    M     | 34
    >>> t.where('Waists', are.below_or_equal_to(38))
    Sizes | Waists
    S     | 30
    M     | 34
    L     | 38
    >>> t.where('Waists', are.strictly_between(30, 38))
    Sizes | Waists
    M     | 34
    >>> t.where('Waists', are.between(30, 38))
    Sizes | Waists
    S     | 30
    M     | 34
    >>> t.where('Waists', are.between_or_equal_to(30, 38))
    Sizes | Waists
    S     | 30
    M     | 34
    L     | 38
    >>> t.where('Sizes',  are.equal_to('L'))
    Sizes | Waists
    L     | 38
    >>> t.where('Waists', are.not_above(38))
    Sizes | Waists
    S     | 30
    M     | 34
    L     | 38
    >>> t.where('Waists', are.not_above_or_equal_to(38))
    Sizes | Waists
    S     | 30
    M     | 34
    >>> t.where('Waists', are.not_below(38))
    Sizes | Waists
    L     | 38
    XL    | 42
    >>> t.where('Waists', are.not_below_or_equal_to(38))
    Sizes | Waists
    XL    | 42
    >>> t.where('Waists', are.not_strictly_between(30, 38))
    Sizes | Waists
    S     | 30
    L     | 38
    XL    | 42
    >>> t.where('Waists', are.not_between(30, 38))
    Sizes | Waists
    L     | 38
    XL    | 42
    >>> t.where('Waists', are.not_between_or_equal_to(30, 38))
    Sizes | Waists
    XL    | 42
    >>> t.where('Sizes', are.containing('L'))
    Sizes | Waists
    L     | 38
    XL    | 42
    >>> t.where('Sizes', are.not_containing('L'))
    Sizes | Waists
    S     | 30
    M     | 34
    >>> t.where('Sizes', are.contained_in('MXL'))
    Sizes | Waists
    M     | 34
    L     | 38
    XL    | 42
    >>> t.where('Sizes', are.contained_in('L'))
    Sizes | Waists
    L     | 38
    >>> t.where('Sizes', are.not_contained_in('MXL'))
    Sizes | Waists
    S     | 30
    """

    @staticmethod
    def equal_to(y):
        """Equal to y."""
        return _combinable(lambda x: _equal_or_float_equal(x, y))

    @staticmethod
    def above(y):
        """Greater than y."""
        return _combinable(lambda x: x > y)

    @staticmethod
    def below(y):
        """Less than y."""
        return _combinable(lambda x: x < y)

    @staticmethod
    def above_or_equal_to(y):
        """Greater than or equal to y."""
        return _combinable(lambda x: x >= y or _equal_or_float_equal(x, y))

    @staticmethod
    def below_or_equal_to(y):
        """Less than or equal to y."""
        return _combinable(lambda x: x <= y or _equal_or_float_equal(x, y))

    @staticmethod
    def strictly_between(y, z):
        """Greater than y and less than z."""
        return _combinable(lambda x: y < x < z)

    @staticmethod
    def between(y, z):
        """Greater than or equal to y and less than z."""
        return _combinable(lambda x: (y <= x < z) or _equal_or_float_equal(x, y))

    @staticmethod
    def between_or_equal_to(y, z):
        """Greater than or equal to y and less than or equal to z."""
        return _combinable(lambda x: (y <= x <= z) or _equal_or_float_equal(x, y) or _equal_or_float_equal(x, z))

    @staticmethod
    def containing(substring):
        """A string that contains within it the given substring."""
        return _combinable(lambda x: substring in x)

    @staticmethod
    def contained_in(superstring):
        """A string that is part of the given superstring."""
        return _combinable(lambda x: x in superstring)

###############
# Combination #
###############

class _combinable:
    """A wrapper that allows one-arg predicate functions to be combined."""
    def __init__(self, f):
        self.f = f
        functools.update_wrapper(self, f)

    def __call__(self, x):
        return self.f(x)

    def __and__(self, other):
        return _combinable(lambda x: self.f(x) and other.f(x))

    def __or__(self, other):
        return _combinable(lambda x: self.f(x) or other.f(x))

    def __neg__(self):
        return _combinable(lambda x: not self.f(x))

    def __xor__(self, other):
        return (self & -other) | (-self & other)

############
# Negation #
############

def _not(f):
    return lambda *args: -f(*args)

def _equal_or_float_equal(x, y):
    if isinstance(x, numbers.Real):
        return x == y or np.nextafter(x, 1) == y or np.nextafter(x, 0) == y
    else:
        return x == y

are.not_equal_to = not_equal_to
are.not_above = not_above
are.not_below = not_below
are.not_below_or_equal_to = not_below_or_equal_to 
are.not_above_or_equal_to = not_above_or_equal_to
are.not_strictly_between = not_strictly_between
are.not_between = not_between
are.not_between_or_equal_to = not_between_or_equal_to 
are.not_containing = not_containing
are.not_contained_in = not_contained_in

def not_equal_to(y):
    """Is not equal to y"""
    return _not(are.equal_to)
def not_above(y):
    """Is not above y"""
    return are.below_or_equal_to
def not_below(y):
    """Is not below y"""
    return are.above_or_equal_to
def not_below_or_equal_to(y):
    """Is neither below y nor equal to y"""
    return are.above
def not_above_or_equal_to(y):
    """Is neither above y nor equal to y"""
    return are.below
def not_strictly_between(y, z):
    """Is equal to y or equal to z or less than y or greater than z"""
    return  _not(are.strictly_between)
def not_between(y, z):
    """Is equal to y or less than y or greater than z"""
    return _not(are.between)
def not_between_or_equal_to(y,z):
    """Is less than y or greater than z"""
    return _not(are.between_or_equal_to)
def not_containing(substring):
    """A string that does not contain substring""" 
    return _not(are.containing)
def not_contained_in(superstring):
    """A string that is not contained within the superstring"""
    return _not(are.contained_in)