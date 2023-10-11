from setup import testng2junit
from setup import assert_equal_content


content = """

    @Guice(modules = SomeModule.class)
    public class SomeTest {
    
      @Before
      public void someTest() {
    
      }
    }

"""

expected = """

    public class SomeTest {
    
      private final Injector injector = Guice.createInjector(new SomeModule());
    
      @Before
      public void someTest() {
        injector.injectMembers(this);
      }
    }
"""


def test_migrate_guice_annotation():
    content_new = testng2junit.migrate_guice_annotation(content)
    assert_equal_content(content_new, expected)
