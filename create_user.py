#!/usr/bin/env python3
import os
import sys
from airflow.auth.managers.fab.models import User
from airflow.utils.db import provide_session
from airflow import settings

@provide_session
def create_admin_user(session=None):
    """Create admin user if it doesn't exist"""
    try:
        username = os.environ.get('AIRFLOW_ADMIN_USERNAME', 'admin')
        password = os.environ.get('AIRFLOW_ADMIN_PASSWORD', 'admin')
        email = os.environ.get('AIRFLOW_ADMIN_EMAIL', 'admin@example.com')
        
        existing_user = session.query(User).filter(User.username == username).first()
        if not existing_user:
            user = User(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User',
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            session.add(user)
            session.commit()
            print(f'Admin user "{username}" created successfully')
        else:
            print(f'Admin user "{username}" already exists')
        return True
    except Exception as e:
        print(f'Error creating admin user: {e}')
        return False

if __name__ == '__main__':
    success = create_admin_user()
    sys.exit(0 if success else 1)
