"""Platform package exports."""

from app.platforms.base import BasePlatform
from app.platforms.google import GooglePlatform
from app.platforms.linkedin import LinkedInPlatform
from app.platforms.x_platform import XPlatform
from app.platforms.youtube import YouTubePlatform
from app.platforms.instagram import InstagramPlatform
from app.platforms.facebook import FacebookPlatform
from app.platforms.threads import ThreadsPlatform
from app.platforms.whatsapp import WhatsAppPlatform
from app.platforms.email import EmailPlatform

PLATFORMS = [
    GooglePlatform(),
    LinkedInPlatform(),
    XPlatform(),
    YouTubePlatform(),
    InstagramPlatform(),
    FacebookPlatform(),
    ThreadsPlatform(),
    WhatsAppPlatform(),
    EmailPlatform(),
]

__all__ = [
    "BasePlatform",
    "GooglePlatform",
    "LinkedInPlatform",
    "XPlatform",
    "YouTubePlatform",
    "InstagramPlatform",
    "FacebookPlatform",
    "ThreadsPlatform",
    "WhatsAppPlatform",
    "EmailPlatform",
    "PLATFORMS",
]