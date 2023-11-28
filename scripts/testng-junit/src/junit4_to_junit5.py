import os
import sys
import re

throw_template = '''    assertThrows(
      %s,
      () -> {
%s
      }
    );'''


def migrate_imports(content):
    """Updates import statements from TestNG to JUnit."""
    content_new = re.sub('org.junit.Test', 'org.junit.jupiter.api.Test', content)

    # Before
    content_new = re.sub('import org.junit.Before;',
                         '''import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.BeforeAll;''', content_new)

    # After
    content_new = re.sub('import org.junit.After;',
                         '''import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.AfterAll;''', content_new)

    # Assert
    content_new = re.sub('org.junit.Assert', 'org.junit.jupiter.api.Assertions', content_new)
    content_new = re.sub('org.testng.AssertJUnit', 'org.junit.jupiter.api.Assertions', content_new)

    return content_new


def migrate_annotations(content):
    content_new = content

    content_new = re.sub('@BeforeClass', '@BeforeAll', content_new)

    if '@BeforeEach' not in content_new:
        content_new = re.sub(r'@Before(?!\s*All)', '@BeforeEach', content_new)

    content_new = re.sub('@AfterMethod', '@AfterEach', content_new)

    if '@AfterEach' not in content_new:
        content_new = re.sub(r'@After(?!\s*All)', '@AfterEach', content_new)

    content_new = re.sub('@AfterClass', '@AfterAll', content_new)

    if '@Disabled' not in content_new:
        content_new = re.sub('org.junit.Ignore', 'org.junit.jupiter.api.Disabled', content_new)
        content_new = re.sub('@Ignore', '@Disabled', content_new)
    return content_new


def migrate_mockito_rule_annotation(content):
    if 'MockitoRule' not in content:
        return content

    content_new = re.sub(
      'import org.mockito.junit.MockitoRule;',
      'import org.junit.jupiter.api.extension.ExtendWith;\nimport org.mockito.junit.jupiter.MockitoExtension;', content)

    content_new = re.sub('public class', '@ExtendWith(MockitoExtension.class)\npublic class', content_new)
    pattern = re.compile(r'^\s*@Rule\s+public\s+MockitoRule\s+rule\s*=\s*.*$', re.MULTILINE)
    content_new = re.sub(pattern, '', content_new)
    return content_new


def migrate_guice_injector(content):
    if 'createInjector' not in content \
            or '@TestInstance(Lifecycle.PER_CLASS)' in content:
        return content

    content_new = re.sub('@BeforeEach', '@BeforeAll', content)

    if "@BeforeAll" in content_new:
        content_new = re.sub('import com.google.inject.Guice;',
                             '''import com.google.inject.Guice;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;''', content_new)
        content_new = re.sub(r'public(\s*final)?\s*class', '@TestInstance(Lifecycle.PER_CLASS)\npublic class', content_new)

    return content_new


###
# with
# assertThrows(
#         IllegalArgumentException.class,
#         () -> {
#           Config config = ConfigFactory.load().getConfig("test8." + BatuNotificationFilterTest.class.getPackageName());
#           new BatuNotificationFilter(config);
#         },
#         "notification_filter.mode must be either 'include' or 'exclude'"
# );
#
def migrate_exceptions(content):
    if '@Test(expected' not in content:
        return content

    #Add import
    content_new = re.sub('import org.junit.jupiter.api.Test;',
        '''import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertThrows;''', content)

    pattern = r'@Test\s*\(\s*expected\s*=\s*([^\)]+)\s*\)'
    new_content = []
    content_iter = iter(content_new.split('\n'))
    for line in content_iter:
        method_body = []
        method_signature = ''
        if '@Test' in line and '(' in line:
            at_test_annotation_line = line
            while ')' not in line:
                line = next(content_iter)
                at_test_annotation_line += line

            matches = re.search(pattern, at_test_annotation_line)

            if not matches:
                new_content.append(at_test_annotation_line)
                continue

            print('expected exception + message matches:', matches)

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

            if matches:
                expected_exception_class = matches.group(1).strip()
                # add the method boby replacement
                method_body_value = throw_template % (expected_exception_class, '\n'.join(method_body))
                new_content.append(method_body_value)

        new_content.append(line)

    return '\n'.join(new_content)


def migrate_asserts(content):

    content_new = content
    if "assertNotNull" in content_new:
        # replace assertNotNull
        pattern = re.compile(r'assertNotNull\((".*?")\s*,\s*(.*?)\);')

        # Use re.sub() to replace the pattern with the desired format
        content_new = re.sub(pattern, r'assertNotNull(\2, \1);', content_new)

    if "assertTrue" in content_new:
        # replace assertTrue
        pattern = re.compile(r'assertTrue\((".*?")\s*,\s*(.*?)\);')
        content_new = re.sub(pattern, r'assertTrue(\2, \1);', content_new)

    return content_new


def migrate_data_provider(content):
    if "@UseDataProvider" not in content:
        return content

    content_new = re.sub('''import com.tngtech.java.junit.dataprovider.DataProvider;
import com.tngtech.java.junit.dataprovider.DataProviderRunner;''',
                         'import org.junit.jupiter.params.ParameterizedTest;', content)

    content_new = re.sub('com.tngtech.java.junit.dataprovider.UseDataProvider',
                         'org.junit.jupiter.params.provider.MethodSource', content_new)

    content_new = re.sub(r'@RunWith\(DataProviderRunner\.class\)\s*public(\s*final)?\s*class',
                         'public class', content_new)

    content_new = re.sub(r'@Test\s*@UseDataProvider', '@ParameterizedTest\n  @MethodSource', content_new)

    content_new = re.sub(r'@DataProvider\s*public static', 'public static', content_new)

    return content_new


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
            content_new = migrate_annotations(content_new)
            content_new = migrate_mockito_rule_annotation(content_new)
            content_new = migrate_guice_injector(content_new)
            content_new = migrate_exceptions(content_new)
            content_new = migrate_asserts(content_new)
            content_new = migrate_data_provider(content_new)
            with open(file_name, 'w') as fn:
                fn.write(content_new)


def migrate_buck(buck_module):
    buck_file = buck_module + "/BUCK"
    if os.path.isfile(buck_file):
        with open(buck_file, 'r') as f_in:
            content = f_in.read()
            if 'java_test_internal' in content and 'test_type = "junit"' not in content:
                content = re.sub(r'java_test_internal\(',
                                 'java_test_internal(\n    test_type = "junit",', content)

            if 'TEST_DEPS' in content and '//infra/library/lang:test_utils' not in content:
                content = re.sub(r'TEST_DEPS = \[',
                                 'TEST_DEPS = [\n    "//infra/library/lang:test_utils",', content)

            with open(buck_file, 'w') as fn_out:
                fn_out.write(content)


def main():
    if len(sys.argv) == 1:
        print('usage: {} <directory_to_migrate>'.format(sys.argv[0]))
        sys.exit(1)

    buck_module = sys.argv[1]
    test_dir = buck_module
    if 'src/test' not in buck_module:
        test_dir = buck_module + '/src/test'
        migrate_buck(buck_module)

    migrate_tests(test_dir)


if __name__ == '__main__':
    sys.exit(main())
