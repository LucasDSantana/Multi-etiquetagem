import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os
import threading

# ==============================================================================
# TENTA IMPORTAR DRIVER DE IMPRESSÃO (WINDOWS)
# ==============================================================================
try:
    import win32print
    PRINTER_AVAILABLE = True
except ImportError:
    PRINTER_AVAILABLE = False

# ==============================================================================
# CONFIGURAÇÕES E BANCO DE DADOS DE PEÇAS
# ==============================================================================
CONSTANTES = {
    "ARQUIVO_SEQUENCIA": "sequencia.json",
    "PASTA_LOG": "logs"
}

PECAS_DB = [
    {
        "id": 0,
        "nome_display": "SEYON: 37112-M4620 (Insulation Pad)",
        "tipo": "SEYON",
        "pn_raw": "37112-M4620",
        "descricao": "Insulation Pad - Batt (60AH AGM)."
    },
    {
        "id": 1,
        "nome_display": "POLO PRETO (TBT) - 2G5.863.367.B",
        "tipo": "VW",
        "pn_raw": "2G5.863.367.B - WH7",
        "pn_formatado": "2G5.863.367.B",
        "suffix": "WH7",
        "modelo_carro": "POLO PRETO"
    },
    {
        "id": 2,
        "nome_display": "POLO PRETO (SBC) - 2G5.863.367.C",
        "tipo": "VW",
        "pn_raw": "2G5.863.367.C - WH7",
        "pn_formatado": "2G5.863.367.C",
        "suffix": "WH7",
        "modelo_carro": "POLO PRETO"
    },
    {
        "id": 3,
        "nome_display": "VIRTUS PRETO (SBC) - 6EC.863.367.C",
        "tipo": "VW",
        "pn_raw": "6EC.863.367.C - WH7",
        "pn_formatado": "6EC.863.367.C",
        "suffix": "WH7",
        "modelo_carro": "VIRTUS PRETO"
    },
    {
        "id": 4,
        "nome_display": "RETRABALHO TRIM (Manual)",
        "tipo": "RETRABALHO",
        "pn_raw": "N/A",
        "descricao": "Etiqueta de Retrabalho"
    }
]

# ==============================================================================
# SERVIÇO DE IMPRESSÃO (ZPL)
# ==============================================================================
class ServicoImpressao:
    def __init__(self):
        self.nome_impressora = None

    def detectar(self):
        if not PRINTER_AVAILABLE:
            return None
        try:
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            impressoras = win32print.EnumPrinters(flags)
            lista_nomes = [info[2] for info in impressoras]

            # PRIORIDADE DE DETECÇÃO
            prioridades = ["ZDesigner ZT230-200dpi ZPL"]
            for p in prioridades:
                if p in lista_nomes:
                    return p

            for nome in lista_nomes:
                if "zebra" in nome.lower() or "zdesigner" in nome.lower():
                    return nome
        except:
            pass
        return None

    def gerar_zpl_seyon(self, turno, operador, seq, dados_peca):
        agora = datetime.datetime.now()
        data_cod = GestorDados().codificar_data(agora)
        pn = dados_peca['pn_raw']
        qr = f"{data_cod}{seq}{pn}"
        return f"^XA^PW400^LL240^CI28^MD25^FO15,10^A0N,25,25^FD{turno}o Turno^FS^FO150,10^A0N,25,25^FD{operador}^FS^FO15,45^BXN,6,200^FD{qr}^FS^FO170,55^A0N,28,28^FD{agora.strftime('%Y/%m/%d')}^FS^FO170,90^A0N,28,28^FD{data_cod}   {seq}^FS^FO170,125^A0N,28,28^FD{pn}^FS^FO0,205^GB400,35,35^FS^FO10,212^A0N,20,20^FR^FD{dados_peca['descricao']}^FS^XZ"

    def gerar_zpl_vw(self, turno, operador, dados_peca):
        agora = datetime.datetime.now()
        data_str = agora.strftime("%d/%m/%Y")
        pn_fmt, pn_raw, suffix, carro = dados_peca['pn_formatado'], dados_peca['pn_raw'], dados_peca['suffix'], dados_peca['modelo_carro']
        
        # REAJUSTE V7: 100mm x 50mm (800x400 dots)
        return f"""
^XA
^PW800
^LL400
^CI28
^MD25
^FO30,25^A0N,28,28^FDVOLKSWAGEN DO BRASIL^FS
^FO30,55^A0N,22,22^FDPRODUZIDO NO BRASIL / MADE IN BRAZIL^FS
^FO30,90^A0N,28,28^FDPART NUMBER:{pn_fmt} - {suffix}  {carro}^FS
^FO30,125^A0N,28,28^FDFABRICANTE: 1WR^FS
^FO30,160^A0N,18,18^FDMATERIAL: > PP <, > PET <, > CO + PP + PET <, > PP + EVA <^FS
^FO30,195^A0N,28,28^FDDATA FABRICACAO:{data_str}   TURNO {turno}^FS
^FO30,230^A0N,28,28^FDMATRICULA: {operador}^FS
^FO50,280^BY3^BCN,85,Y,N,N^FD{pn_raw}^FS
^XZ
"""

    def gerar_zpl_retrabalho(self):
        return "^XA^PW400^LL240^CI28^MD25^FO10,25^A0N,25,25^FDData:______/______/______^FS^FO10,70^A0N,25,25^FDOp. 1:___________________^FS^FO10,115^A0N,25,25^FDM:_______________________^FS^FO10,160^A0N,25,25^FDOp. 2:___________________^FS^FO10,205^A0N,25,25^FDData:______/______/______^FS^XZ"

    def enviar(self, zpl):
        self.nome_impressora = self.detectar()
        if not self.nome_impressora:
            raise Exception("Impressora não encontrada.")
        h = win32print.OpenPrinter(self.nome_impressora)
        try:
            win32print.StartDocPrinter(h, 1, ("Multi-etiquetas APG", None, "RAW"))
            win32print.StartPagePrinter(h)
            win32print.WritePrinter(h, zpl.encode("utf-8"))
            win32print.EndPagePrinter(h)
            win32print.EndDocPrinter(h)
        finally:
            win32print.ClosePrinter(h)

# ==============================================================================
# GESTÃO DE DADOS E LOG
# ==============================================================================
class GestorDados:
    def __init__(self): self.arquivo = CONSTANTES["ARQUIVO_SEQUENCIA"]
    def obter_sequencia(self):
        if not os.path.exists(self.arquivo): self.salvar(280909); return 280909
        try:
            with open(self.arquivo, "r") as f: return json.load(f).get("sequencia", 280909)
        except: return 280909
    def salvar(self, valor):
        with open(self.arquivo, "w") as f: json.dump({"sequencia": valor}, f)
    def codificar_data(self, data):
        mapa_ano, mapa_mes, letras = {2026: "D", 2027: "E"}, {i:str(i) for i in range(1,10)}, "ABCDEFGHIJKLMNOPQRSTUV"
        mapa_mes.update({10:"A", 11:"B", 12:"C"})
        mapa_dia = {i: str(i) for i in range(1,10)}
        mapa_dia.update({i+10: letras[i] for i in range(len(letras))})
        return f"{mapa_ano.get(data.year, '?')}{mapa_mes.get(data.month, '?')}{mapa_dia.get(data.day, '?')}"

class Logger:
    def registrar(self, mensagem):
        os.makedirs(CONSTANTES["PASTA_LOG"], exist_ok=True)
        arquivo = os.path.join(CONSTANTES["PASTA_LOG"], f"{datetime.date.today()}.log")
        with open(arquivo, "a", encoding="utf-8") as f: f.write(mensagem + "\n")

# ==============================================================================
# INTERFACE GRÁFICA
# ==============================================================================
class AppIndustrial(tk.Tk):
    def __init__(self):
        super().__init__()
        self.gestor, self.servico, self.logger = GestorDados(), ServicoImpressao(), Logger()
        self.turno_selecionado = tk.IntVar(value=0)
        self.title("Multi-etiquetas APG")
        self.state("zoomed"); self.configure(bg="#f0f0f0")
        self.criar_interface()
        self.atualizar_status()

    def criar_interface(self):
        self.lbl_zebra = tk.Label(self, text="● Zebra: Buscando...", fg="gray", bg="#f0f0f0", font=("Arial", 12, "bold"))
        self.lbl_zebra.place(relx=0.98, rely=0.02, anchor="ne")
        main = tk.Frame(self, bg="#f0f0f0"); main.pack(expand=True, fill="both", padx=50, pady=20)
        
        tk.Label(main, text="1. SELECIONE A PEÇA:", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=5)
        self.combo = ttk.Combobox(main, values=[p["nome_display"] for p in PECAS_DB], font=("Arial", 20), state="readonly", width=40)
        self.combo.current(0); self.combo.pack(pady=5, ipady=10)
        
        tk.Frame(main, height=2, bg="#cccccc").pack(fill="x", pady=20)
        tk.Label(main, text="2. TURNO:", font=("Arial", 18, "bold"), bg="#f0f0f0").pack()
        f_turnos = tk.Frame(main, bg="#f0f0f0"); f_turnos.pack(pady=5)
        self.btns = []
        for i in range(1, 4):
            btn = tk.Button(f_turnos, text=f"{i}º TURNO", font=("Arial", 16, "bold"), width=12, height=2, command=lambda x=i: self.sel_turno(x))
            btn.pack(side="left", padx=20); self.btns.append(btn)

        tk.Frame(main, height=2, bg="#cccccc").pack(fill="x", pady=20)
        tk.Label(main, text="3. MATRÍCULA:", font=("Arial", 18, "bold"), bg="#f0f0f0").pack()
        self.ent_op = tk.Entry(main, font=("Arial", 30), justify="center", width=12); self.ent_op.pack(pady=5)
        
        tk.Frame(main, height=2, bg="#cccccc").pack(fill="x", pady=20)
        tk.Label(main, text="4. QUANTIDADE:", font=("Arial", 18, "bold"), fg="#d32f2f", bg="#f0f0f0").pack()
        self.ent_qtd = tk.Entry(main, font=("Arial", 35, "bold"), justify="center", fg="#d32f2f", width=8); self.ent_qtd.insert(0, "1"); self.ent_qtd.pack()
        
        tk.Button(main, text="IMPRIMIR", font=("Arial", 25, "bold"), bg="#007acc", fg="white", command=self.imprimir).pack(pady=30, ipadx=40, ipady=10)
        self.lbl_st = tk.Label(main, text="", font=("Arial", 20, "bold"), bg="#f0f0f0"); self.lbl_st.pack()

    def sel_turno(self, v):
        self.turno_selecionado.set(v)
        for i, b in enumerate(self.btns): b.config(bg="#4caf50" if i+1==v else "#e0e0e0", fg="white" if i+1==v else "black")

    def atualizar_status(self):
        nome = self.servico.detectar()
        self.lbl_zebra.config(text=f"● {nome if nome else 'Desconectada'}", fg="green" if nome else "red")
        self.after(3000, self.atualizar_status)

    def imprimir(self):
        try:
            t, op, q_s, idx = self.turno_selecionado.get(), self.ent_op.get(), self.ent_qtd.get(), self.combo.current()
            if t == 0 or not op or not q_s: messagebox.showwarning("Erro", "Campos incompletos!"); return
            
            qtd, peca, zpl = int(q_s), PECAS_DB[idx], ""
            self.lbl_st.config(text="IMPRIMINDO...", fg="orange"); self.update()
            
            if peca["tipo"] == "SEYON":
                seq = self.gestor.obter_sequencia()
                for _ in range(qtd): seq += 1; zpl += self.servico.gerar_zpl_seyon(t, op, seq, peca)
                self.gestor.salvar(seq)
            elif peca["tipo"] == "VW": zpl = self.servico.gerar_zpl_vw(t, op, peca) * qtd
            else: zpl = self.servico.gerar_zpl_retrabalho() * qtd

            self.servico.enviar(zpl)
            self.logger.registrar(f"[{datetime.datetime.now()}] OK | {peca['nome_display']} | Qtd: {qtd}")
            self.lbl_st.config(text="SUCESSO!", fg="green")
            self.after(4000, lambda: self.lbl_st.config(text=""))
        except Exception as e: messagebox.showerror("Erro", str(e))

if __name__ == "__main__": AppIndustrial().mainloop()