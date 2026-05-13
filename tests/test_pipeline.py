import unittest

from backend.app import app, reset_database


class QueryLitePipelineTests(unittest.TestCase):
    def setUp(self):
        reset_database()
        self.client = app.test_client()

    def test_select_query_returns_compiler_phases(self):
        response = self.client.post("/run", json={"query": "SELECT name FROM students WHERE age > 20;"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        for key in [
            "tokens",
            "symbol_table",
            "semantic",
            "intermediate_code",
            "optimized_code",
            "code_generation",
            "output",
        ]:
            self.assertIn(key, payload)

        self.assertEqual(payload["output"]["row_count"], 2)
        self.assertEqual(payload["output"]["rows"][0]["name"], "Alice")

    def test_create_insert_update_delete_flow(self):
        commands = [
            "CREATE TABLE users (id, name, age);",
            "INSERT INTO users (id, name, age) VALUES (1, 'Sara', 20);",
            "UPDATE users SET age = 25 WHERE name = 'Sara';",
            "DELETE FROM users WHERE age < 21 OR name = 'Nobody';",
            "SELECT * FROM users;",
        ]

        last_payload = None
        for query in commands:
            response = self.client.post("/run", json={"query": query})
            self.assertEqual(response.status_code, 200, msg=f"Failed query: {query}")
            last_payload = response.get_json()

        self.assertEqual(last_payload["output"]["row_count"], 1)
        self.assertEqual(last_payload["output"]["rows"][0]["age"], 25)


if __name__ == "__main__":
    unittest.main()
