import os
import unittest
from unittest.mock import patch

# SQLAlchemy는 초기화할 때 DB 주소를 읽습니다. app을 가져오기 전에 설정합니다.
with patch.dict(os.environ, {"TODO_DATABASE_URI": "sqlite:///:memory:"}):
    import app as todo_app


class TodoApiTest(unittest.TestCase):
    def setUp(self):
        todo_app.app.config['TESTING'] = True
        self.client = todo_app.app.test_client()
        self.ctx = todo_app.app.app_context()
        self.ctx.push()
        # 실제 파일 DB가 연결돼 있으면 삭제하지 않고 즉시 중단합니다.
        self.assertEqual(todo_app.db.engine.url.database, ':memory:')
        todo_app.db.drop_all()
        todo_app.db.create_all()

    def tearDown(self):
        todo_app.db.session.remove()
        self.ctx.pop()

    def make(self, **data):
        return self.client.post('/api/todos/', json={'text': '우유 사기', **data})

    def test_create_and_get_note(self):
        r = self.make(note='2리터짜리로')
        self.assertEqual(r.status_code, 201)
        body = r.get_json()
        self.assertEqual(body, {'id': body['id'], 'text': '우유 사기', 'done': False, 'note': '2리터짜리로'})
        self.assertEqual(r.headers['Location'], f"/api/todos/{body['id']}")
        one = self.client.get(r.headers['Location'])
        self.assertEqual(one.status_code, 200)
        self.assertEqual(one.get_json(), body)

    def test_optional_note_defaults_empty(self):
        self.assertEqual(self.make().get_json()['note'], '')

    def test_list_without_filter_keeps_both_states(self):
        self.make(done=True)
        self.make(text='책 반납')
        r = self.client.get('/api/todos/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()), 2)

    def test_filter_true_and_false(self):
        a = self.make(done=True).get_json()
        b = self.make(text='책 반납').get_json()
        for value, expected in [('true', a), ('false', b), ('TRUE', a)]:
            r = self.client.get('/api/todos/?done=' + value)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.get_json(), [expected])

    def test_patch_keeps_unsent_fields(self):
        a = self.make(note='유지할 설명').get_json()
        url = f"/api/todos/{a['id']}"
        for _ in range(2):
            r = self.client.patch(url, json={'done': True})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.get_json(), {**a, 'done': True})
        r = self.client.patch(url, json={'note': '바꾼 설명'})
        self.assertEqual(r.get_json(), {**a, 'done': True, 'note': '바꾼 설명'})

    def test_put_replaces_and_defaults(self):
        a = self.make(done=True, note='이전 설명').get_json()
        r = self.client.put(f"/api/todos/{a['id']}", json={'text': '책 반납'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {'id': a['id'], 'text': '책 반납', 'done': False, 'note': ''})

    def test_missing_id_returns_json_404(self):
        r = self.client.get('/api/todos/999')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.get_json(), {'message': '999 번 할 일이 없습니다'})

    def test_delete_empty_body_and_then_404(self):
        a = self.make().get_json()
        url = f"/api/todos/{a['id']}"
        r = self.client.delete(url)
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.data, b'')
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_post_requires_text(self):
        r = self.client.post('/api/todos/', json={'done': True})
        self.assertEqual(r.status_code, 400)
        self.assertIn('text', r.get_json()['errors'])

    def test_docs_schema_and_shared_html(self):
        self.make(text='API에서 추가한 할 일')
        page = self.client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertIn('API에서 추가한 할 일', page.get_data(as_text=True))
        self.assertEqual(self.client.get('/api/docs').status_code, 200)
        spec = self.client.get('/api/swagger.json').get_json()
        self.assertEqual(set(spec['paths']['/todos/']) & {'get', 'post'}, {'get', 'post'})
        self.assertEqual(set(spec['paths']['/todos/{id}']) & {'get', 'put', 'patch', 'delete'}, {'get', 'put', 'patch', 'delete'})
        self.assertIn('note', spec['definitions']['Todo']['properties'])
        self.assertIn('done', [p['name'] for p in spec['paths']['/todos/']['get']['parameters']])


if __name__ == '__main__':
    unittest.main()
