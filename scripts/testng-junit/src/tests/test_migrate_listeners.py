from setup import testng2junit5
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
@ExtendWith(TestRequestScopeListener.class)
public class SomeTest {
}

@ExtendWith({TestRequestScopeListener.class})
public class SomeTest
{
}
'''
def test_migrate_listeners():
    content_new = testng2junit5.migrate_listeners(content)
    assert_equal_content(content_new, expected)
