from setup import testng2junit5

def test_public_before_class_ensure_static():
    original = """
@BeforeClass
public void alpha() {
    beta();
}
"""
    migrated = testng2junit5.migrate_testng_annotations(original)
    expected = """
@BeforeAll
public static void alpha() {
    beta();
}
"""
    assert migrated == expected

def test_before_class_avoid_double_static():
    original = """
@BeforeClass
public static void alpha() {
    beta();
}
"""
    migrated = testng2junit5.migrate_testng_annotations(original)
    expected = """
@BeforeAll
public static void alpha() {
    beta();
}
"""
    assert migrated == expected