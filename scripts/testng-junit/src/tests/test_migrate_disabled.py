from setup import testng2junit5

def test_migrate_enabled_false_no_whitespace():
    original = """
@Test(enabled=false)
"""
    expected = """
@Disabled @Test
"""
    actual = testng2junit5.migrate_testng_annotations(original)
    assert expected == actual

def test_migrate_enabled_false_whitespace():
    original = """
@Test(enabled = false)
"""
    expected = """
@Disabled @Test
"""
    actual = testng2junit5.migrate_testng_annotations(original)
    assert expected == actual
