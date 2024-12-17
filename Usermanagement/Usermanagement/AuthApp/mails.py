from .utils.email_utils import send_email_template

# Example: Send Verification Email
def send_verification_email(recipient_email):
    email_data = {
        "subject": "Email Verification - Study-Zed",
        "header": "Verify Your Email Address",
        "initial_otp": "Your OTP code",
    }
    return send_email_template(
        recipient_list=recipient_email,
        subject=email_data["subject"],
        template_name="otp",
        email_data=email_data
    )


def resend_otp_verification_email(recipient_email):
    email_data = {
        "subject": "OTP resend for Email Verification - Study-Zed",
        "header": "Verify Your Email Address",
        "initial_otp": "Your Resend OTP code",
    }
    return send_email_template(
        recipient_list=recipient_email,
        subject=email_data["subject"],
        template_name="otp",
        email_data=email_data
    )


# Example: Send Forgot Password Email
def send_forgot_password_email(recipient_email):
    email_data = {
        "subject": "Password Reset - Study-Zed",
        "header": "Reset Your Password",
    }
    return send_email_template(
        recipient_list=recipient_email,
        subject="Password Reset - Study-Zed",
        template_name="forgot_password.html",
        email_data=email_data
    )
