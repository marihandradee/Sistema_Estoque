from conexao import conectar
from seguranca import criar_hash


def configurar():
    banco = conectar()

    if banco is None:
        print("Não foi possível conectar ao MySQL.")
        return

    cursor = banco.cursor()

    try:
        cursor.execute(
            "SELECT id, senha FROM usuarios WHERE usuario = %s",
            ("maria",)
        )

        usuario = cursor.fetchone()

        if usuario:
            if not usuario[1].startswith("pbkdf2_sha256$"):
                senha_hash = criar_hash("senha_temporaria")

                cursor.execute(
                    "UPDATE usuarios SET senha = %s WHERE id = %s",
                    (senha_hash, usuario[0])
                )

                print("Senha de teste protegida com hash.")
            else:
                print("Usuário maria já está configurado.")
        else:
            senha_hash = criar_hash("senha_temporaria")

            cursor.execute(
                """
                INSERT INTO usuarios (nome, usuario, senha)
                VALUES (%s, %s, %s)
                """,
                ("Maria Eduarda", "maria", senha_hash)
            )

            print("Usuário de teste criado.")

        banco.commit()
        print("Configuração concluída.")

    except Exception as erro:
        banco.rollback()
        print("Erro ao configurar usuário:", erro)

    finally:
        cursor.close()
        banco.close()


if __name__ == "__main__":
    configurar()