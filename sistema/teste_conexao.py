from conexao import conectar


banco = conectar()

if banco:
    print("Conexão com o banco realizada com sucesso!")
    banco.close()
else:
    print("Não foi possível conectar ao banco.")