import logging
from typing import Optional
import os

from flask import Flask, request, jsonify
from psycopg2 import pool, errors
from psycopg2.errorcodes import UNIQUE_VIOLATION


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['DEBUG'] = True

db_pool = pool.SimpleConnectionPool(
    1,
    10,
    host=os.environ['DB_HOST'],
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD']
)


def is_valid(value: Optional[int]) -> bool:
    return value is not None and isinstance(value, int)


@app.route('/health', methods=['GET'])
def healthcheck():
    return jsonify(status='OK'), 200


@app.route('/api/user', methods=['POST'])
def add_user():
    user_id = request.json.get('user_id')
    chat_id = request.json.get('chat_id')
    print(user_id, chat_id)

    if not is_valid(user_id) or not is_valid(chat_id):
        return jsonify({
            'status': 400,
            'error': 'Bad Request',
            'message': 'Incorrect format for arguments'
        }), 400

    conn = db_pool.getconn()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO  t_users.users (user_id, chat_id) VALUES (%s, %s);', (user_id, chat_id))
        conn.commit()
    except errors.lookup(UNIQUE_VIOLATION):
        return jsonify({
            'status': 409,
            'error': 'Conflict',
            'message': 'User has already enrolled into subscription.'
        }), 409
    except Exception as e:
        logger.info(e)
        conn.rollback()
        return str(e), 500
    finally:
        cursor.close()
        db_pool.putconn(conn)

    return jsonify({
        "status": 201,
        "message": "User chat recorded"
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
