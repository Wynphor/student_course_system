# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import hashlib
import hmac
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import os


# 说明：给 ITERATIONS 赋值，保存当前步骤需要继续使用的数据。
ITERATIONS = 120_000


# 说明：根据明文密码生成带盐 PBKDF2 哈希，避免数据库保存明文密码。
def hash_password(password: str, salt: bytes | None = None) -> str:
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if salt is None:
        # 说明：生成随机盐值，使相同密码也会得到不同哈希值。
        salt = os.urandom(16)
    # 使用标准库 PBKDF2 保存“算法+迭代次数+盐+摘要”，数据库中不保存明文密码。
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    # 说明：返回处理结果，供调用方继续使用。
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


# 说明：校验用户输入密码是否与数据库保存的哈希值匹配。
def verify_password(password: str, stored_hash: str) -> bool:
    # 说明：开始异常捕获，避免底层错误直接中断程序。
    try:
        # 说明：给 algorithm, iterations_text, salt_hex, digest_hex 赋值，保存当前步骤需要继续使用的数据。
        algorithm, iterations_text, salt_hex, digest_hex = stored_hash.split("$", 3)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if algorithm != "pbkdf2_sha256":
            # 说明：返回处理结果，供调用方继续使用。
            return False
        # 说明：给 iterations 赋值，保存当前步骤需要继续使用的数据。
        iterations = int(iterations_text)
        # 说明：给 salt 赋值，保存当前步骤需要继续使用的数据。
        salt = bytes.fromhex(salt_hex)
        # 说明：给 expected 赋值，保存当前步骤需要继续使用的数据。
        expected = bytes.fromhex(digest_hex)
    # 说明：捕获异常并转换为业务提示或测试结果。
    except ValueError:
        # 说明：返回处理结果，供调用方继续使用。
        return False
    # 说明：使用 PBKDF2-HMAC-SHA256 计算密码摘要。
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    # compare_digest 可避免普通字符串比较带来的时序差异。
    return hmac.compare_digest(digest, expected)
