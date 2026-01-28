#!/usr/bin/env python
"""
Helper script to create/manage admin users for Qwik Admin Panel
Usage:
    python create_admin.py <username> <email> <password>
    python create_admin.py --make-admin <username>
    python create_admin.py --list
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qwik.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin(username, email, password):
    """Create a new admin user"""
    try:
        if User.objects.filter(username=username).exists():
            print(f"❌ User '{username}' already exists!")
            return False
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: admin")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def make_admin(username):
    """Convert existing user to admin"""
    try:
        user = User.objects.get(username=username)
        # user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ User '{username}' is now an admin!")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_admins():
    """List all admin users"""
    admins = User.objects.filter(role='admin').values('id', 'username', 'email', 'is_active')
    
    if not admins.exists():
        print("No admin users found.")
        return
    
    print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Status':<10}")
    print("-" * 70)
    for admin in admins:
        status = "🟢 Active" if admin['is_active'] else "🔴 Banned"
        print(f"{admin['id']:<5} {admin['username']:<20} {admin['email']:<30} {status:<10}")
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == '--list':
        list_admins()
    elif command == '--make-admin':
        if len(sys.argv) < 3:
            print("Usage: python create_admin.py --make-admin <username>")
            return
        make_admin(sys.argv[2])
    else:
        # Create new admin
        if len(sys.argv) < 4:
            print("Usage: python create_admin.py <username> <email> <password>")
            return
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
