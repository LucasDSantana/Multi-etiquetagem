# CHANGELOG — Multi-etiquetas APG

Histórico completo de versões do sistema de impressão industrial.

---

## [V7.0] - Estabilidade e Ajuste Fino *(Versão Atual)*

- **Geometria Final VW:** Ajuste milimétrico de altura para o rolo padrão de **100x50mm** (`^LL400`). Re-espaçamento vertical de todos os blocos de texto.
- **Auto-Detect Dinâmico:** Remoção da dependência da porta fixa (`USB001`). O sistema agora varre todo o hardware conectado e localiza a impressora baseada no nome do driver, priorizando `ZDesigner ZT230-200dpi ZPL` e `ZT231`.
- **Branding:** Título da janela fixado permanentemente para `Multi-etiquetas APG`.

---

## [V6.0] - Nova Geometria de Rolo (VW 100x60mm)

- Engenharia solicitou aumento físico da etiqueta VW.
- Lógica ZPL reescrita para redimensionar o Canvas para `^PW800` (100mm) e `^LL480` (60mm).
- Código de barras linear aumentado para `^BY3` (barras largas) e altura estendida para 100 dots, otimizando drasticamente a velocidade de scan na linha de montagem.

---

## [V5.0] - Inclusão do Setup de Qualidade

- Adição do modelo de etiqueta de **"RETRABALHO TRIM"**.
- Configuração especial ignorando sequenciais e dados inseridos; imprime um esqueleto de formulário estático (`Data`, `Op1`, `M`, `Op2`) para preenchimento manual no setor de qualidade.

---

## [V4.0 – V4.1] - Otimização de Leitura (Scanners)

- **Bugfix:** O Código de Barras do modelo VW não estava sendo lido pelos coletores de dados devido ao excesso de caracteres para uma etiqueta de 30mm.
- **Ajuste ZPL:** Inclusão do comando `^MD25` para escurecer a impressão (Darkness).
- **Ajuste ZPL:** Fixação da largura da barra em `^BY1` e cálculo preciso das margens laterais (Quiet Zones) no eixo X (`^FO85`) para garantir a leitura 100% segura.

---

## [V2.0 – V3.0] - Refatoração de UI/UX

- Interface redesenhada com foco ergonômico para operadores com luvas / monitores touch no chão de fábrica (botões maiores e coloridos).
- Adição do sistema de **Status Polling (Ping)** no canto superior direito para exibir "Zebra Conectada/Desconectada" em tempo real.
- Validação estrita de campos vazios e regex simples para aceitar apenas números na entrada de matrícula e quantidade.

---

## [V1.5] - Arquitetura Multi-Modelo

- Transformação do sistema para suportar **N-modelos de etiquetas**.
- Adição do menu de seleção `Combobox`.
- Inclusão das peças Volkswagen (Polo e Virtus).
- Implementação do **Código de Barras linear (Code 128)** e inclusão de textos fixos obrigatórios (Material, Fabricante, etc.).
- Design Original VW: Formatado inicialmente para o rolo de 50x30mm.

---

## [V1.0 – V1.4] - O Núcleo Base (Seyon)

- Criação da interface original para impressão do componente *Insulation Pad - Batt.*
- Implementação da lógica de sequência persistente (arquivo `sequencia.json`).
- Codificação complexa de datas (ex: Ano 2026 = `D`, Meses em Hex/Letras) conforme especificação da engenharia.
- Geração de código 2D (Data Matrix) via ZPL puro.
- **Hotfix:** Transição do envio padrão de impressões para o envio RAW (`win32print`), resolvendo o travamento na fila do Windows ao imprimir mais de 100 etiquetas.
