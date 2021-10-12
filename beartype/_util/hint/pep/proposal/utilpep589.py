#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`589`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_3_8

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
#FIXME: Call this tester directly *ONLY* from the get_hint_pep_sign_or_none()
#getter. All other areas of the code should efficiently test signs against
#"HintSignTypedDict" instead.

# The implementation of the "typing.TypedDict" attribute substantially varies
# across Python interpreter *AND* "typing" implementation. Specifically:
# * The "typing.TypedDict" attribute under Python >= 3.9 is *NOT* actually a
#   superclass but instead a factory function masquerading as a superclass by
#   setting the subversive "__mro_entries__" dunder attribute to a tuple
#   containing a private "typing._TypedDict" superclass. This superclass
#   necessarily defines the three requisite dunder attributes.
# * The "typing_extensions.TypedDict" attribute under Python < 3.8 is actually
#   a superclass also necessarily defining the three requisite dunder
#   attributes.
# * The "typing.TypedDict" attribute under *ONLY* Python 3.8 is also actually
#   a superclass that *ONLY* defines the requisite "__annotations__" dunder
#   attribute. The two remaining dunder attributes are only conditionally
#   defined and thus *CANNOT* be unconditionally assumed to exist.
# In all three cases, passing the passed hint and that superclass to the
# issubclass() builtin fails, as the metaclass of that superclass prohibits
# issubclass() checks. I am throwing up in my mouth as I write this.
#
# Unfortunately, all of the above complications are further complicated by the
# "dict" type under Python >= 3.10. For unknown reasons, Python >= 3.10 adds
# spurious "__annotations__" dunder attributes to "dict" subclasses -- even if
# those subclasses annotate *NO* class or instance variables. While a likely
# bug, we have little choice but to at least temporarily support this insanity.
def is_hint_pep589(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a :pep:`589`-compliant **typed
    dictionary** (i.e., :class:`typing.TypedDict` subclass).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Although the implementation
    inefficiently performs three calls to the :func:`hasattr` builtin (which
    inefficiently calls the :func:`getattr` builtin and catches the
    :exc:`AttributeError` exception to detect false cases), callers are
    expected to instead (in order):

    #. Call the memoized
       :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign_or_none`
       getter, which internally calls this unmemoized tester.
    #. Compare the object returned by that getter against the
       :attr:`from beartype._util.data.hint.pep.sign.datapepsigns.HintSignTypedDict`
       sign.

    Parameters
    ----------
    hint : object
        Object to be tested.

    Returns
    ----------
    bool
        ``True`` only if this object is a typed dictionary.
    '''

    # If this hint is neither...
    if not (
        # A class *NOR*...
        isinstance(hint, type) and
        # A "dict" subclass...
        issubclass(hint, dict)
    # Then this hint *CANNOT* be a typed dictionary. By definition, each typed
        # dictionary is necessarily a "dict" subclass.
    ):
        return False
    # Else, this hint is a "dict" subclass and thus might be a typed
    # dictionary.

    # Technically, this test can also be performed by inefficiently violating
    # privacy encapsulation. Specifically, this test could perform an O(k) walk
    # up the class inheritance tree of the passed class (for k the number of
    # superclasses of that class), iteratively comparing each such superclass
    # for against the "typing.TypeDict" superclass. That is, this tester could
    # crazily reimplement the issubclass() builtin in pure-Python. Since the
    # implementation of typed dictionaries varies substantially across Python
    # versions, doing so would require version-specific tests in addition to
    # unsafely violating privacy encapsulation and inefficiently violating
    # constant-time guarantees.
    #
    # Technically, the current implementation of this test is susceptible to
    # false positives in unlikely edge cases. Specifically, this test queries
    # for dunder attributes and thus erroneously returns true for user-defined
    # "dict" subclasses *NOT* subclassing the "typing.TypedDict" superclass but
    # nonetheless declaring the same dunder attributes declared by that
    # superclass. Since the likelihood of any user-defined "dict" subclass
    # accidentally defining these attributes is vanishingly small *AND* since
    # "typing.TypedDict" usage is largely discouraged in the typing community,
    # this error is unlikely to meaningfully arise in real-world use cases.
    # Ergo, it is preferable to implement this test portably, safely, and
    # efficiently rather than accommodate this error.
    #
    # In short, the current approach of is strongly preferable.

    # Return true *ONLY* if this "dict" subclass defines all three dunder
    # attributes guaranteed to be defined by all typed dictionaries. Although
    # slow, this is still faster than the MRO-based approach delineated above.
    #
    # Note that *ONLY* the Python 3.8-specific implementation of
    # "typing.TypedDict" fails to unconditionally define the
    # "__required_keys__" and "__optional_keys__" dunder attributes. Ergo, if
    # the active Python interpreter targets exactly Python 3.8, we relax this
    # test to *ONLY* test for the "__annotations__" dunder attribute.
    # Specifically, we return true only if...
    return (
        # This "dict" subclass defines this "TypedDict" attribute *AND*...
        hasattr(hint, '__annotations__') and
        # Either...
        (
            # The active Python interpreter targets exactly Python 3.8 and
            # thus fails to unconditionally define the remaining attributes
            # *OR*...
            IS_PYTHON_3_8 or
            # The active Python interpreter targets any other Python version
            # and thus unconditionally defines the remaining attributes.
            (
                hasattr(hint, '__required_keys__') and
                hasattr(hint, '__optional_keys__')
            )
        )
    )
