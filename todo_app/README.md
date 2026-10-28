# L7 Todo API 수업 실습

L6의 DB 기반 Todo를 바탕으로 L7 2차시의 API 6개를 구현하고, L7 3차시의 기본 테스트 5개를 추가한 실습본입니다. HW4 변경 전 비교 기준입니다.

기존 공용 가상환경에서 Flask, Flask-SQLAlchemy, flask-restx를 설치합니다.

이 폴더에서 `python -m flask --app app --debug run`을 실행하고 `/` 및 `/api/docs`를 확인합니다. `python -m unittest -v`로 테스트 5개를 실행합니다.

`TODO_DATABASE_URI` 환경변수가 없으면 교재처럼 SQLite `instance/todo.db`를 사용합니다. 테스트는 import 전에 메모리 DB를 선택하여 실제 DB를 보호합니다.
