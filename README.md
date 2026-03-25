# Multi-etiquetas APG

> Sistema de Impressão Industrial para Impressoras Zebra | Adler Pelzer Group

Software de automação industrial desenvolvido em **Python + Tkinter** para controle e envio de trabalhos de impressão em lote para impressoras térmicas **Zebra ZT230 / ZT231**. Comunica-se diretamente com o spooler do Windows via protocolo **RAW**, enviando comandos ZPL de alta performance.

**Versão atual:** `V7.0` &nbsp;|&nbsp; **Plataforma:** Windows &nbsp;|&nbsp; **Linguagem:** Python 3.8+

---

## 📄 Documentação

| Documento | Descrição |
|-----------|-----------|
| [DOCUMENTATION.md](DOCUMENTATION.md) | Arquitetura, classes, layouts ZPL, instalação e troubleshooting |
| [CHANGELOG.md](CHANGELOG.md) | Histórico completo de versões (V1.0 → V7.0) |

---

## ✅ Funcionalidades Principais

| Funcionalidade | Descrição |
|----------------|-----------|
| **Comunicação RAW (ZPL)** | Impressão em milissegundos, sem travamentos no spooler |
| **Modo Seyon** | Data Matrix dinâmico com sequencial persistente (`sequencia.json`) |
| **Modo VW** | Code 128 com layout de lote 100x50mm para Polo e Virtus |
| **Modo Retrabalho** | Formulário em branco para preenchimento manual pelo CQ |
| **Auto-Detect** | Varredura automática de hardware priorizando `ZT231` e `ZDesigner ZT230` |
| **Status em Tempo Real** | Indicador de conexão com a impressora, atualizado a cada 3 s |
| **Sistema de Auditoria** | Logs diários em `/logs/AAAA-MM-DD.log` |

---

## 🚀 Início Rápido

**1. Instalar dependências:**
```bash
pip install -r requirements.txt
```

**2. Executar em desenvolvimento:**
```bash
python main.py
```

**3. Gerar executável para produção:**
```bash
pyinstaller --noconsole --onefile --name="Multi-etiquetas_APG" main.py
```
O binário final será gerado em `dist/`.

---

## 📁 Estrutura em Produção

```
C:\Sistemas\Multi_Etiquetas_APG\
├── Multi-etiquetas_APG.exe   ← Executável
├── sequencia.json             ← NÃO APAGAR (memória de contagem Seyon)
└── logs\
    └── AAAA-MM-DD.log
```

> ⚠️ **ATENÇÃO TI:** Nunca apague o `sequencia.json` ao atualizar o sistema. A deleção reinicia a contagem para `280909`, gerando **duplicidade no rastreio da montadora**.