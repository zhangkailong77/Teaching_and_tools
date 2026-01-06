from hashids import Hashids

# 盐值：随便写一串复杂的字符，这是你的加密密钥
SALT = "teaching_platform_super_secret_salt_2025"
MIN_LENGTH = 8 # 生成字符串的最小长度

hasher = Hashids(salt=SALT, min_length=MIN_LENGTH)

def encode_id(id: int) -> str:
    """把数字 6 变成字符串 'Nk7X9d'"""
    return hasher.encode(id)

def decode_id(hash_str: str) -> int:
    """把字符串 'Nk7X9d' 变回数字 6"""
    decoded = hasher.decode(hash_str)
    if not decoded:
        return None
    return decoded[0]