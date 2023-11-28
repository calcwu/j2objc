from setup import junit4_to_junit5
from setup import assert_equal_content


content = """
import com.tngtech.java.junit.dataprovider.UseDataProvider;

@RunWith(DataProviderRunner.class)
public final class AccountImportMappingNotificationResourceTest extends BatuResourceTestBase {

  @Test
  @UseDataProvider("getServices")
  public void someTest(DataUploadRequestMerger service) {
"""

expected = """    
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

public class AccountImportMappingNotificationResourceTest extends BatuResourceTestBase {

  @ParameterizedTest
  @MethodSource("getServices")
  public void someTest(DataUploadRequestMerger service) {
"""


def test_migrate_assert():
    content_new = junit4_to_junit5.migrate_data_provider(content)
    print(content_new)
    #assert_equal_content(content_new, expected)
