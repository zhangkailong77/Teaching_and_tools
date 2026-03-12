import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.school_config import ensure_school_config
from app.db.base_class import Base
from app.models import course as _course_models  # noqa: F401
from app.models import profile as _profile_models  # noqa: F401
from app.models import user as _user_models  # noqa: F401
from app.models.school_config import SchoolConfig


class TestSchoolConfigBootstrap(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_ensure_school_config_inserts_when_empty(self):
        session = self.Session()
        try:
            action = ensure_school_config(
                db=session,
                school_id="school_a",
                school_name="School A",
            )
            self.assertEqual(action, "created")
            rows = session.query(SchoolConfig).all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].school_id, "school_a")
            self.assertEqual(rows[0].school_name, "School A")
        finally:
            session.close()

    def test_ensure_school_config_updates_when_exists_and_differs(self):
        session = self.Session()
        try:
            session.add(
                SchoolConfig(
                    school_id="existing_school",
                    school_name="Existing School",
                )
            )
            session.commit()

            action = ensure_school_config(
                db=session,
                school_id="school_b",
                school_name="School B",
            )
            self.assertEqual(action, "updated")
            rows = session.query(SchoolConfig).all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].school_id, "school_b")
            self.assertEqual(rows[0].school_name, "School B")
        finally:
            session.close()

    def test_ensure_school_config_keeps_when_exists_and_same(self):
        session = self.Session()
        try:
            session.add(
                SchoolConfig(
                    school_id="same_school",
                    school_name="Same School",
                )
            )
            session.commit()

            action = ensure_school_config(
                db=session,
                school_id="same_school",
                school_name="Same School",
            )
            self.assertEqual(action, "unchanged")
            rows = session.query(SchoolConfig).all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].school_id, "same_school")
            self.assertEqual(rows[0].school_name, "Same School")
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
