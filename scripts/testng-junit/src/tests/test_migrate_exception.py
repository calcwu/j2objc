from setup import testng2junit
from setup import assert_equal_content

content = """

  @Test(expectedExceptions = IllegalArgumentException.class,
      expectedExceptionsMessageRegExp = "no last date of range without upper bound: .*")
  public void testGetLast_failUnbounded() {
    DateRangeUtil.getLast(UNBOUNDED_ABOVE);
  }
  
  @Test(expectedExceptions = IllegalStateException.class)
  public void throwsIfThereAreMultiplePartitions(){
    when(messagingAdmin.hasDestinationBlocking(any())).thenReturn(true);
    when(messagingAdmin.getTopicPartitionInfo(any()))
        .thenReturn(ImmutableList.of(new TestTopicPartitionInfo(), new TestTopicPartitionInfo()));
    var destination = MessagingTestUtils.createRandom();
    var offsetProvider = new DestinationOffsetProviderImpl(messagingAdmin, destination);
    offsetProvider.getLatestOffset();
  }

  @Test(expectedExceptions = RuntimeException.class,
      expectedExceptionsMessageRegExp = ".*Timed out.*")
  public void throwsIfMessagingAdminCannotConnect() {
    when(messagingAdmin.connected()).thenReturn(new ManualResetEvent(false));
    var destination = MessagingTestUtils.createRandom();
    var offsetProvider = new DestinationOffsetProviderImpl(messagingAdmin, destination);
    offsetProvider.getLatestOffset();
  }
  
"""

expected = """

  @Test
  public void testGetLast_failUnbounded() {
	assertThrows(
        () -> {
		    DateRangeUtil.getLast(UNBOUNDED_ABOVE);
        },
        IllegalArgumentException.class,
        "no last date of range without upper bound: .*"
    );
  }

  @Test(expected = IllegalStateException.class)
  public void throwsIfThereAreMultiplePartitions(){
    when(messagingAdmin.hasDestinationBlocking(any())).thenReturn(true);
    when(messagingAdmin.getTopicPartitionInfo(any()))
        .thenReturn(ImmutableList.of(new TestTopicPartitionInfo(), new TestTopicPartitionInfo()));
    var destination = MessagingTestUtils.createRandom();
    var offsetProvider = new DestinationOffsetProviderImpl(messagingAdmin, destination);
    offsetProvider.getLatestOffset();
  }  

  @Test
  public void throwsIfMessagingAdminCannotConnect() {
    assertThrows(
      () -> {
            when(messagingAdmin.connected()).thenReturn(new ManualResetEvent(false));
            var destination = MessagingTestUtils.createRandom();
            var offsetProvider = new DestinationOffsetProviderImpl(messagingAdmin, destination);
            offsetProvider.getLatestOffset();
        },
        RuntimeException.class,
        ".*Timed out.*"
    );
  }
    
"""


def test_migrate_exceptions():
    content_new = testng2junit.migrate_exceptions(content)
    assert_equal_content(content_new, expected)
