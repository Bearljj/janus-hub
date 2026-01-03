import secrets
import string

async def execute(parameters, context):
    length = int(parameters.get('length', 16))
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()'
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return f"🔐 **安全密钥已生成 (64位加强版)**\n\n密钥: `{password}`\n\n*警告：请妥善保存。*"