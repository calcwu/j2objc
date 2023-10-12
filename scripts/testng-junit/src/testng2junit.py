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

throw_template = '''    assertThrows(
      () -> {
%s
      },
      %s,
      %s
    );'''


throw_with_callable_template = '''    assertCallableThrows(
      () -> {
%s
        return null;
      },
      %s,
      %s
    );'''


before_inject_template = '''  @Before
  public void setup() {
    injector.injectMembers(this);     
  }
'''


def migrate_imports(content):
  """Updates import statements from TestNG to JUnit."""
  content_new = re.sub('org.testng.annotations.Test', 'org.junit.Test', content)

  #Before
  content_new = re.sub('org.testng.annotations.BeforeSuite',
                       'org.junit.Before', content_new)

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

  content_new = re.sub('org.testng.Assert.assertThrows',
                       'com.addepar.infra.library.lang.assertion.AssertionUtils.assertThrows', content_new)

  # this forces @Guice annotation error, but it's needed for Guice.createInjector
  content_new = re.sub('import org.testng.annotations.Guice;',
                       '''import com.google.inject.Guice;
import com.google.inject.Injector;''', content_new)

  # include @Ignore
  imports = ['org.junit.Test;']
  if '@Test(enabled' in content_new:
      imports.append('import org.junit.Ignore;')

  if 'expectedExceptionsMessageRegExp' in content_new:
    imports.append('import static com.addepar.infra.library.lang.assertion.AssertionUtils.assertThrows;')
    imports.append('import static com.addepar.infra.library.lang.assertion.Assert.assertCallableThrows;')

  # if we have @Guice, we also need @Before imports to support before_inject_template.
  # refer to migrate_guice_annotation
  if '@Guice' in content_new and '@Before' not in content_new:
    imports.append('import org.junit.Before;')

  content_new = re.sub('org.junit.Test;', '\n'.join(imports), content_new)

  return content_new


def migrate_testng_annotations(content):
  content_new = re.sub('@Test\npublic class', 'public class', content)
  content_new = re.sub('@Guice\npublic class', 'public class', content_new)
  content_new = re.sub('@Guice\npublic abstract class', 'public abstract class', content_new)

  # Use @Before/@After over @BeforeClass/@AfterClass since the latter requires the method to be static.
  # Most of our methods are more member friendly.
  content_new = re.sub('@BeforeSuite', '@Before', content_new)
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
  if 'AbstractJerseyJUnit' in content_new:
      content_new = re.sub('\s+(this.)?resetMocks\(\);', '', content_new)

  # Ensure test methods are public
  content_new = re.sub('@Test\n  void', '@Test\n  public void', content_new)
  content_new = re.sub('@Test\n  private', '@Test\n  public', content_new)
  content_new = re.sub('@After\n  private', '@After\n  public', content_new)
  content_new = re.sub('@After\n  void', '@After\n  public void', content_new)
  content_new = re.sub('@Before\n  public static', '@Before\n  public', content_new)
  content_new = re.sub('@Before\n  private static', '@Before\n  public', content_new)
  content_new = re.sub('@Before\n  private', '@Before\n  public', content_new)
  content_new = re.sub('@Before\n  void', '@Before\n  public void', content_new)
  content_new = re.sub(r'@Test\(enabled = false\)', '@Ignore @Test', content_new)

  return content_new


def migrate_data_providers(content):
  """TestNG allows a DataProvider to be renamed."""
  # Make a list of tuples mapping the
  # new name to original name.
  # @DataProvider(name="MillisInstantNoNanos")
  # Object[][] provider_factory_millis_long() {
  if '@DataProvider' not in content:
      return content

  content_new = re.sub(r'private Object\[\]\[\]', 'public Object[][]', content)
  content_new = re.sub(r'\)\n  Object\[\]\[\]', ')\n  public Object[][]', content_new)
  data_provider_regex = re.compile(
      r'@DataProvider\(name\s*=\s*(.*)\)\s*public\s+Object\[\]\[\]\s+(\w+)\(\)')
  data_provider_rename_tuples = re.findall(data_provider_regex, content_new)

  # Remove the renamed data provider from test annotation and put it in.
  # @UseDataProvider annotation
  # @Test(dataProvider="MillisInstantNoNanos")

  #  r'@Test\(dataProvider\s*=\s*(.*)\s*,\s*(.*)\)'
  content_new = re.sub(r'@Test\(dataProvider\s*=\s*(.*?)\s*(?:,\s*(.*))?\)', '@Test(\\2)\n  @UseDataProvider(\\1)', content_new)

  # clean up @Test() to @Test
  content_new = re.sub(r'@Test\(\)', '@Test', content_new)

  print('data_provider_rename_tuples: ', data_provider_rename_tuples)
  for tup in data_provider_rename_tuples:
   content_new = re.sub(r"@UseDataProvider\({}\)".format(tup[0]), "@UseDataProvider(\"{}\")".format(tup[1]), content_new)

  content_new = re.sub('@DataProvider.*', '@DataProvider', content_new)

  if 'DataProvider' in content_new and '@RunWith(DataProviderRunner.class)' not in content_new:
    content_new = re.sub('public class',
                         '@RunWith(DataProviderRunner.class)\npublic class',
                         content_new)
    content_new = re.sub('public final class',
                         '@RunWith(DataProviderRunner.class)\npublic final class',
                         content_new)

  # In JUnit data providers have to be public and static.
  content_new = re.sub(r'(public|private) Object\[\]\[\] (.*)\(\)', 'public static Object[][] \\2()', content_new)

  return content_new


###
# Replace
# @Test(expectedExceptions = IllegalArgumentException.class)
#
# with
# @Test(expected = IllegalArgumentException.class)
#
# OR
# @Test(expected = IllegalArgumentException.class,
#     expectedExceptionsMessageRegExp = "some message")
#
# with
# assertThrows(
#         () -> {
#           Config config = ConfigFactory.load().getConfig("test8." + BatuNotificationFilterTest.class.getPackageName());
#           new BatuNotificationFilter(config);
#         },
#         IllegalArgumentException.class,
#         "notification_filter.mode must be either 'include' or 'exclude'"
# );
#
def migrate_exceptions(content):
  content_new = content
  if 'expectedExceptions' in content:
    content_new = re.sub('expectedExceptions', 'expected', content)

  if 'expectedExceptionsMessageRegExp' not in content:
      return content_new

  pattern = r'@Test\s*\(expected\s*=\s*([^\)]+)\s*,\s*\n*expectedMessageRegExp\s*=\s*(.*?)\s*\)'
  new_content = []
  content_iter = iter(content_new.split('\n'))
  for line in content_iter:
    at_test_annotation_line = ''
    method_body = []
    method_signature = ''
    if '@Test' in line and 'expected' in line\
            and ('expectedMessageRegExp' in line or ')' not in line):
        at_test_annotation_line = line
        while ')' not in line:
            line = next(content_iter)
            at_test_annotation_line += line

        new_content.append('  @Test')
        # method line
        while '{' not in line:
            line = next(content_iter)
            new_content.append(line)
            method_signature += line

        if '{' in line:
            # parse out method lines
            line = next(content_iter)
            while not line.startswith('  }'):
                # 4 spaces.
                method_body.append('    '+line)
                line = next(content_iter)

        matches = re.search(pattern, at_test_annotation_line)
        print('expected exception + message matches:', matches)
        if matches:
          expected_exceptions = matches.group(1).strip()
          message_regex = matches.group(2).strip()
          # add the method boby replacement
          method_template = throw_with_callable_template if 'throws ' in method_signature else throw_template
          method_body_value = method_template % ('\n'.join(method_body), expected_exceptions, message_regex)
          new_content.append(method_body_value)


    new_content.append(line)

  return '\n'.join(new_content)


def migrate_asserts(content):
  """Converts TestNG assertions to JUnit."""
  # TestNG has an overload for assertEquals that takes parameters:
  # obj1, obj2, message. JUnit also has this overload but takes parameters:
  # message, obj1, obj2.

  #replace assertNotNull
  pattern = r'assertNotNull\(([^,]+),\s*"([^"]+)"\);'

  # Use re.sub() to replace the pattern with the desired format
  content_new = re.sub(pattern, r'assertNotNull("\2", \1);', content)

  content_new = re.sub('org.testng.Assert',
                       'org.junit.Assert', content_new)

  content_new = re.sub('org.junit.Assert.assertTrue',
      'com.addepar.infra.library.lang.assertion.Assert.assertTrue', content_new)

  content_new = re.sub('org.junit.Assert.assertEquals',
      'com.addepar.infra.library.lang.assertion.Assert.assertEquals', content_new)

  return content_new

#
# This replaces the following pattern
#
# @Guice(modules = SomeModule.class)
# public class SomeTest {
#
#   @Before
#   public void someTest() {
#
#   }
# }
#
# ..... with .....
#
# public class SomeTest {
#
#   private final Injector injector = Guice.createInjector(new SomeModule());
#
#   @Before
#   public void someTest() {
#     injector.injectMembers(this);
#   }
# }
#
def migrate_guice_annotation(content):
    if '@Guice' not in content:
        return content

    injector_line = replace_guice_module_with_injector(content)
    print('Guice injector: ', injector_line)

    # rewrite the content for simplicity instead of regexp
    new_content = []
    content_iter = iter(content.split('\n'))
    add_injected_member = False
    for line in content_iter:
        # remove all the lines starting with @Guice(....)
        if '@Guice' in line:
            while ')' not in line:
                # skip the next line too since this might span across multiple lines
                next(content_iter)
            continue

        # handle insertion of injector
        if 'public class' in line or 'public final class' in line:
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
            add_injected_member = True
            continue

        new_content.append(line)

    #check if there is any @Before in this test, if not add one.
    if not add_injected_member:
        # insert it before the first @Test
        insert_idx = 0
        for idx, line in enumerate(new_content):
            if '@After' in line or '@BeforeClass' in line or '@Test' in line:
                insert_idx = idx
                break

        if insert_idx:
            new_content.insert(insert_idx, before_inject_template)


    return '\n'.join(new_content)


#
# This replaces the following pattern
#
# private final SomeServiceA serviceA;
#
# private final SomeServiceB serviceB;
#
# @Inject
# public SomeClass(SomeServiceA serviceA, SomeServiceB serviceB) {
#     this.serviceA = serviceA;
#     this.serviceB = serviceB;
# }
#
# ..... with .....
#
# @Inject
# private SomeServiceA serviceA;
#
# @Inject
# private SomeServiceB serviceB;
#
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
                    #check if the argument has annotation, for example - @InProcessMode ChannelFactory channelFactory
                    additional_annotation = ''
                    if '@' in argument:
                        additional_annotation, argument = argument.split(' ', 1)

                    if argument and argument + ';' in line:
                        content_new.append('  @Inject ' + additional_annotation)
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
    match = re.search(r'\((.*?)\)', ''.join(lines))
    if match:
        arguments = [a.strip() for a in match.group(1).strip().split(',') if a.strip()]
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
        new_module = re.sub(r'\.class', '()', new_module)
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
            if 'java_test_internal' in content and 'test_type = "junit"' not in content:
                content = re.sub(r'java_test_internal\(',
                                 'java_test_internal(\n\ttest_type = "junit",', content)

            if 'TEST_DEPS' in content and '//infra/library/lang:test_utils' not in content:
                content = re.sub(r'TEST_DEPS = \[',
                                 'TEST_DEPS = [\n\t"//infra/library/lang:test_utils",', content)

            with open(buck_file, 'w') as fn_out:
                fn_out.write(content)


def migrate_tests(test_dir):
    test_files = []
    for path, dir, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.java') \
                    and not file.endswith('AbstractJerseyTestNG.java') \
                    and not file.endswith('Assert.java') \
                    and not file.endswith('AssertionUtils.java') \
                    and 'NullChecking' not in file:
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
