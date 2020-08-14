#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking code generators.**

This private submodule dynamically generates pure-Python code type-checking all
parameters and return values annotated with **PEP-compliant type hints**
(i.e., :mod:`beartype`-agnostic annotations compliant with
annotation-centric PEPs) of the decorated callable.

This private submodule implements `PEP 484`_ (i.e., "Type Hints") support by
transparently converting high-level objects and types defined by the
:mod:`typing` module into low-level code snippets independent of that module.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ TODO                              }....................
#FIXME: Resolve PEP-compliant forward references as well. Note that doing so is
#highly non-trivial -- sufficiently so, in fact, that we probably want to do so
#as cleverly documented in the "_pep563" submodule.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._decor._code._pep._pepsnip import (
    PARAM_KIND_TO_PEP_CODE_GET,
    PEP_CODE_GET_RETURN,
    PEP_CODE_RETURN_CHECKED,
)
from beartype._decor._code._pep._pephint import pep_code_check_hint
from beartype._decor._data import BeartypeData
from beartype._util.cache.utilcachetext import (
    format_text_cached, reraise_exception_cached)
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param,
    label_callable_decorated_return,
)
from inspect import Parameter

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CODERS                            }....................
def pep_code_check_param(
    data: BeartypeData,
    func_arg: Parameter,
    func_arg_index: int,
) -> str:
    '''
    Python code type-checking the parameter with the passed signature and index
    annotated by a **PEP-compliant type hint** (e.g.,:mod:`beartype`-agnostic
    annotation compliant with annotation-centric PEPs) of the decorated
    callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.
    func_arg : Parameter
        :mod:`inspect`-specific object describing this parameter.
    func_arg_index : int
        0-based index of this parameter in this callable's signature.

    Returns
    ----------
    str
        Python code type-checking this parameter against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))
    assert isinstance(func_arg, Parameter), (
        '{!r} not parameter metadata.'.format(func_arg))
    assert isinstance(func_arg_index, int), (
        '{!r} not parameter index.'.format(func_arg_index))

    # Python code template localizing this parameter if this kind of parameter
    # is supported *OR* "None" otherwise.
    get_arg_code_template = PARAM_KIND_TO_PEP_CODE_GET.get(func_arg.kind, None)

    # If this kind of parameter is unsupported...
    #
    # Note this edge case should *NEVER* occur, as the parent function should
    # have simply ignored this parameter.
    if get_arg_code_template is None:
        #FIXME: Generalize this label to embed the kind of parameter as well
        #(e.g., "positional-only", "keyword-only", "variadic positional"),
        #probably by defining a new label_callable_decorated_param_kind().

        # Human-readable label describing this parameter.
        hint_label = label_callable_decorated_param(
            func=data.func, param_name=func_arg.name)

        # Raise an exception embedding this label.
        raise BeartypeDecorHintPepException(
            '{} kind {!r} unsupported.'.format(hint_label, func_arg.kind))
    # Else, this kind of parameter is supported. Ergo, this code is non-"None".

    # Attempt to...
    try:
        # Unmemoized parameter-specific Python code type-checking this
        # parameter, formatted from...
        param_code_check = format_text_cached(
            # Memoized parameter-agnostic code type-checking this parameter.
            text=pep_code_check_hint(func_arg.annotation),
            # Object representation of this parameter's name, as documented by
            # the pep_code_check_hint() docstring.
            format_str=repr(func_arg.name),
        )
    # If the prior call to the memoized _pep_code_check() function raises a
    # cached exception...
    except BeartypeDecorHintPepException as exception:
        # Human-readable label describing this parameter.
        hint_label = (
            label_callable_decorated_param(
                func=data.func, param_name=func_arg.name) + ' PEP type hint')

        # Reraise this cached exception's memoized parameter-agnostic message
        # into an unmemoized parameter-specific message.
        reraise_exception_cached(exception=exception, format_str=hint_label)

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Return Python code to...
    return (
        # Localize this parameter *AND*...
        get_arg_code_template.format(
            arg_name=func_arg.name, arg_index=func_arg_index) +
        # Type-check this parameter.
        param_code_check
    )


def pep_code_check_return(data: BeartypeData) -> str:
    '''
    Python code type-checking the return value annotated with a **PEP-compliant
    type hint** (e.g.,:mod:`beartype`-agnostic annotation compliant with
    annotation-centric PEPs) of the decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be type-checked.

    Returns
    ----------
    str
        Python code type-checking this return value against this hint.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert isinstance(data, BeartypeData), (
        '{!r} not @beartype data.'.format(data))

    # Attempt to...
    try:
        # Unmemoized return value-specific Python code type-checking this
        # return value, formatted from...
        return_code_check = format_text_cached(
            # Memoized return value-agnostic code type-checking this parameter.
            text=pep_code_check_hint(data.func_sig.return_annotation),
            # Object representation of the magic string implying this return
            # value, as documented by the pep_code_check_hint() docstring.
            format_str=repr('return'),
        )
    # If the prior call to the memoized _pep_code_check() function raises a
    # cached exception...
    except BeartypeDecorHintPepException as exception:
        # Human-readable label describing this return.
        hint_label = (
            label_callable_decorated_return(data.func) + ' PEP type hint')

        # Reraise this cached exception's memoized return value-agnostic
        # message into an unmemoized return value-specific message.
        reraise_exception_cached(exception=exception, format_str=hint_label)

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Return Python code to...
    return (
        # Call the decorated callable and localize its return value *AND*...
        PEP_CODE_GET_RETURN +
        # Type-check this return value *AND*...
        return_code_check +
        # Return this value from this wrapper function.
        PEP_CODE_RETURN_CHECKED
    )