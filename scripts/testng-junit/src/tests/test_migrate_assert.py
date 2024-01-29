from setup import testng2junit5


def test_migrate_assert_reverse_arguments():
    content = """
            GffValidation gffValidation = result.getGffValidation();
            assertNotNull(gffValidation, "gffValidation");
            List<GffAccountValidation> accountValidations = gffValidation.getAccounts().getItem();
    """
    content_new = testng2junit5.migrate_asserts(content)
    assert 'assertNotNull("gffValidation", gffValidation);' in content_new


def test_migrate_assert_doesnt_span_logical_lines():
    original = """
assertNotNull("a");
assertEquals("b", "c");
"""
    assert testng2junit5.migrate_asserts(original) == original
