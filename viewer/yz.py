import bcrypt

def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_password.decode()

# 假设用户输入的密码
password = "159756"

# 生成哈希密码
hashed_password = hash_password(password)

# 打印哈希密码
print("哈希密码:", hashed_password)


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# 假设用户输入的密码
password = "159756"

# 验证密码
if check_password(password, hashed_password):
    print("密码正确")
else:
    print("密码错误")
