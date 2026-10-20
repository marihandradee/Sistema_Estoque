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


def abrir_produtos(janela_principal):
    janela = tk.Toplevel(janela_principal)
    janela.title("Cadastro de Produtos")
    janela.geometry("1050x600")
    janela.configure(bg="#F2F4F7")

    selecionado = {"id": None}

    tk.Label(
        janela,
        text="Cadastro de Produtos",
        font=("Arial", 20, "bold"),
        bg="#F2F4F7",
        fg="#172B4D"
    ).pack(pady=15)

    area = tk.Frame(janela, bg="#F2F4F7")
    area.pack(fill="x", padx=20)

    tk.Label(area, text="Pesquisar produto:", bg="#F2F4F7").grid(
        row=0, column=0, sticky="w"
    )

    campo_busca = tk.Entry(area, width=35)
    campo_busca.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")

    tabela_area = tk.Frame(janela)
    tabela_area.pack(fill="both", expand=True, padx=20, pady=10)

    colunas = (
        "id", "nome", "tamanho", "peso",
        "material", "quantidade", "minimo"
    )

    tabela = ttk.Treeview(
        tabela_area,
        columns=colunas,
        show="headings",
        height=13
    )

    titulos = {
        "id": "ID",
        "nome": "Produto",
        "tamanho": "Tamanho",
        "peso": "Peso",
        "material": "Material",
        "quantidade": "Quantidade",
        "minimo": "Estoque mínimo"
    }

    larguras = {
        "id": 45,
        "nome": 180,
        "tamanho": 100,
        "peso": 80,
        "material": 180,
        "quantidade": 100,
        "minimo": 110
    }

    for coluna in colunas:
        tabela.heading(coluna, text=titulos[coluna])
        tabela.column(coluna, width=larguras[coluna], anchor="center")

    barra = ttk.Scrollbar(
        tabela_area,
        orient="vertical",
        command=tabela.yview
    )

    tabela.configure(yscrollcommand=barra.set)
    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")

    def carregar_produtos():
        for item in tabela.get_children():
            tabela.delete(item)

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
                SELECT id, nome, tamanho, peso, material,
                       quantidade, estoque_minimo
                FROM produtos
                """
            )

            produtos = ordenar_produtos(cursor.fetchall())
            busca = campo_busca.get().strip().casefold()

            for produto in produtos:
                if busca in produto[1].casefold():
                    tabela.insert("", "end", values=produto)

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar os produtos.\n{erro}",
                parent=janela
            )

        finally:
            cursor.close()
            banco.close()

    def selecionar_produto(evento=None):
        selecao = tabela.selection()

        if not selecao:
            selecionado["id"] = None
            return

        valores = tabela.item(selecao[0], "values")
        selecionado["id"] = int(valores[0])

    tabela.bind("<<TreeviewSelect>>", selecionar_produto)

    def formulario(id_produto=None):
        dados = None

        if id_produto is not None:
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
                    SELECT nome, tamanho, peso, material,
                           quantidade, estoque_minimo
                    FROM produtos
                    WHERE id = %s
                    """,
                    (id_produto,)
                )
                dados = cursor.fetchone()

            finally:
                cursor.close()
                banco.close()

            if dados is None:
                messagebox.showerror(
                    "Erro",
                    "Produto não encontrado.",
                    parent=janela
                )
                return

        tela = tk.Toplevel(janela)
        tela.title("Editar Produto" if dados else "Novo Produto")
        tela.geometry("400x500")
        tela.configure(bg="#F2F4F7")
        tela.transient(janela)
        tela.grab_set()

        campos = [
            ("Nome", ""),
            ("Tamanho", ""),
            ("Peso (kg)", ""),
            ("Material", ""),
            ("Quantidade", "0"),
            ("Estoque mínimo", "0")
        ]

        entradas = []

        for indice, (rotulo, valor_padrao) in enumerate(campos):
            tk.Label(
                tela,
                text=rotulo,
                bg="#F2F4F7",
                fg="#172B4D"
            ).pack(anchor="w", padx=25, pady=(8, 0))

            entrada = tk.Entry(tela, font=("Arial", 11))
            entrada.pack(fill="x", padx=25, pady=3, ipady=3)

            if dados:
                entrada.insert(0, str(dados[indice]))
            else:
                entrada.insert(0, valor_padrao)

            entradas.append(entrada)

        def salvar():
            nome = entradas[0].get().strip()
            tamanho = entradas[1].get().strip()
            peso_texto = entradas[2].get().strip().replace(",", ".")
            material = entradas[3].get().strip()
            quantidade_texto = entradas[4].get().strip()
            minimo_texto = entradas[5].get().strip()

            if not nome or not tamanho or not material:
                messagebox.showerror(
                    "Validação",
                    "Preencha nome, tamanho e material.",
                    parent=tela
                )
                return

            try:
                peso = float(peso_texto)
                quantidade = int(quantidade_texto)
                minimo = int(minimo_texto)

                if peso <= 0 or quantidade < 0 or minimo < 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Validação",
                    "Informe peso positivo e quantidades inteiras não negativas.",
                    parent=tela
                )
                return

            banco = conectar()

            if banco is None:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível conectar ao banco.",
                    parent=tela
                )
                return

            cursor = banco.cursor()

            try:
                if id_produto is None:
                    cursor.execute(
                        """
                        INSERT INTO produtos
                        (nome, tamanho, peso, material,
                         quantidade, estoque_minimo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            nome, tamanho, peso, material,
                            quantidade, minimo
                        )
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE produtos
                        SET nome = %s, tamanho = %s, peso = %s,
                            material = %s, quantidade = %s,
                            estoque_minimo = %s
                        WHERE id = %s
                        """,
                        (
                            nome, tamanho, peso, material,
                            quantidade, minimo, id_produto
                        )
                    )

                banco.commit()
                tela.destroy()
                carregar_produtos()

            except Exception as erro:
                banco.rollback()
                messagebox.showerror(
                    "Erro",
                    f"Não foi possível salvar o produto.\n{erro}",
                    parent=tela
                )

            finally:
                cursor.close()
                banco.close()

        tk.Button(
            tela,
            text="Salvar",
            bg="#172B4D",
            fg="white",
            font=("Arial", 11, "bold"),
            command=salvar
        ).pack(pady=15, ipadx=20, ipady=5)

    def excluir_produto():
        id_produto = selecionado["id"]

        if id_produto is None:
            messagebox.showwarning(
                "Atenção",
                "Selecione um produto na tabela.",
                parent=janela
            )
            return

        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja excluir o produto selecionado?",
            parent=janela
        ):
            return

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
                "DELETE FROM produtos WHERE id = %s",
                (id_produto,)
            )
            banco.commit()
            selecionado["id"] = None
            carregar_produtos()

        except Exception:
            banco.rollback()
            messagebox.showerror(
                "Não foi possível excluir",
                "Este produto pode ter movimentações registradas. "
                "Preserve o histórico e não o exclua.",
                parent=janela
            )

        finally:
            cursor.close()
            banco.close()

    botoes = tk.Frame(janela, bg="#F2F4F7")
    botoes.pack(pady=10)

    tk.Button(
        botoes,
        text="Pesquisar",
        command=carregar_produtos
    ).pack(side="left", padx=5)

    tk.Button(
        botoes,
        text="Novo Produto",
        command=lambda: formulario()
    ).pack(side="left", padx=5)

    tk.Button(
        botoes,
        text="Editar",
        command=lambda: formulario(selecionado["id"])
        if selecionado["id"] is not None
        else messagebox.showwarning(
            "Atenção",
            "Selecione um produto.",
            parent=janela
        )
    ).pack(side="left", padx=5)

    tk.Button(
        botoes,
        text="Excluir",
        command=excluir_produto
    ).pack(side="left", padx=5)

    tk.Button(
        botoes,
        text="Atualizar Lista",
        command=carregar_produtos
    ).pack(side="left", padx=5)

    carregar_produtos()