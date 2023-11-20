from setup import testng2junit4

content = """

        GffValidation gffValidation = result.getGffValidation();
        assertNotNull(gffValidation, "gffValidation");
        List<GffAccountValidation> accountValidations = gffValidation.getAccounts().getItem();

"""


def test_migrate_assert():
    content_new = testng2junit4.migrate_asserts(content)
    assert 'assertNotNull("gffValidation", gffValidation);' in content_new
