__all__ = ["execute_csc"]

import asyncio

from . import ATHexapodCSC


def execute_csc():
    asyncio.run(ATHexapodCSC.amain(index=None))
