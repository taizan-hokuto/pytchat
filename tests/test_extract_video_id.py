from pytchat.util import extract_video_id
from pytchat.exceptions import InvalidVideoIdException

VALID_TEST_PATTERNS = (
    ("ABC_EFG_IJK", "ABC_EFG_IJK"),
    ("vid_test_be", "vid_test_be"),
    ("https://www.youtube.com/watch?v=123_456_789", "123_456_789"),
    ("https://www.youtube.com/watch?v=123_456_789&t=123s", "123_456_789"),
    ("www.youtube.com/watch?v=123_456_789", "123_456_789"),
    ("watch?v=123_456_789", "123_456_789"),
    ("youtube.com/watch?v=123_456_789", "123_456_789"),
    ("http://youtu.be/ABC_EFG_IJK", "ABC_EFG_IJK"),
    ("youtu.be/ABC_EFG_IJK", "ABC_EFG_IJK"),
    ("https://www.youtube.com/watch?v=ABC_EFG_IJK&list=XYZ_ABC_12345&start_radio=1&t=1", "ABC_EFG_IJK"),
    ("https://www.youtube.com/embed/ABC_EFG_IJK", "ABC_EFG_IJK"),
    ("www.youtube.com/embed/ABC_EFG_IJK", "ABC_EFG_IJK"),
    ("youtube.com/embed/ABC_EFG_IJK", "ABC_EFG_IJK")
)

INVALID_TEST_PATTERNS = (
    ("", ""),
    ("0123456789", "0123456789"),  # less than 11 letters id
    ("more_than_11_letter_string", "more_than_11_letter_string"),
    ("https://www.youtube.com/watch?v=more_than_11_letter_string", "more_than_11_letter_string"),
    ("https://www.youtube.com/channel/123_456_789", "123_456_789"),
)

TYPEERROR_TEST_PATTERNS = (
    (100, 100),  # not string
    (["123_456_789"], "123_456_789"),  # not string
)


def test_extract_valid_pattern():
    for pattern in VALID_TEST_PATTERNS:
        ret = extract_video_id(pattern[0])
        assert ret == pattern[1]


def test_extract_invalid_pattern():
    for pattern in INVALID_TEST_PATTERNS:
        try:
            extract_video_id(pattern[0])
            assert False
        except InvalidVideoIdException:
            assert True


def test_extract_typeerror_pattern():
    for pattern in TYPEERROR_TEST_PATTERNS:
        try:
            extract_video_id(pattern[0])
            assert False
        except TypeError:
            assert True
