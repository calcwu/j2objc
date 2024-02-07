from setup import junit4_to_junit5
from setup import assert_equal_content


content = """
    @Before
    @BeforeAll
    @BeforeClass
    @After
    @AfterAll
"""

expected = """    
    @BeforeEach
    @BeforeAll
    @BeforeAll
    @AfterEach
    @AfterAll
"""


def test_migrate_assert():
    content_new = junit4_to_junit5.migrate_annotations(content)
    assert_equal_content(content_new, expected)
