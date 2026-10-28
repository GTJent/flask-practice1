import os
import unittest
from unittest.mock import patch

with patch.dict(os.environ, {'TODO_DATABASE_URI': 'sqlite:///:memory:'}):
    import app as todo_app


class TodoApiTest(unittest.TestCase):
    def setUp(self):
        todo_app.app.config['TESTING'] = True
        self.client = todo_app.app.test_client()
        self.ctx = todo_app.app.app_context()
        self.ctx.push()
        self.assertEqual(todo_app.db.engine.url.database, ':memory:')
        todo_app.db.drop_all()
        todo_app.db.create_all()

    def tearDown(self):
        todo_app.db.session.remove()
        self.ctx.pop()

    def test_list_keeps_both_states(self):
        self.client.post('/api/todos/', json={'text': '우유 사기', 'done': True})
        self.client.post('/api/todos/', json={'text': '책 반납'})
        r = self.client.get('/api/todos/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()), 2)

    def test_create(self):
        r = self.client.post('/api/todos/', json={'text': '우유 사기'})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()['text'], '우유 사기')

    def test_not_found(self):
        self.assertEqual(self.client.get('/api/todos/999').status_code, 404)

    def test_patch(self):
        a = self.client.post('/api/todos/', json={'text': '책 반납'}).get_json()
        r = self.client.patch(f"/api/todos/{a['id']}", json={'done': True})
        self.assertEqual(r.get_json()['text'], '책 반납')
        self.assertTrue(r.get_json()['done'])

    def test_delete(self):
        a = self.client.post('/api/todos/', json={'text': '지울 것'}).get_json()
        url = f"/api/todos/{a['id']}"
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)
