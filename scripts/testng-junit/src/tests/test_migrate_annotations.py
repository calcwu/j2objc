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

def test_after_each_always_run():
    original = """
@AfterMethod(alwaysRun = true)
"""
    expected = """
@AfterEach
"""
    actual = testng2junit5.migrate_testng_annotations(original)
    assert expected == actual


def test_after_each_always_run_no_whitespace():
    original = """
@AfterMethod(alwaysRun=true)
"""
    expected = """
@AfterEach
"""
    actual = testng2junit5.migrate_testng_annotations(original)
    assert expected == actual
