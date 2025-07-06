"""
Utility functions for Opera Panel
"""
import os
from fastapi import Request

def get_full_profile_photo_url(profile_photo: str) -> str:
    """
    Convert relative profile photo path to full URL pointing to Stardust server
    """
    if not profile_photo:
        return '/static/avatar-default.png'
    
    # If it's already a full URL, return as is
    if profile_photo.startswith('http'):
        return profile_photo
    
    # If it's a relative path starting with /static, prepend the Stardust server URL
    if profile_photo.startswith('/static'):
        stardust_base_url = os.getenv('STARDUST_API_BASE_URL', 'https://stardust.my-firstcare.com')
        return f"{stardust_base_url}{profile_photo}"
    
    # Default fallback
    return '/static/avatar-default.png'

def get_user_language(request: Request) -> str:
    """
    Detect user language from URL parameter, session, or Accept-Language header
    """
    # Check URL parameter first
    lang_param = request.query_params.get('lang', '').lower()
    if lang_param in ['th', 'en']:
        return lang_param
    
    # Check session (future enhancement)
    # session_lang = request.session.get('language', '').lower()
    # if session_lang in ['th', 'en']:
    #     return session_lang
    
    # Check Accept-Language header
    accept_language = request.headers.get('Accept-Language', '')
    if 'th' in accept_language.lower():
        return 'th'
    
    # Default to English
    return 'en'

def get_copyright_text(language: str) -> str:
    """
    Get copyright text based on language
    """
    if language == 'th':
        return "สงวนลิขสิทธิ์ © 2025 บริษัท อะเมดิคอล ฟอร์ ยู จำกัด กรุงเทพฯ ประเทศไทย"
    else:
        return "Copyright © 2023-2025 A Medical For You Co., Ltd. Bangkok Thailand"

def get_mfc_logo(language: str) -> str:
    """
    Get My FirstCare logo based on language
    """
    if language == 'th':
        return "/static/LOGO_MFC_TH.png"
    else:
        return "/static/LOGO_MFC_EN.png"