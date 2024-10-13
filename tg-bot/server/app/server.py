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


@app.route('/api/user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')

    conn = db_pool.getconn()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM t_users.users WHERE user_id = %s;', (user_id,))
        result = cursor.fetchone()
        if result is None:
            return '', 204
        else:
            return jsonify({
                'user_id': result[0],
                'chat_id': result[1],
                'subscribed': result[2],
            }), 200
    except Exception as e:
        logger.info(e)
        return str(e), 500
    finally:
        cursor.close()
        db_pool.putconn(conn)


@app.route('/api/user', methods=['POST'])
def add_user_to_db():
    user_id = request.json.get('user_id')
    chat_id = request.json.get('chat_id')

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

        return jsonify({
            "status": 201,
            "message": "User chat recorded."
        }), 201
    except errors.lookup(UNIQUE_VIOLATION):
        return jsonify({
            'status': 409,
            'error': 'Conflict',
            'message': 'User is already present in DB.'
        }), 409
    except Exception as e:
        logger.info(e)
        conn.rollback()
        return str(e), 500
    finally:
        cursor.close()
        db_pool.putconn(conn)


@app.route('/api/user', methods=['PATCH'])
def subscribe_user():
    user_id = request.json.get('user_id')
    subscription = request.json.get('subscription')

    if not is_valid(user_id):
        return jsonify({
            'status': 400,
            'error': 'Bad Request',
            'message': 'Incorrect format for arguments'
        }), 400

    conn = db_pool.getconn()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT subscribed FROM t_users.users WHERE user_id = user_id')
        is_subscribed = cursor.fetchone()
        if is_subscribed == subscription:
            return jsonify({
                'status': 409,
                'error': 'Conflict',
                'message': 'User is already subscribed' if is_subscribed else 'User is already not subscribed'
            }), 409
        else:
            cursor.execute('UPDATE t_users.users SET subscribed = %s WHERE user_id = %s', (subscription, user_id))
            conn.commit()
            return jsonify({
                'status': 200,
                'message': 'User has subscribed' if is_subscribed else 'User has unsubscribed'
            }), 200
    except Exception as e:
        logger.info(e)
        conn.rollback()
        return str(e), 500
    finally:
        cursor.close()
        db_pool.putconn(conn)


@app.route('/api/user', methods=['PATCH'])
def unsubscribe_user():
    user_id = request.json.get('user_id')

    if not is_valid(user_id):
        return jsonify({
            'status': 400,
            'error': 'Bad Request',
            'message': 'Incorrect format for arguments'
        }), 400

    conn = db_pool.getconn()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT subscribed FROM t_users.users WHERE user_id = user_id')
        is_subscribed = cursor.fetchone()
        if is_subscribed:
            return jsonify({
                'status': 409,
                'error': 'Conflict',
                'message': 'User is already subscribed'
            }), 409

        cursor.execute('UPDATE t_users.users SET subscribed = TRUE WHERE user_id = user_id', (user_id,))
        conn.commit()

        return jsonify({
            'status': 200,
            'message': "User subscribed"
        }), 200
    except Exception as e:
        logger.info(e)
        conn.rollback()
        return str(e), 500
    finally:
        cursor.close()
        db_pool.putconn(conn)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
