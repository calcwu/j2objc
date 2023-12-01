from setup import testng2junit5
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

  @Test (expectedExceptions = IllegalArgumentException.class,
      expectedExceptionsMessageRegExp = ".*encountered multiple partitions.*")
  public void verifyMultiplePartitionsUnsupported() {
    DestinationPartition dp1 = new DestinationPartition(
        new Destination(TEST_ENVIRONMENT, "destination"), 0);
    DestinationPartition dp2 = new DestinationPartition(
        new Destination(TEST_ENVIRONMENT, "destination"), 1);
    strategy.load("test.group", Type.PUBSUB, ImmutableSet.of(dp1, dp2));
  }

  @Test(
      expectedExceptions = IllegalArgumentException.class,
      expectedExceptionsMessageRegExp = "Invalid rate: .*")
  public void testInvalidTier() {
    new RateTierImpl(-1, -5.0, 0.0, 1.0);
  }

  @ParameterizedTest(expectedExceptions = IllegalArgumentException.class)
  public void testParameteredTest() {
    new RateTierImpl(-1, -5.0, 0.0, 1.0);
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

  @Test
  public void throwsIfThereAreMultiplePartitions(){
    assertThrows(
      () -> {
        when(messagingAdmin.hasDestinationBlocking(any())).thenReturn(true);
        when(messagingAdmin.getTopicPartitionInfo(any()))
            .thenReturn(ImmutableList.of(new TestTopicPartitionInfo(), new TestTopicPartitionInfo()));
        var destination = MessagingTestUtils.createRandom();
        var offsetProvider = new DestinationOffsetProviderImpl(messagingAdmin, destination);
        offsetProvider.getLatestOffset();
      },
      IllegalStateException.class
    );
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

  @Test
  public void verifyMultiplePartitionsUnsupported() {
    assertThrows(
      () -> {
        DestinationPartition dp1 = new DestinationPartition(
            new Destination(TEST_ENVIRONMENT, "destination"), 0);
        DestinationPartition dp2 = new DestinationPartition(
            new Destination(TEST_ENVIRONMENT, "destination"), 1);
        strategy.load("test.group", Type.PUBSUB, ImmutableSet.of(dp1, dp2));
      },
      IllegalArgumentException.class,
      ".*encountered multiple partitions.*"
    );
  }

  @Test
  public void testInvalidTier() {
    assertThrows(
      () -> {
        new RateTierImpl(-1, -5.0, 0.0, 1.0);
      },
      IllegalArgumentException.class,
      "Invalid rate: .*"
    );
  }

  @ParameterizedTest
  public void testParameteredTest() {
    assertThrows(
      () -> {
        new RateTierImpl(-1, -5.0, 0.0, 1.0);
      },
      IllegalArgumentException.class
    );
  }
"""


def test_migrate_exceptions():
    content_new = testng2junit5.migrate_exceptions(content)
    assert_equal_content(content_new, expected)
