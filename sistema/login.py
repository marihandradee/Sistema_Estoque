import tkinter as tk
from tkinter import messagebox

from conexao import conectar
from seguranca import verificar_senha


def iniciar_login():
    janela = tk.Tk()
    janela.title("Sistema de Gestão de Estoque")
    janela.geometry("420x380")
    janela.resizable(False, False)
    janela.configure(bg="#F2F4F7")

    def fazer_login(evento=None):
        usuario = campo_usuario.get().strip()
        senha = campo_senha.get()

        if not usuario or not senha:
            messagebox.showerror(
                "Atenção",
                "Preencha o usuário e a senha.",
                parent=janela
            )
            return

        banco = conectar()

        if banco is None:
            messagebox.showerror(
                "Erro",
                "Não foi possível conectar ao banco de dados.",
                parent=janela
            )
            return

        cursor = banco.cursor()

        try:
            cursor.execute(
                """
                SELECT id, nome, senha
                FROM usuarios
                WHERE usuario = %s
                """,
                (usuario,)
            )

            resultado = cursor.fetchone()

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível consultar o usuário.\n{erro}",
                parent=janela
            )
            return

        finally:
            cursor.close()
            banco.close()

        if resultado and verificar_senha(senha, resultado[2]):
            id_usuario = resultado[0]
            nome_usuario = resultado[1]

            janela.destroy()

            import main
            main.abrir_menu(id_usuario, nome_usuario)

        else:
            messagebox.showerror(
                "Login inválido",
                "Usuário ou senha incorretos.",
                parent=janela
            )

            campo_senha.delete(0, tk.END)
            campo_senha.focus()

    tk.Label(
        janela,
        text="GESTÃO DE ESTOQUE",
        font=("Arial", 20, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(pady=(35, 8))

    tk.Label(
        janela,
        text="Entre com seus dados para continuar",
        font=("Arial", 10),
        bg="#F2F4F7",
        fg="#596579"
    ).pack(pady=(0, 22))

    tk.Label(
        janela,
        text="Usuário",
        font=("Arial", 10, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(anchor="w", padx=65)

    campo_usuario = tk.Entry(
        janela,
        font=("Arial", 12),
        width=30
    )
    campo_usuario.pack(pady=(5, 12), ipady=5)

    tk.Label(
        janela,
        text="Senha",
        font=("Arial", 10, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(anchor="w", padx=65)

    campo_senha = tk.Entry(
        janela,
        font=("Arial", 12),
        width=30,
        show="*"
    )
    campo_senha.pack(pady=(5, 18), ipady=5)

    tk.Button(
        janela,
        text="ENTRAR",
        font=("Arial", 11, "bold"),
        bg="#172B4D",
        fg="white",
        activebackground="#263F68",
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        command=fazer_login
    ).pack(fill="x", padx=65, ipady=7)

    janela.bind("<Return>", fazer_login)
    campo_usuario.focus()

    janela.mainloop()


if __name__ == "__main__":
    iniciar_login()