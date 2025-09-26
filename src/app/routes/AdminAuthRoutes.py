from fastapi import APIRouter, HTTPException, Body, Query, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import logging

from src.config import Config
from src.models.admin import Admin
from uuid import UUID

class TokenData:
    def __init__(self, admin_id: str = None):
        self.admin_id = admin_id

router = APIRouter()

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def safe_password_hash(password: str) -> str:
    """Safely hash password by truncating to 72 bytes if necessary"""
    # Convert to bytes and truncate if longer than 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # If password is too long, hash it first to get consistent length
        password = hashlib.sha256(password_bytes).hexdigest()
    
    return pwd_context.hash(password)

def safe_password_verify(plain_password: str, hashed_password: str) -> bool:
    """Safely verify password by applying same truncation logic"""
    try:
        # Apply same truncation logic as in hashing
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            plain_password = hashlib.sha256(password_bytes).hexdigest()
        
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # If verification fails due to length, try truncating the password
        if "72 bytes" in str(e):
            truncated_password = plain_password[:72] if len(plain_password) > 72 else plain_password
            try:
                return pwd_context.verify(truncated_password, hashed_password)
            except:
                return False
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
        token_data = TokenData(admin_id=admin_id)
    except JWTError:
        raise credentials_exception
    
    session = Config.get_session()
    try:
        admin = Admin.get_by_id(session, UUID(token_data.admin_id))
        if admin is None:
            raise credentials_exception
        return admin
    finally:
        session.close()

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

async def send_verification_email(email: str, verification_token: str, name: str):
    """Send verification email to the admin"""
    try:
        smtp_server = Config.SMTP_SERVER
        smtp_port = Config.SMTP_PORT
        smtp_username = Config.SMTP_USERNAME
        smtp_password = Config.SMTP_PASSWORD
        
        base_url = Config.BASE_URL
        verification_url = f"{base_url}/api/auth/verify-email?token={verification_token}"
        
        subject = "Verify Your Admin Account"
        html_body = f"""
        <html>
        <body>
            <h2>Welcome {name}!</h2>
            <p>Thank you for signing up as an admin. Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <br>
            <p>Best regards,<br>The Admin Team</p>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = email
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
        print(f"✅ Verification email sent to {email}")
        
    except Exception as e:
        print(f"❌ Failed to send verification email: {e}")

@router.post("/signup")
async def signup(
    background_tasks: BackgroundTasks,
    name: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    session = Config.get_session()
    try:
        existing_admin = Admin.get_by_email(session, email)
        if existing_admin:
            raise HTTPException(status_code=400, detail="Email already registered")
        domain = email.split('@')[-1]
        if domain.lower() != Config.ORGANIZATION_DOMAIN.lower():
            raise HTTPException(status_code=400, detail=f"Email must belong to the {Config.ORGANIZATION_DOMAIN} domain")
        
        verification_token = generate_verification_token()
        hashed_password = safe_password_hash(password)
        
        new_admin = Admin.create(
            session=session,
            name=name,
            email=email,
            password=hashed_password,
            enabled=False,
            verification_token=verification_token
        )
        
        background_tasks.add_task(
            send_verification_email,
            email,
            verification_token,
            name
        )
        
        return {
            "message": "Admin account created successfully. Please check your email to verify your account.",
            "id": str(new_admin.id),
            "name": new_admin.name,
            "email": new_admin.email,
            "verified": False
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")
    finally:
        session.close()

@router.get("/verify-email")
async def verify_email(token: str = Query(...)):
    """Verify admin email using the verification token"""
    session = Config.get_session()
    try:
        admin = session.query(Admin).filter_by(verification_token=token).first()
        
        if not admin:
            raise HTTPException(status_code=400, detail="Invalid verification token")
        
        if admin.verified:
            return {"message": "Email already verified"}
        
        admin.verified = True
        admin.enabled = True
        admin.verification_token = None
        session.commit()
        
        return {
            "message": "Email verified successfully! Your account is now active.",
            "admin_name": admin.name,
            "verified": True
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
    finally:
        session.close()

@router.post("/resend-verification")
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    email: str = Body(..., embed=True)
):
    """Resend verification email"""
    session = Config.get_session()
    try:
        admin = Admin.get_by_email(session, email)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        if admin.verified:
            raise HTTPException(status_code=400, detail="Email already verified")
        
        verification_token = generate_verification_token()
        admin.verification_token = verification_token
        session.commit()
        
        background_tasks.add_task(
            send_verification_email,
            email,
            verification_token,
            admin.name
        )
        
        return {"message": "Verification email sent successfully"}
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to resend verification: {str(e)}")
    finally:
        session.close()

@router.post("/create/manual")
async def create_admin_manual(
    name: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    bypass_key: str = Body(..., embed=True)
):
    """Create an admin manually without email verification (for initial setup)"""
    if bypass_key != Config.BYPASS_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    if len(password) < 4: # change in production to 8
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    
    session = Config.get_session()
    try:
        existing_admin = Admin.get_by_email(session, email)
        if existing_admin:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = safe_password_hash(password)
        
        new_admin = Admin.create(
            session=session,
            name=name,
            email=email,
            password=hashed_password,
            enabled=True,
            verification_token=None  # No verification needed
        )
        
        # Manually set as verified
        new_admin.verified = True
        session.commit()
        
        return {
            "message": "Admin account created successfully.",
            "id": str(new_admin.id),
            "name": new_admin.name,
            "email": new_admin.email,
            "verified": True,
            "enabled": True
        }
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")
    finally:
        session.close()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    session = Config.get_session()
    try:        
        admin = Admin.get_by_email(session, form_data.username)
        logging.info(f"Login attempt for user: {form_data.username}")
        
        if not admin:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        # Use safe password verification to handle long passwords
        try:
            password_valid = safe_password_verify(form_data.password, admin.password)
        except Exception as e:
            logging.error(f"Password verification error for user {form_data.username}: {str(e)}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        if not admin.verified:
            raise HTTPException(status_code=400, detail="Please verify your email before logging in")
        
        if not admin.enabled:
            raise HTTPException(status_code=400, detail="Account is disabled")
        
        Admin.update_last_login(session, admin.id)
        logging.info(f"User {form_data.username} logged in successfully.")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(admin.id)}, expires_delta=access_token_expires
        )
        
        logging.info(f"Access token created for user: {form_data.username}")
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "admin_info": admin.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error for user {form_data.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    finally:
        session.close()

@router.get("/me")
async def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    """Get current admin information"""
    return current_admin.to_dict()