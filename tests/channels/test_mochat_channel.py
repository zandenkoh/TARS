from TARS.channels.mochat import resolve_mochat_target, MochatTarget

def test_resolve_mochat_target_empty_input():
    # Empty strings and None behavior (type hinted as str but testing robustness)
    target1 = resolve_mochat_target("")
    assert target1.id == ""
    assert target1.is_panel is False
    assert target1.user_id is None

    target2 = resolve_mochat_target("   ")
    assert target2.id == ""
    assert target2.is_panel is False
    assert target2.user_id is None

    # Passing None implicitly via (raw or "")
    target3 = resolve_mochat_target(None)
    assert target3.id == ""
    assert target3.is_panel is False
    assert target3.user_id is None

def test_resolve_mochat_target_basic_id():
    # Basic strings without prefix
    target = resolve_mochat_target("room123")
    assert target.id == "room123"
    # Not forced panel, and doesn't start with session_ -> is_panel = True
    assert target.is_panel is True
    assert target.user_id is None

def test_resolve_mochat_target_session_id():
    # Strings starting with session_ without prefix
    target = resolve_mochat_target("session_456")
    assert target.id == "session_456"
    # Not forced panel, and starts with session_ -> is_panel = False
    assert target.is_panel is False
    assert target.user_id is None

def test_resolve_mochat_target_mochat_prefix():
    # mochat: prefix is not forced panel
    target = resolve_mochat_target("mochat:room123")
    assert target.id == "room123"
    assert target.is_panel is True
    assert target.user_id is None

    target_session = resolve_mochat_target("mochat:session_456")
    assert target_session.id == "session_456"
    assert target_session.is_panel is False
    assert target_session.user_id is None

def test_resolve_mochat_target_forced_panel_prefixes():
    # group:, channel:, panel: prefixes force is_panel to True
    for prefix in ("group:", "channel:", "panel:"):
        # Even with session_ name, forced_panel overrides
        target = resolve_mochat_target(f"{prefix}session_789")
        assert target.id == "session_789"
        assert target.is_panel is True
        assert target.user_id is None

        target_normal = resolve_mochat_target(f"{prefix}room123")
        assert target_normal.id == "room123"
        assert target_normal.is_panel is True
        assert target_normal.user_id is None

def test_resolve_mochat_target_prefix_case_insensitivity():
    target = resolve_mochat_target("PaNeL:  room123  ")
    assert target.id == "room123"
    assert target.is_panel is True
    assert target.user_id is None

def test_resolve_mochat_target_empty_after_prefix():
    # If the prefix strips out to nothing, return empty
    target = resolve_mochat_target("panel:")
    assert target.id == ""
    assert target.is_panel is False
    assert target.user_id is None

    target_spaces = resolve_mochat_target("group:   ")
    assert target_spaces.id == ""
    assert target_spaces.is_panel is False
    assert target_spaces.user_id is None

def test_resolve_mochat_target_with_user_id():
    # Test strings with `@` symbol (issue description scenario)
    target1 = resolve_mochat_target("room123@user456")
    assert target1.id == "room123"
    assert target1.user_id == "user456"
    assert target1.is_panel is True

    target2 = resolve_mochat_target("session_123@user456")
    assert target2.id == "session_123"
    assert target2.user_id == "user456"
    assert target2.is_panel is False

    target3 = resolve_mochat_target("panel:room123@user456")
    assert target3.id == "room123"
    assert target3.user_id == "user456"
    assert target3.is_panel is True

def test_resolve_mochat_target_empty_room_with_user_id():
    # Missing room part
    target1 = resolve_mochat_target("@user456")
    assert target1.id == ""
    assert target1.user_id == "user456"
    assert target1.is_panel is False

    # Missing room part but with a prefix applied
    target2 = resolve_mochat_target("mochat:@user456")
    assert target2.id == ""
    assert target2.user_id == "user456"
    assert target2.is_panel is False
