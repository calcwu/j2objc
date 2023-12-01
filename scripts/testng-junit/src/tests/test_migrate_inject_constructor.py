from setup import testng2junit5
from setup import assert_equal_content

content = """

  private final SomeServiceA serviceA;

  private final SomeServiceB serviceB;

  @Inject
  public SomeClass(SomeServiceA serviceA, SomeServiceB serviceB) {
    this.serviceA = serviceA;
    this.serviceB = serviceB;
  }

  @Test
  public void runSomeTest() {

  }

"""

expected = """

  @Inject
  private SomeServiceA serviceA;

  @Inject
  private SomeServiceB serviceB;

  @Test
  public void runSomeTest() {

  }

"""


def test_migrate_inject_constructor():
    content_new = testng2junit5.migrate_inject_constructor('SomeClass', content)
    assert_equal_content(content_new, expected)
