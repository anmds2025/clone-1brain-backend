import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.clerk_auth import require_clerk_identity
from app.core.config import settings
from app.core.send_mail import send_email

router = APIRouter(prefix="/auth", tags=["Auth"])

CLERK_SECRET_KEY = settings.clerk_secret_key
FRONT_END_LINK = settings.front_end_link

@router.post("/invite-member")
async def invite_member(request: Request, identity=Depends(require_clerk_identity)):
    try:
        data = await request.json()
        email = data.get("email")
        organization_id = data.get("organization_id")

        if not email or not organization_id:
            raise HTTPException(status_code=400, detail="Missing email or organization_id")

        # Gọi API Clerk backend để tạo lời mời
        clerk_url = f"https://api.clerk.com/v1/organizations/{organization_id}/invitations"
        payload = {
            "email_address": email,
            "role": "org:member",
            "redirect_url": f"{FRONT_END_LINK}/invitation",
            "send_email": True 
        }

        headers = {
            "Authorization": f"Bearer {CLERK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(clerk_url, json=payload, headers=headers)


        if response.status_code not in (200, 201):
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        result = response.json()
        
        invite_url = result.get("url", f"{FRONT_END_LINK}/invitation")  # fallback
        expires_at = result.get("expires_at")
        expires_str = ""
        if expires_at:
            try:
                from datetime import datetime
                expires_dt = datetime.fromtimestamp(int(expires_at) / 1000.0)
                expires_str = expires_dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass

        # Nội dung email HTML
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #111; line-height: 1.5;">
            <div style="max-width:600px; margin:0 auto; padding:20px; border:1px solid #ddd; border-radius:8px;">
            <h2 style="color:#2563eb;">Lời mời tham gia tổ chức</h2>
            <p>Xin chào,</p>
            <p>Bạn vừa được mời tham gia tổ chức của chúng tôi trên hệ thống. Nhấn nút bên dưới để chấp nhận lời mời và tạo tài khoản:</p>
            <div style="text-align:center; margin:30px 0;">
                <a href="{invite_url}" style="
                display:inline-block;
                padding:14px 28px;
                background-color:#2563eb;
                color:#ffffff;
                font-weight:bold;
                font-size:16px;
                text-decoration:none;
                border-radius:6px;
                ">Chấp nhận lời mời</a>
            </div>
            <p>Nếu nút trên không hoạt động, hãy sao chép và dán đường dẫn sau vào trình duyệt:</p>
            <p><a href="{invite_url}">{invite_url}</a></p>
            {f"<p>Link này sẽ hết hạn vào: <strong>{expires_str}</strong></p>" if expires_str else ""}
            <hr style="border:none; border-top:1px solid #eee; margin:20px 0;" />
            <p style="font-size:12px; color:#555;">Nếu bạn không yêu cầu lời mời này, vui lòng bỏ qua email này. Đây là email tự động, xin đừng trả lời.</p>
            </div>
        </body>
        </html>
        """

        # Gọi hàm send_email
        send_email(
            to_email=email,
            subject="Bạn được mời tham gia tổ chức",
            body_text=f"Mở link sau để chấp nhận lời mời: {invite_url}",
            body_html=body_html
        )
        
        return JSONResponse(content=result, status_code=200)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/remove-member")
async def remove_member(request: Request, identity=Depends(require_clerk_identity)):
    """
    Xóa member khỏi tổ chức Clerk.
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="Missing member_id")

        clerk_url = f"https://api.clerk.com/v1/users/{user_id}"

        headers = {
            "Authorization": f"Bearer {CLERK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.delete(clerk_url, headers=headers)

        if response.status_code not in (200, 204):
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text
            raise HTTPException(status_code=response.status_code, detail=error_detail)

        return JSONResponse(content={"message": "Member removed successfully"}, status_code=200)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
