from setup import testng2junit
from setup import assert_equal_content

content = '''
@Guice
@Listeners(TestRequestScopes.Listener.class)
public class SomeTest {
}

@Listeners({TestRequestScopes.Listener.class})
public class SomeTest
{
}
'''

expected = '''
@Guice
public class SomeTest {

  @Rule
  public TestRule rule = TestRequestScopes.rule();
}

public class SomeTest
{

  @Rule
  public TestRule rule = TestRequestScopes.rule();
}
'''
def test_migrate_listeners():
    content_new = testng2junit.migrate_listeners(content)
    assert_equal_content(content_new, expected)