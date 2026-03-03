"""
File: auth_service.py
Author: 양창일
Created: 2026-02-15
Description: 로그인과 토큰을 실제로 처리하는 코드

Modification History:
<<<<<<< HEAD
- 2026-02-15 (양창일): 초기 생성 (로그인, JWT 토큰 관리 로직)
- 2026-02-21 (김지우): 비밀번호 찾기 (이메일 인증, 비밀번호 업데이트) SQLAlchemy 통합
- 2026-02-22 (양창일): username 혼동으로 email, name으로 정리, 소셜 로그인 수정
=======
- 2026-02-15: 초기 생성
>>>>>>> 3266b1e9f74b438985b9c6640f00b53ce80b4111
"""

from sqlalchemy.orm import Session  # 세션
from datetime import datetime, timezone, timedelta  # 시간
from backend.models.user import User  # 유저
from backend.models.refresh_token import RefreshToken  # 리프레시 저장
from backend.core.security import (
    hash_password, verify_password, new_jti, sha256_hex,
    create_access_token, create_refresh_token, decode_token
)  # 보안 유틸
from backend.core.config import settings  # 설정

<<<<<<< HEAD
load_dotenv(override=True)

# 이메일 발송 환경변수
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


# ==========================================
# 1. 회원가입 및 로그인 (기존 코드 유지)
# ==========================================
def signup(db: Session, email: str, password: str, name: str | None = None) -> None:
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise ValueError("invalid credentials")
    user = User(email=email, name=name, password=hash_password(password))
    db.add(user)
    db.commit()

def login(db: Session, email: str, password: str) -> tuple[str, str, str]:
    user = db.query(User).filter(User.email == email).first()
=======
def signup(db: Session, username: str, password: str) -> None:
    exists = db.query(User).filter(User.username == username).first()  # 중복 확인
    if exists:
        raise ValueError("invalid credentials")  # 계정열거 방지용 동일 메세지
    user = User(username=username, password_hash=hash_password(password))  # 유저 생성
    db.add(user)  # 추가
    db.commit()  # 커밋

def login(db: Session, username: str, password: str) -> tuple[str, str, str]:
    user = db.query(User).filter(User.username == username).first()  # 유저 조회
>>>>>>> 3266b1e9f74b438985b9c6640f00b53ce80b4111

    # 소셜 유저(password_hash=None)는 로컬 로그인 불가
    if (not user) or (not user.password_hash) or (not verify_password(password, user.password_hash)):  # 검증
        raise ValueError("invalid credentials")  # 동일 응답(계정열거 방지)

    access = create_access_token(sub=str(user.id))  # access 발급
    jti = new_jti()  # refresh id
    refresh = create_refresh_token(sub=str(user.id), jti=jti)  # refresh 발급

    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    row = RefreshToken(user_id=user.id, jti=jti, token_hash=sha256_hex(refresh), expires_at=exp)  # DB 저장(해시)
    db.add(row)  # 추가
    db.commit()  # 커밋

    return access, refresh, str(user.id)  # 반환


def rotate_refresh(db: Session, refresh_token: str) -> tuple[str, str]:
    payload = decode_token(refresh_token)  # 검증
    user_id = int(payload.get("sub"))  # 소유자
    jti = payload.get("jti")  # 토큰 ID
    if not jti:
        raise ValueError("invalid token")  # 실패

    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()  # DB 조회
    if (not row) or (row.revoked_at is not None):  # 없거나 폐기됨
        raise ValueError("invalid token")  # 실패
    if row.token_hash != sha256_hex(refresh_token):  # 토큰 불일치(탈취/재사용)
        raise ValueError("invalid token")  # 실패
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):  # 만료
        raise ValueError("invalid token")  # 실패

    row.revoked_at = datetime.now(timezone.utc)  # 기존 refresh 폐기(회전)
    db.add(row)  # 반영

    new_access = create_access_token(sub=str(user_id))  # 새 access
    new_jti = new_jti()  # 새 jti
    new_refresh = create_refresh_token(sub=str(user_id), jti=new_jti)  # 새 refresh

    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    db.add(RefreshToken(user_id=user_id, jti=new_jti, token_hash=sha256_hex(new_refresh), expires_at=exp))  # 저장
    db.commit()  # 커밋

    return new_access, new_refresh  # 반환

def revoke_refresh(db: Session, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)  # 디코드
        jti = payload.get("jti")  # jti
    except Exception:
        return  # 토큰이 이미 이상하면 그냥 무시(정보노출 방지)

    if not jti:
        return  # 없음

    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()  # 조회
    if row and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)  # 폐기
        db.add(row)  # 반영
        db.commit()  # 커밋

def get_user_from_access(db: Session, access_token: str) -> User:
    payload = decode_token(access_token)  # 검증
    sub = payload.get("sub")  # user id
    if not sub:
        raise ValueError("invalid token")  # 실패
    user = db.query(User).filter(User.id == int(sub)).first()  # 유저 조회
    if not user:
        raise ValueError("invalid token")  # 실패
    return user  # 반환

def issue_tokens_for_user_id(db: Session, user_id: int) -> tuple[str, str]:
    access = create_access_token(sub=str(user_id))  # access 발급
    jti = new_jti()  # refresh jti
    refresh = create_refresh_token(sub=str(user_id), jti=jti)  # refresh 발급

    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_DAYS)  # 만료
    row = RefreshToken(user_id=user_id, jti=jti, token_hash=sha256_hex(refresh), expires_at=exp)  # DB 저장
    db.add(row)  # 추가
    db.commit()  # 커밋

<<<<<<< HEAD
    return access, refresh  


# ==========================================
# 3. 비밀번호 찾기 & 변경 (🔥 SQLAlchemy ORM 통합)
# ==========================================
def check_user_exists(db: Session, email: str) -> bool:
    """이메일 기반 유저 존재 여부 확인"""
    user = db.query(User).filter(User.email == email).first()
    return user is not None

def send_auth_email(receiver_email: str, auth_code: str) -> tuple[bool, str]:
    """SMTP 기반 인증 이메일 발송"""
    if not SENDER_EMAIL or not APP_PASSWORD:
        return False, "서버의 이메일 설정이 누락되었습니다."
        
    subject = "[보안] 비밀번호 재설정 인증 코드 안내"
    body = f"""
    <html>
    <body style="font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 500px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #222;">코드를 입력하고 비밀번호를 재설정하세요</h2>
        <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
            <h1 style="color: #bb38d0; letter-spacing: 8px; margin: 0; font-size: 32px;">{auth_code}</h1>
        </div>
        <p style="font-size: 14px; color: #555;">화면에 위 코드를 입력하세요. 코드는 15분 뒤 만료됩니다.</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, "성공"
    except Exception as e:
        return False, f"이메일 발송 실패: {str(e)}"

def update_password(db: Session, email: str, new_raw_password: str) -> tuple[bool, str]:
    """새로운 비밀번호를 암호화하여 DB 업데이트 (ORM 활용)"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "가입되지 않은 이메일입니다."

        user.password = hash_password(new_raw_password)
        db.commit()
        return True, "성공"
    except Exception as e:
        db.rollback()
        return False, f"비밀번호 업데이트 오류: {str(e)}"
=======
    return access, refresh  # 반환
>>>>>>> 3266b1e9f74b438985b9c6640f00b53ce80b4111
