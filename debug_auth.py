#!/usr/bin/env python3
"""
Debug script to check role-based authentication issues
Run this to diagnose why super_admin routes are not accessible
"""

import sys
sys.path.append('src')

from src.config import Config
from src.models.admin import Admin, AdminRole
from src.middleware.auth_middleware import token_validator
from jose import jwt
from uuid import UUID

def debug_admin_role():
    """Debug admin roles and accounts"""
    print("=" * 50)
    print("DEBUGGING ADMIN ROLE AUTHENTICATION")
    print("=" * 50)
    
    session = Config.get_session()
    try:
        # Get all admins
        admins = Admin.get_all(session)
        print(f"\n📊 Total admins in database: {len(admins)}")
        
        for admin in admins:
            print(f"\n👤 Admin: {admin.name}")
            print(f"   📧 Email: {admin.email}")
            print(f"   🔐 Role: {admin.role} (type: {type(admin.role)})")
            print(f"   ✅ Enabled: {admin.enabled}")
            print(f"   ✔️ Verified: {admin.verified}")
            print(f"   🆔 ID: {admin.id}")
            
            # Check if this is a super admin
            if admin.role == AdminRole.super_admin:
                print(f"   🌟 THIS IS A SUPER ADMIN!")
                print(f"   🔍 Role comparison: {admin.role} == {AdminRole.super_admin} = {admin.role == AdminRole.super_admin}")
                print(f"   🔍 Role value: '{admin.role.value}' vs 'super_admin'")
            else:
                print(f"   ⚠️  Not a super admin. Role: {admin.role.value}")
    
    finally:
        session.close()

def debug_token(token_string=None):
    """Debug token validation"""
    print("\n" + "=" * 50)
    print("DEBUGGING TOKEN VALIDATION")
    print("=" * 50)
    
    if not token_string:
        print("❌ No token provided for debugging")
        return
    
    try:
        # Validate token using the middleware
        payload = token_validator.validate_token(token_string)
        print(f"✅ Token is valid!")
        print(f"🆔 Admin ID from token: {payload['admin_id']}")
        
        # Get admin from database
        session = Config.get_session()
        try:
            admin = Admin.get_by_id(session, UUID(payload['admin_id']))
            if admin:
                print(f"✅ Admin found in database!")
                print(f"👤 Name: {admin.name}")
                print(f"📧 Email: {admin.email}")
                print(f"🔐 Role: {admin.role} (value: {admin.role.value})")
                print(f"✅ Enabled: {admin.enabled}")
                print(f"✔️ Verified: {admin.verified}")
                
                # Test role check
                if admin.role == AdminRole.super_admin:
                    print(f"🌟 ROLE CHECK PASSED: This admin IS a super_admin!")
                else:
                    print(f"❌ ROLE CHECK FAILED: This admin is NOT a super_admin")
                    print(f"   Current role: {admin.role.value}")
                    print(f"   Expected role: super_admin")
            else:
                print(f"❌ Admin not found in database with ID: {payload['admin_id']}")
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Token validation failed: {e}")

def debug_enum_values():
    """Debug AdminRole enum values"""
    print("\n" + "=" * 50)
    print("DEBUGGING ADMINROLE ENUM")
    print("=" * 50)
    
    print("Available AdminRole values:")
    for role in AdminRole:
        print(f"  - {role.name}: '{role.value}'")
    
    print(f"\nSuper admin enum: {AdminRole.super_admin}")
    print(f"Super admin value: '{AdminRole.super_admin.value}'")

if __name__ == "__main__":
    print("🔍 Starting authentication debug session...\n")
    
    # Debug enum values
    debug_enum_values()
    
    # Debug admin accounts
    debug_admin_role()
    
    # Ask for token if needed
    print("\n" + "=" * 50)
    print("TOKEN DEBUGGING")
    print("=" * 50)
    print("To debug your specific token:")
    print("1. Login to get your JWT token")
    print("2. Copy the token (without 'Bearer ' prefix)")
    print("3. Run: python debug_auth.py <your_token>")
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
        debug_token(token)
    else:
        print("\n💡 No token provided. Run with token as argument to debug specific authentication.")
    
    print(f"\n🏁 Debug session complete!")
