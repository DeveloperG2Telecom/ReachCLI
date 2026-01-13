"""
Aplicação Desktop para Teste de Conectividade HTTP/HTTPS - IPv4
Interface gráfica com Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import csv
from datetime import datetime

from services.http_tester import HTTPTester
from utils.file_reader import validar_ipv4
import config


class AppDesktop:
    """Classe principal da aplicação desktop"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Teste de Conectividade HTTP/HTTPS - IPv4")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variáveis
        self.resultados = []
        self.executando = False
        
        # Configura estilo
        self.configurar_estilo()
        
        # Cria interface
        self.criar_interface()
        
        # Centraliza janela
        self.centralizar_janela()
    
    def configurar_estilo(self):
        """Configura o estilo visual da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores personalizadas
        self.cor_primaria = "#2563eb"
        self.cor_sucesso = "#10b981"
        self.cor_erro = "#ef4444"
        self.cor_timeout = "#f59e0b"
        self.cor_fundo = "#f8fafc"
    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def criar_interface(self):
        """Cria todos os componentes da interface"""
        
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🌐 Teste de Conectividade HTTP/HTTPS",
            font=("Arial", 18, "bold"),
            fg=self.cor_primaria
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Sistema de teste para clientes IPv4",
            font=("Arial", 10),
            fg="#64748b"
        )
        subtitle_label.pack()
        
        # Frame de configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        config_inner = ttk.Frame(config_frame)
        config_inner.pack(fill=tk.X)
        
        # Porta
        ttk.Label(config_inner, text="Porta:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.porta_var = tk.StringVar(value=str(config.PORTA_PADRAO))
        porta_entry = ttk.Entry(config_inner, textvariable=self.porta_var, width=10)
        porta_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Timeout
        ttk.Label(config_inner, text="Timeout (segundos):").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.timeout_var = tk.StringVar(value=str(config.TIMEOUT_PADRAO))
        timeout_entry = ttk.Entry(config_inner, textvariable=self.timeout_var, width=10)
        timeout_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Verificar SSL
        self.verificar_ssl_var = tk.BooleanVar(value=config.VERIFICAR_SSL)
        ssl_check = ttk.Checkbutton(
            config_inner,
            text="Verificar SSL",
            variable=self.verificar_ssl_var
        )
        ssl_check.grid(row=0, column=4, sticky=tk.W)
        
        # Frame de entrada de IPs
        input_frame = ttk.LabelFrame(main_frame, text="Lista de IPs", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Textarea para IPs
        self.ips_text = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            font=("Courier New", 10),
            wrap=tk.WORD
        )
        self.ips_text.pack(fill=tk.BOTH, expand=True)
        self.ips_text.insert("1.0", "187.10.10.1\n200.150.30.5\n179.40.22.9")
        
        # Botões de ação
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.btn_testar = tk.Button(
            button_frame,
            text="▶ Executar Testes",
            command=self.executar_testes,
            bg=self.cor_primaria,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.btn_testar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_limpar = tk.Button(
            button_frame,
            text="Limpar",
            command=self.limpar,
            bg="#64748b",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        )
        btn_limpar.pack(side=tk.LEFT)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Frame de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        resultados_frame.pack(fill=tk.BOTH, expand=True)
        
        # Estatísticas
        self.stats_frame = ttk.Frame(resultados_frame)
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tabela de resultados
        self.criar_tabela(resultados_frame)
        
        # Botão exportar
        btn_exportar = tk.Button(
            resultados_frame,
            text="📥 Exportar CSV",
            command=self.exportar_csv,
            bg=self.cor_sucesso,
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        )
        btn_exportar.pack(pady=(10, 0))
    
    def criar_tabela(self, parent):
        """Cria a tabela de resultados"""
        # Frame para scrollbar
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview (tabela)
        columns = ('IP', 'HTTP', 'HTTPS', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configura colunas
        self.tree.heading('IP', text='IP')
        self.tree.heading('HTTP', text='HTTP')
        self.tree.heading('HTTPS', text='HTTPS')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('IP', width=200, anchor=tk.W)
        self.tree.column('HTTP', width=200, anchor=tk.W)
        self.tree.column('HTTPS', width=200, anchor=tk.W)
        self.tree.column('Status', width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tags para cores
        self.tree.tag_configure('ok', background='#d1fae5')
        self.tree.tag_configure('timeout', background='#fef3c7')
        self.tree.tag_configure('error', background='#fee2e2')
    
    def calcular_workers(self, numero_ips: int) -> int:
        """Calcula número ideal de workers"""
        workers = max(config.MIN_WORKERS, min(numero_ips // 5, config.MAX_WORKERS))
        workers = min(workers, numero_ips, config.MAX_WORKERS)
        return max(workers, 1)
    
    def processar_ips(self) -> List[str]:
        """Processa texto de IPs e retorna lista válida"""
        texto = self.ips_text.get("1.0", tk.END).strip()
        if not texto:
            return []
        
        ips_validos = []
        linhas = texto.split('\n')
        
        for linha in linhas:
            ip = linha.strip()
            if ip and not ip.startswith('#'):
                if validar_ipv4(ip):
                    ips_validos.append(ip)
        
        return ips_validos
    
    def executar_testes(self):
        """Executa os testes de conectividade"""
        if self.executando:
            return
        
        # Obtém IPs
        ips = self.processar_ips()
        
        if not ips:
            messagebox.showwarning("Aviso", "Por favor, insira pelo menos um IP válido.")
            return
        
        # Obtém configurações
        try:
            porta = int(self.porta_var.get())
            timeout = int(self.timeout_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Porta e Timeout devem ser números válidos.")
            return
        
        # Limpa resultados anteriores
        self.tree.delete(*self.tree.get_children())
        self.resultados = []
        
        # Desabilita botão e inicia progresso
        self.executando = True
        self.btn_testar.config(state=tk.DISABLED, text="Executando...")
        self.progress.start(10)
        
        # Executa em thread separada
        self.root.after(100, lambda: self._executar_testes_thread(ips, porta, timeout))
    
    def _executar_testes_thread(self, ips: List[str], porta: int, timeout: int):
        """Executa testes em thread separada"""
        try:
            # Inicializa testador
            testador = HTTPTester(
                porta=porta,
                timeout=timeout,
                verificar_ssl=self.verificar_ssl_var.get()
            )
            
            # Calcula workers
            num_workers = self.calcular_workers(len(ips))
            
            # Executa testes
            resultados = []
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {executor.submit(testador.testar_ip, ip): ip for ip in ips}
                
                for future in as_completed(futures):
                    ip = futures[future]
                    try:
                        resultado = future.result()
                        resultados.append(resultado)
                        
                        # Atualiza interface
                        self.root.after(0, lambda r=resultado: self._adicionar_resultado(r))
                        
                    except Exception as e:
                        resultado = {
                            'ip': ip,
                            'http': f'Erro: {str(e)}',
                            'https': f'Erro: {str(e)}'
                        }
                        resultados.append(resultado)
                        self.root.after(0, lambda r=resultado: self._adicionar_resultado(r))
            
            # Ordena resultados
            resultados.sort(key=lambda x: x['ip'])
            self.resultados = resultados
            
            # Atualiza estatísticas
            self.root.after(0, self._atualizar_estatisticas)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao executar testes: {str(e)}"))
        
        finally:
            # Reabilita botão e para progresso
            self.root.after(0, self._finalizar_execucao)
    
    def _adicionar_resultado(self, resultado: Dict):
        """Adiciona um resultado à tabela"""
        ip = resultado['ip']
        http = resultado.get('http', 'N/A')
        https = resultado.get('https', 'N/A')
        
        # Determina status e tag
        status = 'OK'
        tag = 'ok'
        
        if 'Timeout' in http and 'Timeout' in https:
            status = 'Timeout'
            tag = 'timeout'
        elif 'OK' not in http and 'OK' not in https:
            status = 'Error'
            tag = 'error'
        
        # Insere na tabela
        self.tree.insert('', tk.END, values=(ip, http, https, status), tags=(tag,))
    
    def _atualizar_estatisticas(self):
        """Atualiza as estatísticas exibidas"""
        # Limpa estatísticas anteriores
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        if not self.resultados:
            return
        
        total = len(self.resultados)
        ok = sum(1 for r in self.resultados if 'OK' in str(r.get('http', '')) or 'OK' in str(r.get('https', '')))
        timeout = sum(1 for r in self.resultados if 'Timeout' in str(r.get('http', '')) and 'Timeout' in str(r.get('https', '')))
        error = total - ok - timeout
        
        # Cria labels de estatísticas
        stats_text = f"Total: {total} | OK: {ok} ({ok*100/total:.1f}%) | Timeout: {timeout} ({timeout*100/total:.1f}%) | Error: {error} ({error*100/total:.1f}%)"
        
        stats_label = tk.Label(
            self.stats_frame,
            text=stats_text,
            font=("Arial", 10, "bold"),
            fg=self.cor_primaria
        )
        stats_label.pack()
    
    def _finalizar_execucao(self):
        """Finaliza a execução dos testes"""
        self.executando = False
        self.btn_testar.config(state=tk.NORMAL, text="▶ Executar Testes")
        self.progress.stop()
    
    def limpar(self):
        """Limpa os campos e resultados"""
        self.ips_text.delete("1.0", tk.END)
        self.tree.delete(*self.tree.get_children())
        self.resultados = []
        
        # Limpa estatísticas
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
    
    def exportar_csv(self):
        """Exporta resultados para CSV"""
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum resultado para exportar.")
            return
        
        # Solicita local para salvar
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as arquivo:
                campos = ['IP', 'HTTP', 'HTTPS', 'Status']
                escritor = csv.DictWriter(arquivo, fieldnames=campos)
                
                escritor.writeheader()
                
                for resultado in self.resultados:
                    http = resultado.get('http', 'N/A')
                    https = resultado.get('https', 'N/A')
                    
                    # Determina status
                    status = 'OK'
                    if 'Timeout' in http and 'Timeout' in https:
                        status = 'Timeout'
                    elif 'OK' not in http and 'OK' not in https:
                        status = 'Error'
                    
                    escritor.writerow({
                        'IP': resultado['ip'],
                        'HTTP': http,
                        'HTTPS': https,
                        'Status': status
                    })
            
            messagebox.showinfo("Sucesso", f"Resultados exportados para:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV: {str(e)}")


def main():
    """Função principal"""
    root = tk.Tk()
    app = AppDesktop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
