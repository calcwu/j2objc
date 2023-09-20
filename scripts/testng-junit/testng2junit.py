#!/usr/bin/python3
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Migrates all java files in a directory from TestNG to JUnit.

Used by J2ObjC to translate Android's libcore new TestNG unit tests.

Usage:
    testng2junit.py <directory_to_migrate>
"""

import os
import sys
import re


def migrate_imports(content):
  """Updates import statements from TestNG to JUnit."""
  content_new = re.sub('org.testng.annotations.Test', 'org.junit.Test', content)

  #Before
  content_new = re.sub('org.testng.annotations.BeforeMethod',
                       'org.junit.Before', content_new)

  content_new = re.sub('org.testng.annotations.BeforeClass',
                       'org.junit.Before', content_new)

  content_new = re.sub('org.testng.annotations.BeforeTest',
                       'org.junit.Before', content_new)

  #After
  content_new = re.sub('org.testng.annotations.AfterMethod',
                       'org.junit.After', content_new)

  content_new = re.sub('org.testng.annotations.AfterClass',
                       'org.junit.After', content_new)

  content_new = re.sub('org.testng.annotations.AfterTest',
                       'org.junit.After', content_new)

  content_new = re.sub(
      'import org.testng.annotations.DataProvider;',
      '''import com.tngtech.java.junit.dataprovider.DataProvider;
import com.tngtech.java.junit.dataprovider.DataProviderRunner;
import com.tngtech.java.junit.dataprovider.UseDataProvider;
import org.junit.runner.RunWith;''', content_new)

  content_new = re.sub('org.testng.AssertJUnit',
                       'org.junit.Assert', content_new)

  content_new = re.sub('org.testng.Assert',
                       'org.junit.Assert', content_new)

  # this forces @Guice annotation error, but it's needed for Guice.createInjector
  content_new = re.sub('import org.testng.annotations.Guice;',
                       '''import com.google.inject.Guice;
import com.google.inject.Injector;''', content_new)

  # include @Ignore
  if '@Test(enabled' in content_new:
      content_new = re.sub('org.junit.Test;',
                           '''org.junit.Test;
import org.junit.Ignore;''', content_new)

  return content_new


def migrate_testng_annotations(content):
  content_new = re.sub('@Test\npublic class', 'public class', content)
  content_new = re.sub('@Guice\npublic class', 'public class', content_new)
  content_new = re.sub('@Guice\npublic abstract class', 'public abstract class', content_new)

  # Use @Before/@After over @BeforeClass/@AfterClass since the latter requires the method to be static.
  # Most of our methods are more member friendly.
  content_new = re.sub('@BeforeMethod', '@Before', content_new)
  content_new = re.sub('@BeforeClass', '@Before', content_new)
  content_new = re.sub('@BeforeTest', '@Before', content_new)

  content_new = re.sub('@AfterMethod', '@After', content_new)
  content_new = re.sub('@AfterClass', '@After', content_new)
  content_new = re.sub('@AfterTest', '@After', content_new)

  # migrate NullChecking*TestBase
  content_new = re.sub('NullCheckingClassTestBase', 'NullCheckingClassJunitTestBase', content_new)
  content_new = re.sub('NullCheckingEnumTestBase', 'NullCheckingEnumJunitTestBase', content_new)
  content_new = re.sub('NullCheckingInstanceTestBase', 'NullCheckingInstanceJunitTestBase', content_new)
  content_new = re.sub('NullCheckingBuilderTestBase', 'NullCheckingBuilderJunitTestBase', content_new)

  # Migrate AbstractJerseyTestNG to AbstractJerseyJUnit
  content_new = re.sub('AbstractJerseyTestNG', 'AbstractJerseyJUnit', content_new)

  # Ensure test methods are public
  content_new = re.sub('@Test\n  void', '@Test\n  public void', content_new)
  content_new = re.sub('@Test\n  private', '@Test\n  public', content_new)
  content_new = re.sub('@After\n  private', '@After\n  public', content_new)
  content_new = re.sub('@Before\n  private', '@Before\n  public', content_new)
  content_new = re.sub(r'@Test\(enabled = false\)', '@Ignore @Test', content_new)

  # clean up junit4 warnings that junit4 tests should not start with void test*.
  content_new = re.sub('public void test', 'public void verify', content_new)

  return content_new


def migrate_data_providers(content):
  """TestNG allows a DataProvider to be renamed."""
  # Make a list of tuples mapping the
  # new name to original name.
  # @DataProvider(name="MillisInstantNoNanos")
  # Object[][] provider_factory_millis_long() {
  data_provider_regex = re.compile(
      r'@DataProvider\(name\s?=\s?(".*")\)\s*.*\[\]\[\] (.*)\(\)')
  data_provider_rename_tuples = re.findall(data_provider_regex, content)

  # Remove the renamed data provider from test annotation and put it in.
  # @UseDataProvider annotation
  # @Test(dataProvider="MillisInstantNoNanos")
  data_provider_test_regex = re.compile(
      r'@Test\(dataProvider\s*=\s*(".*"),?\s?(.*)?\)')
  content_new = data_provider_test_regex.sub(
      '@Test(\\2)\n  @UseDataProvider(\\1)', content)

  # clean up @Test() to @Test
  content_new = re.sub('@Test\(\)', '@Test', content_new)

  for tup in data_provider_rename_tuples:
    content_new = re.sub(tup[0], '"' + tup[1] + '"', content_new)

  content_new = re.sub('@DataProvider.*', '@DataProvider', content_new)

  #content_new = re.sub('public final class', 'public class', content_new)

  if 'DataProvider' in content_new and '@RunWith(DataProviderRunner.class)' not in content_new:
    content_new = re.sub('public class',
                         '@RunWith(DataProviderRunner.class)\npublic class',
                         content_new)

  # In JUnit data providers have to be public and static.
  object_array_provider_regex = re.compile(r'(public|private) Object\[\]\[\] (.*)\(\)')
  content_new = object_array_provider_regex.sub(
      'public static Object[][] \\2()', content_new)

  return content_new


def migrate_exceptions(content):
  content_new = re.sub('expectedExceptions', 'expected', content)

  exception_patt = re.compile(r'expected\s?=\s?{(.*)}')
  content_new = exception_patt.sub('expected=\\1', content_new)

  return content_new


def migrate_asserts(content):
  """Converts TestNG assertions to JUnit."""
  # TestNG has an overload for assertEquals that takes parameters:
  # obj1, obj2, message. JUnit also has this overload but takes parameters:
  # message, obj1, obj2.
  assert_equals_overload_regex = re.compile(
      r'assertEquals\((.*), (.*), (("|String).*)\);')
  content_new = assert_equals_overload_regex.sub('assertEquals(\\3, \\1, \\2);',
                                                 content)

  multiline_assert_equals_overload_regex = re.compile(
      r'assertEquals\((.*), (.*),\s*(".*\s*\+.*)\);')
  content_new = multiline_assert_equals_overload_regex.sub(
      'assertEquals(\\3, \\1, \\2);', content_new)

  multiline_assert_equals_overload_regex = re.compile(
      r'assertEquals\((.*), (.*),\s*(".*\s*\+ String.*\s*.*)\);')
  content_new = multiline_assert_equals_overload_regex.sub(
      'assertEquals(\\3, \\1, \\2);', content_new)

  # TestNG has overloads for assert(True|False|NotNull|Same) taking two
  # parameters: condition, message. JUnit also has these overloads but takes
  # parameters: message, condition.
  # assert_conditional_regex = re.compile(
  #     r'assert(True|False|NotNull|Same)\((.*), (.*)\);')
  # content_new = assert_conditional_regex.sub('assert\\1(\\3, \\2);',
  #                                            content_new)

  return content_new

"""
This replaces the following pattern

@Guice(modules = SomeModule.class)
public class SomeTest {

  @Before
  public void someTest() {
  
  }
}

..... with .....

public class SomeTest {

  private final Injector injector = Guice.createInjector(new SomeModule());

  @Before
  public void someTest() {
    injector.injectMembers(this);  
  }
}
"""
def migrate_guice_annotation(content):
    if '@Guice' not in content:
        return content

    injector_line = replace_guice_module_with_injector(content)
    print('Guice injector: ', injector_line)

    # rewrite the content for simplicity instead of regexp
    new_content = []
    content_iter = iter(content.split('\n'))
    for line in content_iter:
        # remove all the lines starting with @Guice(....)
        if '@Guice' in line:
            while ')' not in line:
                # skip the next line too since this might span across multiple lines
                next(content_iter)
            continue

        # handle insertion of injector
        if 'public class' in line:
            new_content.append(line)

            if '{' in line:
                new_content.append(injector_line)
            else:
                #inject injector after public class SomeClass {
                insert_line_after_method(new_content, content_iter, injector_line)

            continue

        # handle insertion of injectMember
        #  @Before
        #   public void beforeMethod() {
        #   ....insert here....
        if '@Before' in line:
            new_content.append(line)
            # this should be the line of the method and keep adding the line until we get {
            # insert injectMember as the first line below the below method.
            insert_line_after_method(new_content, content_iter, '    injector.injectMembers(this);')
            continue

        new_content.append(line)

    return '\n'.join(new_content)


"""
This replaces the following pattern

private final SomeServiceA serviceA;

private final SomeServiceB serviceB;

@Inject
public SomeClass(SomeServiceA serviceA, SomeServiceB serviceB) {
    this.serviceA = serviceA;
    this.serviceB = serviceB;
}

..... with .....

@Inject
private SomeServiceA serviceA;

@Inject
private SomeServiceB serviceB;
"""
def migrate_inject_constructor(class_name, content):
    if '@Inject' not in content or '@Test' not in content:
        return content

    # extract constructor arguments
    injected_arguments = extract_constructor_arguments(class_name, content)

    if injected_arguments:
        content_iter = iter(content.split('\n'))
        content_new = []
        parsing = True
        for line in content_iter:
            if parsing:
                for argument in injected_arguments:
                    if argument + ';' in line:
                        content_new.append('  @Inject')
                        line = re.sub('final ', '', line)

                # remove constructor
                if '@Inject' in line:
                    line = next(content_iter)
                    # match any constructor variation
                    match_constructor = re.search(r'\b(public\s+)?' + class_name + '\s*\(', line)
                    if match_constructor:
                        # next skipping while there is a }
                        while '}' not in line:
                            line = next(content_iter)

                        parsing = False
                        continue

            content_new.append(line)

        return '\n'.join(content_new)
    return content

def extract_constructor_arguments(class_name, content):
    content_iter = iter(content.split('\n'))
    lines = []
    for line in content_iter:
        if class_name + '(' in line:
            lines.append(line)
            while ')' not in line:
                line = next(content_iter)
                lines.append(line)

        if lines:
            break

    # combine everything to oneline
    arguments = []
    match = re.search('\((.*?)\)', ''.join(lines))
    if match:
        arguments = [a.strip() for a in match.group(1).strip().split(',')]
        print('injected arguments: ', arguments)

    return arguments

def replace_guice_module_with_injector(content):
    if '@Guice' not in content:
        raise Exception("@Guice is expected")

    modules_regex = re.compile(
        r'@Guice\(modules\s*=\s*\{?([^}\n]+)\}?\)')
    module_matches = re.findall(modules_regex, content)
    print("module_matches: ", module_matches)

    if not module_matches:
        raise Exception("Cannot extract @Guice modules. Double check the regexp.")

    module_line = module_matches[0].split(',')
    modules = []
    for m in module_line:
        new_module = re.sub(r'^', 'new ', m.strip())
        new_module = re.sub('\.class', '()', new_module)
        modules.append(new_module)

    return '\n  private final Injector injector = Guice.createInjector({});'\
        .format(", ".join(["{}"] * len(modules)).format(*modules))


def insert_line_after_method(contents, content_iter, new_line):
    method_line = next(content_iter)
    while '{' not in method_line:
        contents.append(method_line)
        method_line = next(content_iter)

    contents.append(method_line)
    contents.append(new_line)


def migrate_buck(buck_module):
    buck_file = buck_module + "/BUCK"
    if os.path.isfile(buck_file):
        with open(buck_file, 'r') as f_in:
            content = f_in.read()
            if 'java_test_internal' in content and 'junit' not in content:
                print('Converting ', buck_file)
                content = re.sub(r'java_test_internal\(',
                                 'java_test_internal(\n\ttest_type = "junit",', content)
                with open(buck_file, 'w') as fn:
                    fn.write(content)


def migrate_tests(test_dir):
    test_files = []
    for path, dir, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.java'):
                test_files.append(os.path.join(path, file))

    for file_name in test_files:
        with open(file_name, 'r') as f:
            print("Converting ", file_name)
            content = f.read()
            content_new = migrate_imports(content)
            content_new = migrate_testng_annotations(content_new)
            content_new = migrate_data_providers(content_new)
            content_new = migrate_guice_annotation(content_new)
            content_new = migrate_inject_constructor(extrac_class_name(file_name), content_new)
            content_new = migrate_exceptions(content_new)
            content_new = migrate_asserts(content_new)
            with open(file_name, 'w') as fn:
                fn.write(content_new)


def extrac_class_name(file):
    b = file.rfind('/')
    e = file.rfind('.java')
    return file[b+1:e]


def main():
  if len(sys.argv) == 1:
    print('usage: testng2junit.py <directory_to_migrate>')
    sys.exit(1)

  buck_module = sys.argv[1]
  test_dir = buck_module
  if 'src/test' not in buck_module:
      test_dir = buck_module + '/src/test'
      migrate_buck(buck_module)

  migrate_tests(test_dir)

if __name__ == '__main__':
  sys.exit(main())
