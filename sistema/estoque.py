import tkinter as tk
from tkinter import ttk, messagebox

from conexao import conectar


def ordenar_produtos(produtos):
    lista = list(produtos)

    for i in range(len(lista)):
        menor = i

        for j in range(i + 1, len(lista)):
            if lista[j][1].casefold() < lista[menor][1].casefold():
                menor = j

        lista[i], lista[menor] = lista[menor], lista[i]

    return lista


def abrir_estoque(janela_principal, id_usuario):
    janela = tk.Toplevel(janela_principal)
    janela.title("Controle de Estoque")
    janela.geometry("1050x620")
    janela.configure(bg="#F2F4F7")

    tk.Label(
        janela,
        text="Controle de Estoque",
        font=("Arial", 20, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(pady=15)

    formulario = tk.Frame(janela, bg="#F2F4F7")
    formulario.pack(fill="x", padx=20, pady=5)

    tk.Label(
        formulario,
        text="Produto:",
        bg="#F2F4F7"
    ).grid(row=0, column=0, padx=5, sticky="w")

    escolha_produto = ttk.Combobox(
        formulario,
        width=35,
        state="readonly"
    )
    escolha_produto.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(
        formulario,
        text="Operação:",
        bg="#F2F4F7"
    ).grid(row=0, column=1, padx=5, sticky="w")

    escolha_tipo = ttk.Combobox(
        formulario,
        values=["ENTRADA", "SAIDA"],
        state="readonly",
        width=15
    )
    escolha_tipo.grid(row=1, column=1, padx=5, pady=5)
    escolha_tipo.set("ENTRADA")

    tk.Label(
        formulario,
        text="Quantidade:",
        bg="#F2F4F7"
    ).grid(row=0, column=2, padx=5, sticky="w")

    campo_quantidade = tk.Entry(formulario, width=15)
    campo_quantidade.grid(row=1, column=2, padx=5, pady=5)

    tabela_area = tk.Frame(janela)
    tabela_area.pack(fill="both", expand=True, padx=20, pady=10)

    colunas = (
        "id", "produto", "quantidade",
        "minimo", "situacao"
    )

    tabela = ttk.Treeview(
        tabela_area,
        columns=colunas,
        show="headings",
        height=8
    )

    titulos = {
        "id": "ID",
        "produto": "Produto",
        "quantidade": "Quantidade",
        "minimo": "Estoque mínimo",
        "situacao": "Situação"
    }

    for coluna in colunas:
        tabela.heading(coluna, text=titulos[coluna])
        tabela.column(coluna, width=150, anchor="center")

    tabela.pack(fill="both", expand=True)

    tk.Label(
        janela,
        text="Histórico de movimentações",
        font=("Arial", 13, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(pady=(5, 0))

    historico = ttk.Treeview(
        janela,
        columns=(
            "data", "produto", "tipo",
            "quantidade", "responsavel"
        ),
        show="headings",
        height=6
    )

    historico_titulos = {
        "data": "Data",
        "produto": "Produto",
        "tipo": "Operação",
        "quantidade": "Quantidade",
        "responsavel": "Responsável"
    }

    for coluna in historico_titulos:
        historico.heading(coluna, text=historico_titulos[coluna])
        historico.column(coluna, width=175, anchor="center")

    historico.pack(fill="x", padx=20, pady=5)

    produtos_por_nome = {}

    def carregar_produtos():
        produtos_por_nome.clear()
        banco = conectar()

        if banco is None:
            messagebox.showerror(
                "Erro",
                "Não foi possível conectar ao banco.",
                parent=janela
            )
            return

        cursor = banco.cursor()

        try:
            cursor.execute(
                """
                SELECT id, nome, quantidade, estoque_minimo
                FROM produtos
                """
            )

            produtos = ordenar_produtos(cursor.fetchall())

            for item in escolha_produto["values"]:
                pass

            nomes = []

            for produto in produtos:
                id_produto, nome, quantidade, minimo = produto
                nomes.append(nome)
                produtos_por_nome[nome] = (
                    id_produto, quantidade, minimo
                )

                situacao = (
                    "ESTOQUE BAIXO"
                    if quantidade < minimo
                    else "Normal"
                )

                tabela.insert(
                    "",
                    "end",
                    values=(
                        id_produto,
                        nome,
                        quantidade,
                        minimo,
                        situacao
                    )
                )

            escolha_produto["values"] = nomes

            cursor.execute(
                """
                SELECT m.data_movimentacao, p.nome, m.tipo,
                       m.quantidade, u.nome
                FROM movimentacoes m
                INNER JOIN produtos p ON p.id = m.produto_id
                INNER JOIN usuarios u ON u.id = m.usuario_id
                ORDER BY m.data_movimentacao DESC, m.id DESC
                """
            )

            for movimento in cursor.fetchall():
                historico.insert("", "end", values=movimento)

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar os dados.\n{erro}",
                parent=janela
            )

        finally:
            cursor.close()
            banco.close()

    def atualizar():
        for item in tabela.get_children():
            tabela.delete(item)

        for item in historico.get_children():
            historico.delete(item)

        carregar_produtos()

    def movimentar():
        nome_produto = escolha_produto.get()
        tipo = escolha_tipo.get()
        quantidade_texto = campo_quantidade.get().strip()

        if not nome_produto or not tipo or not quantidade_texto:
            messagebox.showerror(
                "Validação",
                "Selecione o produto, a operação e a quantidade.",
                parent=janela
            )
            return

        try:
            quantidade = int(quantidade_texto)

            if quantidade <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Validação",
                "A quantidade deve ser um número inteiro positivo.",
                parent=janela
            )
            return

        if nome_produto not in produtos_por_nome:
            messagebox.showerror(
                "Erro",
                "Selecione um produto válido.",
                parent=janela
            )
            return

        id_produto, estoque_atual, minimo = (
            produtos_por_nome[nome_produto]
        )

        if tipo == "SAIDA" and quantidade > estoque_atual:
            messagebox.showerror(
                "Estoque insuficiente",
                "A quantidade de saída é maior que o estoque disponível.",
                parent=janela
            )
            return

        if tipo == "ENTRADA":
            novo_estoque = estoque_atual + quantidade
        else:
            novo_estoque = estoque_atual - quantidade

        banco = conectar()

        if banco is None:
            messagebox.showerror(
                "Erro",
                "Não foi possível conectar ao banco.",
                parent=janela
            )
            return

        cursor = banco.cursor()

        try:
            cursor.execute(
                """
                UPDATE produtos
                SET quantidade = %s
                WHERE id = %s
                """,
                (novo_estoque, id_produto)
            )

            cursor.execute(
                """
                INSERT INTO movimentacoes
                (produto_id, usuario_id, tipo, quantidade)
                VALUES (%s, %s, %s, %s)
                """,
                (id_produto, id_usuario, tipo, quantidade)
            )

            banco.commit()

            campo_quantidade.delete(0, tk.END)
            atualizar()

            if novo_estoque < minimo:
                messagebox.showwarning(
                    "Alerta de estoque baixo",
                    f"O produto {nome_produto} ficou com "
                    f"{novo_estoque} unidade(s), abaixo do mínimo "
                    f"de {minimo}.",
                    parent=janela
                )
            else:
                messagebox.showinfo(
                    "Sucesso",
                    "Movimentação registrada.",
                    parent=janela
                )

        except Exception as erro:
            banco.rollback()
            messagebox.showerror(
                "Erro",
                f"Não foi possível registrar a movimentação.\n{erro}",
                parent=janela
            )

        finally:
            cursor.close()
            banco.close()

    tk.Button(
        formulario,
        text="Registrar movimentação",
        bg="#172B4D",
        fg="white",
        command=movimentar
    ).grid(row=1, column=3, padx=10, ipady=4)

    tk.Button(
        formulario,
        text="Atualizar",
        command=atualizar
    ).grid(row=1, column=4, padx=5, ipady=4)

    carregar_produtos()