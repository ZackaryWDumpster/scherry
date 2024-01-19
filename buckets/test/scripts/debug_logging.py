import logging
import sys

debugLv = globals().get("debugLv", logging.DEBUG)

logging.basicConfig(level=debugLv, stream=sys.stdout)