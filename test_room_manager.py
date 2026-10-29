import pytest
from game.room_manager import RoomManager, PlayerState

def test_room_creation():
    mgr = RoomManager()
    host = PlayerState(sid='sid_host_1', user_id=1, username='HostUser', avatar='cyber_ninja')
    room = mgr.create_room('sid_host_1', host)

    assert room.code.startswith('QC-')
    assert room.host_sid == 'sid_host_1'
    assert len(room.players) == 1
    assert mgr.get_room(room.code) is room

def test_join_room():
    mgr = RoomManager()
    host = PlayerState(sid='sid_host_2', user_id=1, username='HostUser', avatar='cyber_ninja')
    room = mgr.create_room('sid_host_2', host)

    guest = PlayerState(sid='sid_guest_2', user_id=2, username='GuestUser', avatar='pixel_queen')
    joined = mgr.join_room(room.code, guest)

    assert joined is not None
    assert len(room.players) == 2
    assert mgr.get_room_by_sid('sid_guest_2') is room

def test_ready_check():
    mgr = RoomManager()
    host = PlayerState(sid='sid_host_3', user_id=1, username='HostUser', avatar='cyber_ninja')
    room = mgr.create_room('sid_host_3', host, game_mode='pvp')

    guest = PlayerState(sid='sid_guest_3', user_id=2, username='GuestUser', avatar='pixel_queen')
    mgr.join_room(room.code, guest)

    assert room.all_players_ready() is False

    host.is_ready = True
    assert room.all_players_ready() is False

    guest.is_ready = True
    assert room.all_players_ready() is True

def test_leave_and_host_migration():
    mgr = RoomManager()
    host = PlayerState(sid='sid_host_4', user_id=1, username='HostUser', avatar='cyber_ninja')
    room = mgr.create_room('sid_host_4', host)

    guest = PlayerState(sid='sid_guest_4', user_id=2, username='GuestUser', avatar='pixel_queen')
    mgr.join_room(room.code, guest)

    # Host leaves -> guest should be promoted to host
    mgr.leave_room('sid_host_4')
    assert room.host_sid == 'sid_guest_4'
    assert len(room.players) == 1
