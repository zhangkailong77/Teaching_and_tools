import unittest

from app.core import security
from app.core.federation_sso import consume_federation_ticket, issue_federation_ticket
from app.core.config import settings
from jose import jwt


class InMemoryOnceStore:
    def __init__(self):
        self.keys = set()

    def store(self, key: str, ttl_seconds: int) -> bool:
        if key in self.keys:
            return False
        self.keys.add(key)
        return True

    def consume(self, key: str) -> bool:
        if key not in self.keys:
            return False
        self.keys.remove(key)
        return True


class TestFederationSSO(unittest.TestCase):
    def test_issue_ticket_contains_school_id_and_type(self):
        store = InMemoryOnceStore()
        result = issue_federation_ticket(
            user_id=11,
            username="alice",
            role="student",
            school_id="school-a",
            ttl_seconds=60,
            store_jti_fn=store.store,
        )
        payload = jwt.decode(
            result["ticket"],
            settings.secret_key,
            algorithms=[security.ALGORITHM],
        )
        self.assertEqual(payload["school_id"], "school-a")
        self.assertEqual(payload["typ"], "federation_sso_ticket")
        self.assertIn("jti", payload)
        self.assertEqual(result["expires_in"], 60)

    def test_consume_ticket_is_one_time_only(self):
        store = InMemoryOnceStore()
        issue_result = issue_federation_ticket(
            user_id=12,
            username="bob",
            role="teacher",
            school_id="school-b",
            ttl_seconds=60,
            store_jti_fn=store.store,
        )

        first = consume_federation_ticket(
            ticket=issue_result["ticket"],
            consume_jti_fn=store.consume,
        )
        self.assertEqual(first["username"], "bob")
        self.assertEqual(first["school_id"], "school-b")

        with self.assertRaises(ValueError):
            consume_federation_ticket(
                ticket=issue_result["ticket"],
                consume_jti_fn=store.consume,
            )


if __name__ == "__main__":
    unittest.main()
