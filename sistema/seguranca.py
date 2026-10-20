import hashlib
import secrets
import hmac


def criar_hash(senha):
    salt = secrets.token_hex(16)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    )

    return f"pbkdf2_sha256${salt}${resultado.hex()}"


def verificar_senha(senha, senha_banco):
    partes = senha_banco.split("$")

    if len(partes) != 3 or partes[0] != "pbkdf2_sha256":
        return False

    salt = partes[1]
    hash_armazenado = partes[2]

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    )

    return hmac.compare_digest(
        resultado.hex(),
        hash_armazenado
    )