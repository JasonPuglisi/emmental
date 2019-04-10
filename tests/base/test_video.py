"""Tests video handling functionality."""

import uuid
import pytest
from src.video import get_extension, get_video_list, is_valid_filename, Video
from .test_db import arrange_users, TEST_USERS  # pylint: disable=unused-import


@pytest.mark.parametrize('filename, extension, username', [
    ('video.mp4', 'mp4', TEST_USERS[0][0]),
    ('video2.webm', 'webm', TEST_USERS[1][0])
])
def test_video_class(filename, extension, username):
    """Ensure video class is created and functions properly."""
    video = Video()
    assert (video.video_id == '' and video.extension == '' and
            video.user_id == '')

    video.create(filename, username)
    assert (uuid.UUID(video.video_id) and video.extension == extension and
            uuid.UUID(video.user_id))

    temp_video_id = uuid.uuid4()
    temp_extension = 'webm' if extension == 'mp4' else 'mp4'
    temp_user_id = uuid.uuid4()
    video.load(temp_video_id, temp_extension, temp_user_id)
    assert (video.video_id == str(temp_video_id) and
            video.extension == temp_extension and
            video.user_id == str(temp_user_id))

    storage_path = '/srv/videos'
    assert (video.get_path(storage_path) ==
            f'{storage_path}/{temp_video_id}.{temp_extension}')

    assert video.save()
    assert video.delete()


@pytest.mark.parametrize('filename, success', [
    ('video.mp4', True),
    ('video.webm', True),
    ('video.ogg', True),
    ('video.mp4.html', False),
    ('video.html', False),
    ('', False),
    ('webm', False),
    ('.php', False)
])
def test_is_valid_filename(filename, success):
    """Ensure video filename is validated correctly."""
    assert is_valid_filename(filename) == success


@pytest.mark.parametrize('filename, extension', [
    ('video.mp4', 'mp4'),
    ('video.webm', 'webm'),
    ('video.html', 'html'),
    ('video', ''),
    ('.mp3', 'mp3')
])
def test_get_extension(filename, extension):
    """Ensure extension is properly extracted from filename."""
    assert get_extension(filename) == extension


def test_get_video_list():
    """Ensure video list is properly returned from databse."""
    video_id = uuid.uuid4()
    extension = 'mp4'
    user_id = uuid.uuid4()

    video = Video()
    video.load(video_id, extension, user_id)
    video.save()

    videos = get_video_list()
    returned = videos[-1]
    assert (returned.video_id == str(video_id) and
            returned.extension == extension and
            returned.user_id == str(user_id))
    video.delete()
