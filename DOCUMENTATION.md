# DOCUMENTATION — Multi-etiquetas APG

Documentação técnica completa do sistema de impressão industrial.

---

## Stack Tecnológico

| Componente              | Tecnologia                                     |
|-------------------------|------------------------------------------------|
| Linguagem               | Python 3.8+                                    |
| Interface Gráfica       | `tkinter` (nativo)                             |
| Comunicação SO          | `pywin32` — API do Windows para fila de impressão |
| Protocolo de Impressão  | ZPL II (Zebra Programming Language)            |
| Armazenamento           | JSON (`sequencia.json`)                        |
| Logs                    | Arquivos `.log` diários em `/logs/`            |

---

## Arquitetura do Código (`main.py`)

O código é estruturado em **4 classes** bem definidas:

### `ServicoImpressao`
Responsável por toda comunicação com a impressora.

| Método               | Descrição                                                                    |
|----------------------|------------------------------------------------------------------------------|
| `detectar()`         | Varre todas as impressoras do sistema e retorna a Zebra com maior prioridade |
| `gerar_zpl_seyon()`  | Gera o ZPL para o modo **Seyon** (Data Matrix com sequencial dinâmico)       |
| `gerar_zpl_vw()`     | Gera o ZPL para o modo **VW** (Code 128 com layout 100x50mm)                 |
| `gerar_zpl_retrabalho()` | Gera o ZPL para o modo **Retrabalho** (formulário estático em branco)   |
| `enviar(zpl)`        | Envia o payload ZPL via protocolo RAW (`win32print`)                         |

**Prioridade de detecção de impressoras:**
1. `ZDesigner ZT230-200dpi ZPL` (prioridade máxima)
2. Qualquer driver com "zebra" ou "zdesigner" no nome

---

### `GestorDados`
Gerencia a persistência da sequência numérica e a codificação de datas.

| Método               | Descrição                                                              |
|----------------------|------------------------------------------------------------------------|
| `obter_sequencia()`  | Lê o valor atual do `sequencia.json` (padrão de fábrica: `280909`)   |
| `salvar(valor)`      | Persiste o novo valor de sequência no JSON                             |
| `codificar_data(data)` | Converte datas no formato especial de rastreabilidade da engenharia  |

**Lógica de codificação de data:**

| Campo | Mapeamento                                      |
|-------|-------------------------------------------------|
| Ano   | `2026 → D`, `2027 → E`, ...                     |
| Mês   | `1-9 → 1-9`, `10 → A`, `11 → B`, `12 → C`     |
| Dia   | `1-9 → 1-9`, `10 → A`, `11 → B`, ..., `31 → V` |

> **Exemplo:** 22 de março de 2026 → `D3M`

---

### `Logger`
Sistema de auditoria de operações.

- Cria automaticamente a pasta `logs/` se não existir.
- Grava um arquivo por dia no formato `AAAA-MM-DD.log`.
- Cada linha registra: `[timestamp] OK | Nome da Peça | Qtd: N`

---

### `AppIndustrial` (Interface Gráfica)
Janela principal `tkinter` em modo maximizado (`zoomed`).

| Elemento            | Função                                                              |
|---------------------|---------------------------------------------------------------------|
| `Combobox`          | Seleção da peça/modelo de etiqueta                                  |
| Botões de Turno     | 1º, 2º e 3º turno — destaca o selecionado em verde                 |
| Campo Matrícula     | Entrada do operador (somente números)                               |
| Campo Quantidade    | Número de etiquetas a imprimir (padrão: `1`)                        |
| Botão IMPRIMIR      | Dispara o fluxo completo em thread principal                        |
| `lbl_zebra`         | Indicador de status da impressora, atualizado a cada **3 segundos** |

---

## Banco de Peças (`PECAS_DB`)

| ID | Nome Display                        | Tipo        | Part Number              |
|----|-------------------------------------|-------------|--------------------------|
| 0  | SEYON: 37112-M4620 (Insulation Pad) | `SEYON`     | `37112-M4620`            |
| 1  | POLO PRETO (TBT) - 2G5.863.367.B   | `VW`        | `2G5.863.367.B - WH7`   |
| 2  | POLO PRETO (SBC) - 2G5.863.367.C   | `VW`        | `2G5.863.367.C - WH7`   |
| 3  | VIRTUS PRETO (SBC) - 6EC.863.367.C | `VW`        | `6EC.863.367.C - WH7`   |
| 4  | RETRABALHO TRIM (Manual)            | `RETRABALHO`| N/A                      |

---

## Layouts ZPL por Tipo de Etiqueta

### Tipo `SEYON` — Rolo 50x30mm (400x240 dots)
- **Conteúdo do Data Matrix:** `[DataCodificada][Sequencial][PartNumber]`
- O sequencial é **incrementado unitariamente** por etiqueta e persistido no JSON.
- Layout inclui: Turno, Operador, Data Matrix, Data, Código Data, Sequencial, PN e descrição da peça em banner invertido.

### Tipo `VW` — Rolo 100x50mm (800x400 dots)
- **Sem sequencial** — todas as etiquetas do lote são idênticas.
- Layout inclui: Header VW, País de Fabricação, Part Number + Suffix + Modelo, FABRICANTE: `1WR`, Material, Data de Fabricação + Turno, Matrícula e Código de Barras Code 128 (`^BY3`, 85 dots de altura).

### Tipo `RETRABALHO` — Rolo 50x30mm (400x240 dots)
- Formulário **estático em branco** para preenchimento manual com caneta.
- Campos: Data, Op. 1, M (Motivo), Op. 2, Data.

---

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+ instalado.
- Driver oficial da Zebra instalado (`ZDesigner`). A impressora **não deve** estar configurada como "Generic/Text Only".

### Instalar Dependências
```bash
pip install -r requirements.txt
```

### Gerar Executável (Deploy na Fábrica)
```bash
pyinstaller --noconsole --onefile --name="Multi-etiquetas_APG" main.py
```
O executável final estará em `dist/`.

---

## Estrutura de Diretórios em Produção

```
C:\Sistemas\Multi_Etiquetas_APG\
│
├── Multi-etiquetas_APG.exe   # Executável gerado
├── sequencia.json             # Memória de contagem sequencial
└── logs\
    ├── 2026-03-22.log
    └── 2026-03-23.log
```

> ⚠️ **ATENÇÃO TI:** Ao atualizar o executável, **NUNCA apague o `sequencia.json`**. Caso contrário, a contagem volta para o padrão de fábrica (`280909`), gerando **duplicidade no rastreio da montadora**.

---

## Solução de Problemas (Troubleshooting)

### ❌ "Nenhuma Impressora Zebra encontrada"
- **Causa:** Cabo desconectado ou driver incorreto.
- **Solução:** Verifique no Painel de Controle do Windows se a impressora aparece com "Zebra", "ZT230" ou "ZT231" no nome.

### ⏳ Status fica eternamente em "IMPRIMINDO..."
- **Causa:** Spooler bloqueado ou erro de porta RAW.
- **Solução:** Limpe a fila de impressão no Windows. Vá em *Propriedades da Impressora → Avançado → desmarque "Ativar recursos de impressão avançados"*.

### 📵 Código de Barras VW não é lido pelo Scanner
- **Causa:** Resolução incompatível ou fita fraca.
- **Solução:** A densidade térmica está no `^MD25`. Verifique físicamente se a fita (Ribbon) está em bom estado ou se a cabeça de impressão precisa de limpeza com álcool isopropílico.
