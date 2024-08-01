import pytest
from flask import url_for


def test_register(client):
    response = client.post('/auth/register', data={'email': 'test@example.com'})
    assert response.status_code == 302  # Redirect status code
    assert b'OTP sent to your email. Please check your email.' in response.data


def test_verify_otp(client, mocker):
    mocker.patch('api.auth_apis.generate_and_store_otp', return_value=123456)
    mocker.patch('api.auth_apis.send_otp_email')

    client.post('/auth/register', data={'email': 'test@example.com'})

    response = client.post('/auth/verify_otp', data={'otp': '123456'})
    assert response.status_code == 200
    assert b'Login successful!' in response.data


def test_protected_endpoint(client, mocker):
    mocker.patch('flask_jwt_extended.create_access_token', return_value='fake-token')

    client.post('/auth/register', data={'email': 'test@example.com'})
    client.post('/auth/verify_otp', data={'otp': '123456'})

    response = client.get('/auth/protected', headers={'Authorization': 'Bearer fake-token'})
    assert response.status_code == 200
    assert b'logged_in_as' in response.data


def test_post_data(client):
    response = client.post('/api/post')
    assert response.data == b'Data added successfully'


def test_get_data(client):
    response = client.get('/api/get')
    assert response.status_code == 200
    assert b'Likhitha' in response.data
