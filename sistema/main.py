import tkinter as tk
from tkinter import messagebox


def abrir_menu(id_usuario, nome_usuario):
    janela = tk.Tk()
    janela.title("Sistema de Gestão de Estoque")
    janela.geometry("650x470")
    janela.resizable(False, False)
    janela.configure(bg="#F2F4F7")

    def abrir_produtos():
        import produtos
        produtos.abrir_produtos(janela)

    def abrir_estoque():
        import estoque
        estoque.abrir_estoque(janela, id_usuario)

    def sair():
        if messagebox.askyesno(
            "Sair",
            "Deseja sair do sistema?",
            parent=janela
        ):
            janela.destroy()

            import login
            login.iniciar_login()

    janela.protocol("WM_DELETE_WINDOW", sair)

    tk.Label(
        janela,
        text="GESTÃO DE ESTOQUE",
        font=("Arial", 22, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(pady=(40, 10))

    tk.Label(
        janela,
        text=f"Bem-vindo(a), {nome_usuario}!",
        font=("Arial", 13),
        bg="#F2F4F7",
        fg="#596579"
    ).pack(pady=(0, 30))

    tk.Button(
        janela,
        text="Cadastro de Produtos",
        font=("Arial", 12, "bold"),
        bg="#172B4D",
        fg="white",
        width=28,
        relief="flat",
        command=abrir_produtos
    ).pack(pady=10, ipady=9)

    tk.Button(
        janela,
        text="Controle de Estoque",
        font=("Arial", 12, "bold"),
        bg="#263F68",
        fg="white",
        width=28,
        relief="flat",
        command=abrir_estoque
    ).pack(pady=10, ipady=9)

    tk.Button(
        janela,
        text="Sair",
        font=("Arial", 10),
        width=15,
        command=sair
    ).pack(pady=25)

    janela.mainloop()