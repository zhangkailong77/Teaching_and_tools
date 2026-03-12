import unittest

from app.api.v1.endpoints import content


class TestInteractiveManifestHelpers(unittest.TestCase):
    def test_extract_available_lesson_ids_from_app_data_returns_sorted_int_ids(self):
        app_data = {
            "version": "v1.0.0",
            "lessons": {
                "205": {"entry": "interactive/1/ppt-test/lesson_205/v1.0.0/index.html"},
                "abc": {"entry": "interactive/1/ppt-test/lesson_abc/v1.0.0/index.html"},
                "204": {"entry": "interactive/1/ppt-test/lesson_204/v1.0.0/index.html"},
                "206": {"version": "v1.0.0"},
                "207": {"entry": ""},
            },
        }

        self.assertEqual(
            content._extract_available_lesson_ids_from_app_data(app_data),
            [204, 205],
        )

    def test_extract_available_lesson_ids_from_app_data_handles_invalid_payload(self):
        self.assertEqual(content._extract_available_lesson_ids_from_app_data(None), [])
        self.assertEqual(content._extract_available_lesson_ids_from_app_data("invalid"), [])


if __name__ == "__main__":
    unittest.main()
