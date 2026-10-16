from chatterbox_studio.error_messages import friendly_generation_error


def test_pagefile_error_includes_actionable_recovery():
    text = friendly_generation_error(RuntimeError('The paging file is too small for this operation to complete. (os error 1455)'))
    assert 'Windows error 1455' in text
    assert 'system-managed' in text
    assert 'Nano' in text
    assert 'os error 1455' in text


def test_other_error_is_preserved():
    assert friendly_generation_error(ValueError('file missing')) == 'file missing'
