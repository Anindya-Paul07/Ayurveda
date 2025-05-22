"""
Email Utilities

This module provides functions for sending emails using Flask-Mail.
"""

from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from ..extensions import mail
import os

def send_async_email(app, msg):
    """Send an email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """
    Send an email using a template.
    
    Args:
        to (str): Recipient email address
        subject (str): Email subject
        template (str): Template name (without .html extension)
        **kwargs: Variables to pass to the template
    """
    app = current_app._get_current_object()
    
    # Render email templates
    html_body = render_template(f'emails/{template}.html', **kwargs)
    text_body = render_template(f'emails/{template}.txt', **kwargs)
    
    msg = Message(
        subject=subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to],
        html=html_body,
        body=text_body
    )
    
    # Send email asynchronously in production
    if not app.config.get('TESTING'):
        Thread(target=send_async_email, args=(app, msg)).start()
    else:
        # For testing, send synchronously
        mail.send(msg)
    
    return msg

def send_verification_email(user):
    """Send a verification email to the user."""
    token = user.generate_confirmation_token()
    verify_url = f"{current_app.config['FRONTEND_URL']}/verify-email/{token}"
    
    return send_email(
        to=user.email,
        subject="Verify Your Email Address",
        template='verify_email',
        username=user.username,
        verify_url=verify_url
    )

def send_password_reset_email(user):
    """Send a password reset email to the user."""
    token = user.generate_reset_token()
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"
    
    return send_email(
        to=user.email,
        subject="Reset Your Password",
        template='reset_password',
        username=user.username,
        reset_url=reset_url
    )

def send_welcome_email(user):
    """Send a welcome email to a new user."""
    return send_email(
        to=user.email,
        subject="Welcome to Our App!",
        template='welcome',
        username=user.username
    )

def send_notification_email(user, subject, message):
    """Send a notification email to a user."""
    return send_email(
        to=user.email,
        subject=subject,
        template='notification',
        username=user.username,
        message=message
    )
