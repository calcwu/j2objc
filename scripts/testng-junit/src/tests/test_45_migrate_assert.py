from setup import junit4_to_junit5
from setup import assert_equal_content


content = """
    assertNotNull("gffValidation", gffValidation);
    List<GffAccountValidation> accountValidations = gffValidation.getAccounts().getItem();
    assertNotNull("accountValidations", accountValidations);
    GffAccountValidation gffAccountValidation = gffValidation.getAccounts().getItem().get(0);
    assertNotNull("gff", gff);
    assertNotNull("emptyGff", emptyGff);
    assertTrue("Empty test", true);
"""

expected = """    
    assertNotNull(gffValidation, "gffValidation");
    List<GffAccountValidation> accountValidations = gffValidation.getAccounts().getItem();
    assertNotNull(accountValidations, "accountValidations");
    GffAccountValidation gffAccountValidation = gffValidation.getAccounts().getItem().get(0);
    assertNotNull(gff, "gff");
    assertNotNull(emptyGff, "emptyGff");    
    assertTrue(true, "Empty test");
"""


def test_migrate_assert():
    content_new = junit4_to_junit5.migrate_asserts(content)
    print(content_new)
    assert_equal_content(content_new, expected)
