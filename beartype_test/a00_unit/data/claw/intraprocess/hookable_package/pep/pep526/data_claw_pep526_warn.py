#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype import hookable** :pep:`526` **warning submodule**
(i.e., data module containing *only* :pep:`526`-compliant annotated variable
assignments emitting :exc:`UserWarning` violations, mimicking real-world usage
of the :func:`beartype.claw.beartype_package` import hook from an external
caller).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    List,
    Union,
)
from pytest import warns

# from beartype.claw._clawstate import claw_state
# print(f'this_submodule conf: {repr(claw_state.module_name_to_beartype_conf)}')

# ....................{ PEP 526                            }....................
# Validate that the import hook presumably installed by the caller implicitly
# appends all PEP 526-compliant annotated assignment statements in this
# submodule with calls to beartype's statement-level
# beartype.door.die_if_unbearable() warning-emitter.

# Assert that a PEP 526-compliant annotated assignment statement assigning an
# object satisfying the type hint annotating that statement emits *NO* warning.
as_oceans_moon: int = len("As ocean's moon looks on the moon in heaven.")

# Assert that a PEP 526-compliant annotated statement lacking an assignment
# emits *NO* warning.
looks_on_the_moon: str

# Assert that a PEP 526-compliant annotated assignment statement assigning an
# object violating the type hint annotating that statement emits the expected
# warning.
with warns(UserWarning):
    in_heaven: Union[float, List[str]] = len(
        'The spirit of sweet human love has sent')