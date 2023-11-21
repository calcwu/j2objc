import os
import sys
import re


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


def migrate_testng_annotations(content):
    # Most of our methods are more member friendly.
    content_new = re.sub('@Before', '@BeforeEach', content)

    content_new = re.sub('@AfterMethod', '@AfterEach', content_new)
    content_new = re.sub('@AfterClass', '@AfterAll', content_new)

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
    if 'Guice.createInjector' not in content:
        return content

    content_new = re.sub('import com.google.inject.Guice;',
                         '''import com.google.inject.Guice;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;''', content)

    content_new = re.sub('public class', '@TestInstance(Lifecycle.PER_CLASS)\npublic class', content_new)
    content_new = re.sub('@BeforeEach', '@BeforeAll', content_new)
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
            content_new = migrate_testng_annotations(content_new)
            content_new = migrate_mockito_rule_annotation(content_new)
            content_new = migrate_guice_injector(content_new)
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
