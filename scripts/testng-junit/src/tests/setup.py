import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import testng2junit5
import junit4_to_junit5


###
# Strip content for equality comparison.
###
def assert_equal_content(content, expected):
    assert ''.join(content.split()) == ''.join(expected.split())

