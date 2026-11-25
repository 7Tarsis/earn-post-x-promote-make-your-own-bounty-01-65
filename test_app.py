import unittest

from app import create_task, delete_task, get_task, init_db, list_tasks, update_task


class TestCrudFlow(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_crud_flow(self):
        created = create_task("first task")
        self.assertEqual(created["title"], "first task")
        self.assertFalse(created["done"])

        listed = list_tasks()
        self.assertGreaterEqual(len(listed), 1)

        fetched = get_task(created["id"])
        self.assertEqual(fetched["id"], created["id"])

        updated = update_task(created["id"], done=True)
        self.assertTrue(updated["done"])

        deleted = delete_task(created["id"])
        self.assertTrue(deleted)


if __name__ == "__main__":
    unittest.main()
