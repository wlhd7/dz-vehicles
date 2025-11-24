import pytest
from vehicles import create_app
from vehicles.db import get_db, init_database

@pytest.fixture
def app():
    import tempfile, os
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    db_path = tf.name
    app = create_app({'TESTING': True, 'DATABASE': db_path, 'SECRET_KEY': 'test-key'})
    with app.app_context():
        init_database()
        db = get_db()
        # create a test user
        db.execute("INSERT INTO users (username, password, is_identified) VALUES (?, ?, ?)", ('tester', 'x', 1))
        # create entries for vehicle and gas card
        db.execute("INSERT INTO vehicles (plate, insurance, inspection, maintenance, mileage, status) VALUES (?, ?, ?, ?, ?, ?)",
                   ('ABC123', '', '', '', '1000', 'returned'))
        db.execute("INSERT INTO gas_cards (card_number, balance, status) VALUES (?, ?, ?)", ('GC100', 0.0, 'returned'))
        db.commit()
    yield app
    # cleanup temp db file
    try:
        os.unlink(db_path)
    except Exception:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

def login_as(client, app):
    # set session user_id to tester
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', ('tester',)).fetchone()
        uid = user['id']
    with client.session_transaction() as sess:
        sess['user_id'] = uid

def test_take_and_return_vehicle(client, app):
    login_as(client, app)
    # take vehicle
    resp = client.post('/lock/submit', data={'vehicle': 'ABC123'}, follow_redirects=True)
    # ensure vehicle status changed to taken
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        assert v['status'] == 'taken'
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        assert v['status'] == 'taken'
        # now return vehicle
    resp = client.post('/lock/submit', data={'vehicle': 'ABC123', 'mileage': '1100'}, follow_redirects=True)
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        assert v['status'] == 'returned'
        assert v['mileage'] == '1100'
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        assert v['status'] == 'returned'
        assert v['mileage'] == '1100'

def test_take_both_partial_return_forbidden(client, app):
    login_as(client, app)
    # take both
    resp = client.post('/lock/submit', data={'vehicle': 'ABC123', 'gasCard': 'GC100'}, follow_redirects=True)
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        g = db.execute('SELECT * FROM gas_cards WHERE card_number = ?', ('GC100',)).fetchone()
        assert v['status'] == 'taken'
        assert g['status'] == 'taken'
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        g = db.execute('SELECT * FROM gas_cards WHERE card_number = ?', ('GC100',)).fetchone()
        assert v['status'] == 'taken'
        assert g['status'] == 'taken'
    # attempt partial return (vehicle only) - should be blocked
    resp = client.post('/lock/submit', data={'vehicle': 'ABC123', 'mileage': '1200'}, follow_redirects=True)
    # expect flash message about paired return; page should not show new password
    text = resp.get_data(as_text=True)
    assert ('必须同时归还' in text) or ('必须同时' in text) or ('归还' in text)
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        g = db.execute('SELECT * FROM gas_cards WHERE card_number = ?', ('GC100',)).fetchone()
        assert v['status'] == 'taken'
        assert g['status'] == 'taken'

def test_return_both_success(client, app):
    login_as(client, app)
    # take both
    resp = client.post('/lock/submit', data={'vehicle': 'ABC123', 'gasCard': 'GC100'}, follow_redirects=True)
    assert '临时密码' in resp.get_data(as_text=True)
    # return both
    resp = client.post('/lock/submit', data={'vehicle': 'ABC123', 'gasCard': 'GC100', 'mileage': '1300', 'balance': '50'}, follow_redirects=True)
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        g = db.execute('SELECT * FROM gas_cards WHERE card_number = ?', ('GC100',)).fetchone()
        assert v['status'] == 'returned'
        assert g['status'] == 'returned'
        assert v['mileage'] == '1300'
        assert float(g['balance']) == 50.0
    with app.app_context():
        db = get_db()
        v = db.execute('SELECT * FROM vehicles WHERE plate = ?', ('ABC123',)).fetchone()
        g = db.execute('SELECT * FROM gas_cards WHERE card_number = ?', ('GC100',)).fetchone()
        assert v['status'] == 'returned'
        assert g['status'] == 'returned'
        assert v['mileage'] == '1300'
        assert float(g['balance']) == 50.0
