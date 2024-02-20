from setup import testng2junit5
from setup import assert_equal_content

content = """
  @DataProvider(name = BAD_CHAR_NAMES)
  public Object[][] provideBadCharNames() {
    return new Object[][]{
        {""},
        {"hello!world"}
    };
  }

  @Test(dataProvider = BAD_CHAR_NAMES, expectedExceptions = IllegalArgumentException.class)
  public void testReserved(String name) {
    JsonApiNaming.checkName(name);
  }

  @Test(dataProvider = "args")
  public void testIsDoubleZero(double val, boolean expected, boolean ignore1, boolean ignore2) {
    assertThat("expected isDoubleZero() for + " + val + " to be " + expected,
        EqualityUtils.isDoubleZero(val), is(expected));
  }

  @DataProvider(name = "args")
  public Object[][] getArgs() {
    return new Object[][] {
        {0d, true, true, true},
        {1E-2, false, false, false}
    };
  }

  @DataProvider(name = "adiaHosts")
  Object[][] providesAdiaHosts() throws URISyntaxException {
    return new Object[][] {
        {new URI("https://adia1.prod.addepar.com")},
        {new URI("https://adia1:4447")}
    };
  }

  @Test(dataProvider = "adiaHosts")
  public void parsesUrlPrefixFromValidAdiaHost(URI adiaHost) {
    assertThat(AdiaReverseProxyServletModule.getUrlPrefix(adiaHost), is("/proxy-adia1"));
  }
"""

expected = """
  public static Object[][] provideBadCharNames() {
    return new Object[][]{
        {""},
        {"hello!world"}
    };
  }

  @ParameterizedTest(expectedExceptions = IllegalArgumentException.class)
  @MethodSource("provideBadCharNames")
  public void testReserved(String name) {
    JsonApiNaming.checkName(name);
  }

  @ParameterizedTest
  @MethodSource("getArgs")
  public void testIsDoubleZero(double val, boolean expected, boolean ignore1, boolean ignore2) {
    assertThat("expected isDoubleZero() for + " + val + " to be " + expected,
        EqualityUtils.isDoubleZero(val), is(expected));
  }

  public static Object[][] getArgs() {
    return new Object[][] {
        {0d, true, true, true},
        {1E-2, false, false, false}
    };
  }

  static Object[][] providesAdiaHosts() throws URISyntaxException {
    return new Object[][] {
        {new URI("https://adia1.prod.addepar.com")},
        {new URI("https://adia1:4447")}
    };
  }

  @ParameterizedTest
  @MethodSource("providesAdiaHosts")
  public void parsesUrlPrefixFromValidAdiaHost(URI adiaHost) {
    assertThat(AdiaReverseProxyServletModule.getUrlPrefix(adiaHost), is("/proxy-adia1"));
  }
"""


def test_migrate_data_providers():
    content_new = testng2junit5.migrate_data_providers(content)
    assert_equal_content(content_new, expected)


