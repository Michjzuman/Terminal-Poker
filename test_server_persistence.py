import importlib.util
import os
from contextlib import contextmanager
from pathlib import Path
import sys
import tempfile
import unittest
import uuid


REPO_ROOT = Path(__file__).resolve().parent


@contextmanager
def temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def load_server_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    module_name = f"server_test_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / "server.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ServerPersistenceTests(unittest.TestCase):
    def test_save_users_round_trip_preserves_money(self):
        with tempfile.TemporaryDirectory() as tmpdir, temporary_cwd(Path(tmpdir)):
            server = load_server_module()
            server.users = [
                server.User("alice", "hash-a", 123),
                server.User("bob", "hash-b", 45),
            ]

            server.save_users()

            data = server.read_json_file(server.USERS_LIST_FILE)
            self.assertEqual(data, {
                "users": [
                    {
                        "username": "alice",
                        "password_hash": "hash-a",
                        "money": 123,
                    },
                    {
                        "username": "bob",
                        "password_hash": "hash-b",
                        "money": 45,
                    },
                ]
            })

    def test_reset_after_hand_clears_busted_players_and_round_state(self):
        with tempfile.TemporaryDirectory() as tmpdir, temporary_cwd(Path(tmpdir)):
            server = load_server_module()
            table = server.Table()
            busted = server.User("busted", "hash", 0)
            survivor = server.User("survivor", "hash", 10)

            table.players = [busted, survivor]
            table.game = None
            table.info = {"stale": True}
            table.count_down = 1
            busted.last_handshake = (table.id, server.datetime.now())
            survivor.last_handshake = (table.id, server.datetime.now())

            table.reset_after_hand()

            self.assertEqual([player.name for player in table.players], ["survivor"])
            self.assertIsNone(table.game)
            self.assertEqual(table.info, {})
            self.assertEqual(table.count_down, server.WAIT_UNITL_ROUND_START)
            self.assertEqual(busted.last_handshake, ())
            self.assertEqual(survivor.last_handshake[0], table.id)
            self.assertIsNone(busted.game)
            self.assertIsNone(survivor.game)

    def test_do_move_rejects_non_current_player(self):
        with tempfile.TemporaryDirectory() as tmpdir, temporary_cwd(Path(tmpdir)):
            server = load_server_module()
            password = "pw"
            user_a = server.User("alice", server.hash_password(password), 100)
            user_b = server.User("bob", server.hash_password(password), 100)
            server.users = [user_a, user_b]

            table = server.Table()
            server.tables = [table]
            table.players = [user_a, user_b]
            table.start_hand([user_a, user_b])

            self.assertEqual(table.game.players[table.game.turn].name, "alice")

            with self.assertRaises(server.HTTPException) as exc:
                server.do_move(server.MoveBody(
                    username="bob",
                    password=password,
                    table_id=table.id,
                    move_type="Call",
                    amount=0,
                ))

            self.assertEqual(exc.exception.status_code, 409)
            self.assertIn("not your turn", exc.exception.detail.lower())

    def test_do_move_allows_short_stack_call(self):
        with tempfile.TemporaryDirectory() as tmpdir, temporary_cwd(Path(tmpdir)):
            server = load_server_module()
            password = "pw"
            short_stack = server.User("short", server.hash_password(password), 1)
            small_blind = server.User("sb", server.hash_password(password), 100)
            big_blind = server.User("bb", server.hash_password(password), 100)
            server.users = [short_stack, small_blind, big_blind]

            table = server.Table()
            server.tables = [table]
            table.players = [short_stack, small_blind, big_blind]
            table.start_hand([short_stack, small_blind, big_blind])

            response = server.do_move(server.MoveBody(
                username="short",
                password=password,
                table_id=table.id,
                move_type="Call",
                amount=0,
            ))

            self.assertEqual(response, {"ok": True})
            self.assertIsNotNone(short_stack.move)
            self.assertEqual(short_stack.move.type.value, "Call")


if __name__ == "__main__":
    unittest.main()
