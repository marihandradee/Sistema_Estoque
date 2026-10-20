-- Script de criação e população do banco de dados do Sistema de Gestão de Estoque
-- Banco exigido na atividade: saep_db
-- As senhas abaixo são contas de demonstração e ficam armazenadas em hash PBKDF2-SHA256.
-- Não coloque neste arquivo a senha real do servidor MySQL.

CREATE DATABASE IF NOT EXISTS saep_db;
USE saep_db;

-- 1. Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

-- 2. Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tamanho VARCHAR(50) NOT NULL,
    peso DECIMAL(10,2) NOT NULL,
    material VARCHAR(100) NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 0
);

-- 3. Tabela de movimentações
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    tipo ENUM('ENTRADA', 'SAIDA') NOT NULL,
    quantidade INT NOT NULL,
    data_movimentacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movimentacoes_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
    CONSTRAINT fk_movimentacoes_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Usuários de demonstração. Insere cada um somente se ainda não existir.
-- Login: maria / senha_temporaria
INSERT INTO usuarios (nome, usuario, senha)
SELECT 'Maria Eduarda', 'maria', 'pbkdf2_sha256$00112233445566778899aabbccddeeff$4a65f7391e00603cd78b2b7e03808e35960895c60b90705118aa5c18f335ac37'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'maria');

-- Login: operador1 / operador123
INSERT INTO usuarios (nome, usuario, senha)
SELECT 'Operador de Estoque 1', 'operador1', 'pbkdf2_sha256$112233445566778899aabbccddeeff00$58cc5a9719ad1c10227f9e0759165252499e1dadd9fae9be8cf5e410c5185a46'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'operador1');

-- Login: operador2 / operador456
INSERT INTO usuarios (nome, usuario, senha)
SELECT 'Operador de Estoque 2', 'operador2', 'pbkdf2_sha256$2233445566778899aabbccddeeff0011$2141f95f12ce193c6e571a8732859a933f83f13504cfac5407df10db02c816ef'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'operador2');

-- Produtos de exemplo. Insere somente se o produto ainda não existir.
INSERT INTO produtos (nome, tamanho, peso, material, quantidade, estoque_minimo)
SELECT 'Martelo', '30 cm', 0.80, 'Aço e madeira', 15, 5
WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Martelo');

INSERT INTO produtos (nome, tamanho, peso, material, quantidade, estoque_minimo)
SELECT 'Chave de fenda', '20 cm', 0.25, 'Aço e plástico', 8, 10
WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Chave de fenda');

INSERT INTO produtos (nome, tamanho, peso, material, quantidade, estoque_minimo)
SELECT 'Alicate', '18 cm', 0.35, 'Aço carbono', 12, 4
WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Alicate');

-- Movimentações iniciais de exemplo para registrar o saldo atual dos produtos.
-- Estas instruções registram o histórico, mas não alteram a quantidade na tabela produtos.
-- Insere cada movimentação somente se ainda não houver movimentação desse produto
-- vinculada ao usuário maria.
INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, data_movimentacao)
SELECT p.id, u.id, 'ENTRADA', p.quantidade, NOW()
FROM produtos p
JOIN usuarios u ON u.usuario = 'maria'
WHERE p.nome = 'Martelo'
  AND NOT EXISTS (
      SELECT 1 FROM movimentacoes m
      WHERE m.produto_id = p.id AND m.usuario_id = u.id
  );

INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, data_movimentacao)
SELECT p.id, u.id, 'ENTRADA', p.quantidade, NOW()
FROM produtos p
JOIN usuarios u ON u.usuario = 'maria'
WHERE p.nome = 'Chave de fenda'
  AND NOT EXISTS (
      SELECT 1 FROM movimentacoes m
      WHERE m.produto_id = p.id AND m.usuario_id = u.id
  );

INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, data_movimentacao)
SELECT p.id, u.id, 'ENTRADA', p.quantidade, NOW()
FROM produtos p
JOIN usuarios u ON u.usuario = 'maria'
WHERE p.nome = 'Alicate'
  AND NOT EXISTS (
      SELECT 1 FROM movimentacoes m
      WHERE m.produto_id = p.id AND m.usuario_id = u.id
  );

-- Confira a população após executar:
-- SELECT * FROM usuarios;
-- SELECT * FROM produtos;
-- SELECT * FROM movimentacoes;
