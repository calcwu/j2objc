from setup import testng2junit
from setup import assert_equal_content


content_1 = """

    @Guice(modules = SomeModule.class)
    public class SomeTest {
    
      @Before
      public void someTest() {
    
      }
    }

"""

expected_1 = """

    public class SomeTest {
    
      private final Injector injector = Guice.createInjector(new SomeModule());
    
      @Before
      public void someTest() {
        injector.injectMembers(this);
      }
    }
"""

content_2 = """

    @Guice
    public class SomeTest {

      @Before
      public void someTest() {

      }
    }

"""

expected_2 = """

    public class SomeTest {

      private final Injector injector = Guice.createInjector();

      @Before
      public void someTest() {
        injector.injectMembers(this);
      }
    }
"""

content_3 = """

    @Guice(modules = {TestModuleA.class,
        Test.ModuleB.class})
    public class SomeTest {

      @Before
      public void someTest() {

      }
    }

"""

expected_3 = """

    public class SomeTest {

      private final Injector injector = Guice.createInjector(new TestModuleA(), new Test.ModuleB());

      @Before
      public void someTest() {
        injector.injectMembers(this);
      }
    }
"""


def test_migrate_guice_annotation():
    assert_equal_content(testng2junit.migrate_guice_annotation(content_1), expected_1)
    assert_equal_content(testng2junit.migrate_guice_annotation(content_2), expected_2)
    assert_equal_content(testng2junit.migrate_guice_annotation(content_3), expected_3)
