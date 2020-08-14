#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant code snippets.**

This private submodule *only* defines **PEP-compliant code snippets** (i.e.,
triple-quoted pure-Python code constants formatted and concatenated together
into wrapper functions implementing type-checking for decorated callables
annotated by PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ PARAMETERS                        }....................
from inspect import Parameter

# ....................{ CODE                              }....................
PEP_CODE_PITH_ROOT_EXPR = '__beartype_pith_root'
'''
Name of the local variable providing the **root pith** (i.e., value of the
current parameter or return value being type-checked by the current call).
'''


PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER = 'PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER'
'''
Placeholder substring embedded in the generic parameter- and return-agnostic
code generated by the memoized
:func:`:mod:`beartype._decor._code._pep._pephint.pep_code_check_hint` function,
subsequently replaced with the name of the current parameter or ``return`` for
return value in the unique parameter- and return-specific code generated by the
non-memoized
:func:`:mod:`beartype._decor._code._pep.pepcode.pep_code_check_param` and
:func:`:mod:`beartype._decor._code._pep.pepcode.pep_code_check_return`
functions.

Design
----------
This substring is agnostic of any specific callable and is thus generically
memoizable for all callables. This substring is intentionally a magic
unformattable bare identifier protected against erroneous formatting by the
frequently called :moth:`str.format` method, which the
:mod:`beartype._decor._code._pep._pephint` submodule then globally replaces
before its evaluation as code with the magic formattable substring
:attr:`beartype._util.cache.utilcachetext.CACHED_FORMAT_VAR`, which the
:mod:`beartype._decor._code._pep.pepcode` submodule then replaces with either
the name of the current parameter or ``return`` for return values by calling
the :func:`beartype._util.cache.utilcachetext.format_text_cached` function.

Unmaintainability is the well-known to be the high price of ludicrous speed.
'''

# ....................{ CODE ~ param                      }....................
#FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
#which are the optimal means of performing string formatting.
PARAM_KIND_TO_PEP_CODE_GET = {
    # Snippet localizing any positional or keyword parameter as follows:
    #
    # * If this parameter's 0-based index (in the parameter list of the
    #   decorated callable's signature) does *NOT* exceed the number of
    #   positional parameters passed to the wrapper function, localize this
    #   positional parameter from the wrapper's variadic "*args" tuple.
    # * Else if this parameter's name is in the dictionary of keyword
    #   parameters passed to the wrapper function, localize this keyword
    #   parameter from the wrapper's variadic "*kwargs" tuple.
    # * Else, this parameter is unpassed. In this case, localize this parameter
    #   as a placeholder value guaranteed to *NEVER* be passed to any wrapper
    #   function: the private "__beartypistry" singleton passed to this wrapper
    #   function as a hidden default parameter and thus accessible here.
    Parameter.POSITIONAL_OR_KEYWORD: '''
    {pith_root_name} = (
        args[{{arg_index}} if {{arg_index}} < len(args) else
        kwargs.get({{arg_name!r}}, __beartypistry)
    )
    if {pith_root_name} is not __beartypistry:
'''.format(pith_root_name=PEP_CODE_PITH_ROOT_EXPR),

    # Snippet localizing any keyword-only parameter (e.g., "*, kwarg") by
    # lookup in the wrapper's variadic "**kwargs" dictionary. (See above.)
    Parameter.KEYWORD_ONLY: '''
    {pith_root_name} = kwargs.get({{arg_name!r}}, __beartypistry)
    if {pith_root_name} is not __beartypistry:
'''.format(pith_root_name=PEP_CODE_PITH_ROOT_EXPR),

    # Snippet iteratively localizing all variadic positional parameters.
    Parameter.VAR_POSITIONAL: '''
    for {pith_root_name} in args[{{arg_index!r}}:]:
'''.format(pith_root_name=PEP_CODE_PITH_ROOT_EXPR),
}
'''
Dictionary mapping from the type of each callable parameter supported by the
:func:`beartype.beartype` decorator to a PEP-compliant code snippet localizing
that callable's next parameter to be type-checked.
'''

# ....................{ CODE ~ return                     }....................
PEP_CODE_GET_RETURN = '''
    {pith_root_name} = __beartype_func(*args, **kwargs)
    (
'''.format(pith_root_name=PEP_CODE_PITH_ROOT_EXPR)
'''
PEP-compliant code snippet calling the decorated callable and localizing the
value returned by that call.

Note that this snippet intentionally terminates on a line containing only the
``(`` character, enabling subsequent type-checking code to effectively ignore
indentation level and thus uniformly operate on both:

* Parameters localized via values of the :data:`PARAM_KIND_TO_PEP_CODE_GET`
  dictionary.
* Return values localized via this sippet.
'''


PEP_CODE_RETURN_CHECKED = '''
    )
    return {pith_root_name}
'''.format(pith_root_name=PEP_CODE_PITH_ROOT_EXPR)
'''
PEP-compliant code snippet returning from the wrapper function the successfully
type-checked value returned from the decorated callable.

Note that this snippet intentionally terminates on a line containing only the
``)`` character, which closes the corresponding character terminating the
:data:`PEP_CODE_GET_RETURN` snippet.
'''

# ....................{ CODE ~ check                      }....................
#FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
#which are the optimal means of performing string formatting.
PEP_CODE_CHECK_NONPEP_TYPE = '''
{{indent_curr}}if not isinstance({{pith_curr_expr}}, {{hint_curr_expr}}):
{{indent_curr}}    raise __beartype_raise_pep_call_exception(
{{indent_curr}}        func=__beartype_func,
{{indent_curr}}        param_or_return_name={pith_root_name},
{{indent_curr}}        param_or_return_value={pith_root_expr},
{{indent_curr}})
'''.format(
    pith_root_name=PEP_CODE_PITH_ROOT_NAME_PLACEHOLDER,
    pith_root_expr=PEP_CODE_PITH_ROOT_EXPR,
)
'''
PEP-compliant code snippet type-checking a simple non-:mod:`typing` type (e.g.,
:class:`dict`, :class:`list`).
'''