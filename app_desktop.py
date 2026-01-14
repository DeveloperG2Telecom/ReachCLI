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
import ipaddress

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
        self.ordem_atual = 'ip'  # 'ip', 'status', 'http', 'https'
        self.ordem_reversa = False
        
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
        
        # Cores personalizadas modernas
        self.cor_primaria = "#2563eb"
        self.cor_primaria_hover = "#1d4ed8"
        self.cor_sucesso = "#10b981"
        self.cor_sucesso_hover = "#059669"
        self.cor_erro = "#ef4444"
        self.cor_erro_hover = "#dc2626"
        self.cor_timeout = "#f59e0b"
        self.cor_timeout_hover = "#d97706"
        self.cor_fundo = "#f8fafc"
        self.cor_secundaria = "#64748b"
        self.cor_secundaria_hover = "#475569"
        
        # Configura cores do tema
        self.root.configure(bg=self.cor_fundo)
        
        # Estiliza ttk widgets
        style.configure('TLabelFrame', background='white', borderwidth=2, relief='solid')
        style.configure('TLabelFrame.Label', background='white', font=('Arial', 10, 'bold'))
        style.configure('TFrame', background=self.cor_fundo)
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=5)
        style.configure('TButton', padding=8, font=('Arial', 9))
    
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
        
        # Frame principal com padding e fundo
        main_frame = tk.Frame(self.root, bg=self.cor_fundo, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título com gradiente visual
        title_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        title_frame.pack(fill=tk.X, pady=(0, 25))
        
        title_label = tk.Label(
            title_frame,
            text="🌐 Teste de Conectividade HTTP/HTTPS",
            font=("Segoe UI", 22, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Sistema de teste para clientes IPv4",
            font=("Segoe UI", 11),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Frame de configurações com estilo melhorado
        config_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        config_title = tk.Label(
            config_frame,
            text="⚙️ Configurações",
            font=("Segoe UI", 11, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        config_title.pack(fill=tk.X, padx=15, pady=(12, 8))
        
        config_inner = tk.Frame(config_frame, bg='white')
        config_inner.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Porta
        tk.Label(config_inner, text="Porta:", bg='white', font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.porta_var = tk.StringVar(value=str(config.PORTA_PADRAO))
        porta_entry = tk.Entry(config_inner, textvariable=self.porta_var, width=12, font=("Segoe UI", 9), relief='solid', bd=1)
        porta_entry.grid(row=0, column=1, padx=(0, 25))
        
        # Timeout
        tk.Label(config_inner, text="Timeout (segundos):", bg='white', font=("Segoe UI", 9)).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.timeout_var = tk.StringVar(value=str(config.TIMEOUT_PADRAO))
        timeout_entry = tk.Entry(config_inner, textvariable=self.timeout_var, width=12, font=("Segoe UI", 9), relief='solid', bd=1)
        timeout_entry.grid(row=0, column=3, padx=(0, 25))
        
        # Verificar SSL
        self.verificar_ssl_var = tk.BooleanVar(value=config.VERIFICAR_SSL)
        ssl_check = tk.Checkbutton(
            config_inner,
            text="Verificar SSL",
            variable=self.verificar_ssl_var,
            bg='white',
            font=("Segoe UI", 9),
            activebackground='white'
        )
        ssl_check.grid(row=0, column=4, sticky=tk.W)
        
        # Frame de entrada de IPs
        input_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        input_title = tk.Label(
            input_frame,
            text="📝 Lista de IPs",
            font=("Segoe UI", 11, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        input_title.pack(fill=tk.X, padx=15, pady=(12, 8))
        
        # Textarea para IPs com estilo melhorado
        text_frame = tk.Frame(input_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.ips_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief='solid',
            bd=1,
            bg='#fafafa',
            fg='#1e293b',
            insertbackground=self.cor_primaria
        )
        self.ips_text.pack(fill=tk.BOTH, expand=True)
        self.ips_text.insert("1.0", "187.10.10.1\n200.150.30.5\n179.40.22.9")
        
        # Botões de ação com estilo melhorado
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.btn_testar = self.criar_botao(
            button_frame,
            "▶ Executar Testes",
            self.executar_testes,
            self.cor_primaria,
            self.cor_primaria_hover,
            bold=True
        )
        self.btn_testar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_limpar = self.criar_botao(
            button_frame,
            "🗑 Limpar",
            self.limpar,
            self.cor_secundaria,
            self.cor_secundaria_hover
        )
        btn_limpar.pack(side=tk.LEFT)
        
        # Barra de progresso com estilo melhorado
        progress_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400,
            style='TProgressbar'
        )
        self.progress.pack()
        
        # Frame de resultados
        resultados_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        resultados_frame.pack(fill=tk.BOTH, expand=True)
        
        resultados_title = tk.Label(
            resultados_frame,
            text="📊 Resultados",
            font=("Segoe UI", 11, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        resultados_title.pack(fill=tk.X, padx=15, pady=(12, 8))
        
        # Estatísticas
        self.stats_frame = tk.Frame(resultados_frame, bg='white')
        self.stats_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Frame para botões de ação dos resultados
        resultados_actions = tk.Frame(resultados_frame, bg='white')
        resultados_actions.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Botões de ordenação e cópia
        ordenar_frame = tk.Frame(resultados_actions, bg='white')
        ordenar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(ordenar_frame, text="Ordenar por:", bg='white', font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 8))
        
        btn_ord_ip = self.criar_botao_pequeno(ordenar_frame, "IP", lambda: self.ordenar_resultados('ip'))
        btn_ord_ip.pack(side=tk.LEFT, padx=2)
        
        btn_ord_status = self.criar_botao_pequeno(ordenar_frame, "Status", lambda: self.ordenar_resultados('status'))
        btn_ord_status.pack(side=tk.LEFT, padx=2)
        
        # Botões de cópia
        copiar_frame = tk.Frame(resultados_actions, bg='white')
        copiar_frame.pack(side=tk.RIGHT)
        
        btn_copiar_ok = self.criar_botao(
            copiar_frame,
            "✅ Copiar IPs OK",
            self.copiar_ips_ok,
            self.cor_sucesso,
            self.cor_sucesso_hover,
            small=True
        )
        btn_copiar_ok.pack(side=tk.LEFT, padx=5)
        
        btn_copiar_erro = self.criar_botao(
            copiar_frame,
            "❌ Copiar IPs Erro",
            self.copiar_ips_erro,
            self.cor_erro,
            self.cor_erro_hover,
            small=True
        )
        btn_copiar_erro.pack(side=tk.LEFT, padx=5)
        
        # Tabela de resultados
        self.criar_tabela(resultados_frame)
        
        # Botão exportar
        exportar_frame = tk.Frame(resultados_frame, bg='white')
        exportar_frame.pack(fill=tk.X, padx=15, pady=(10, 15))
        
        btn_exportar = self.criar_botao(
            exportar_frame,
            "📥 Exportar CSV",
            self.exportar_csv,
            self.cor_sucesso,
            self.cor_sucesso_hover
        )
        btn_exportar.pack()
    
    def criar_botao(self, parent, text, command, bg, bg_hover, bold=False, small=False):
        """Cria um botão estilizado"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="white",
            font=("Segoe UI", 9 if small else 10, "bold" if bold else "normal"),
            padx=15 if not small else 12,
            pady=8 if not small else 6,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=bg_hover,
            activeforeground="white"
        )
        
        # Efeito hover
        def on_enter(e):
            btn.config(bg=bg_hover)
        def on_leave(e):
            btn.config(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def criar_botao_pequeno(self, parent, text, command):
        """Cria um botão pequeno para ordenação"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg='#e2e8f0',
            fg='#475569',
            font=("Segoe UI", 8),
            padx=10,
            pady=4,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground='#cbd5e1',
            activeforeground='#1e293b'
        )
        return btn
    
    def criar_tabela(self, parent):
        """Cria a tabela de resultados"""
        # Frame para scrollbar
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Treeview (tabela) com estilo melhorado
        columns = ('IP', 'HTTP', 'HTTPS', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configura colunas
        self.tree.heading('IP', text='IP')
        self.tree.heading('HTTP', text='HTTP')
        self.tree.heading('HTTPS', text='HTTPS')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('IP', width=220, anchor=tk.W)
        self.tree.column('HTTP', width=220, anchor=tk.W)
        self.tree.column('HTTPS', width=220, anchor=tk.W)
        self.tree.column('Status', width=120, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tags para cores melhoradas
        self.tree.tag_configure('ok', background='#d1fae5', foreground='#065f46')
        self.tree.tag_configure('timeout', background='#fef3c7', foreground='#92400e')
        self.tree.tag_configure('error', background='#fee2e2', foreground='#991b1b')
    
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
        
        # Cria labels de estatísticas com estilo melhorado
        stats_container = tk.Frame(self.stats_frame, bg='white')
        stats_container.pack(fill=tk.X)
        
        def criar_stat_badge(text, bg, fg):
            frame = tk.Frame(stats_container, bg=bg, relief='flat', bd=0)
            frame.pack(side=tk.LEFT, padx=5)
            label = tk.Label(
                frame,
                text=text,
                font=("Segoe UI", 9, "bold"),
                bg=bg,
                fg=fg,
                padx=12,
                pady=6
            )
            label.pack()
            return frame
        
        criar_stat_badge(f"Total: {total}", '#e0e7ff', '#3730a3')
        criar_stat_badge(f"✅ OK: {ok} ({ok*100/total:.1f}%)", '#d1fae5', '#065f46')
        criar_stat_badge(f"⏱ Timeout: {timeout} ({timeout*100/total:.1f}%)", '#fef3c7', '#92400e')
        criar_stat_badge(f"❌ Error: {error} ({error*100/total:.1f}%)", '#fee2e2', '#991b1b')
    
    def ordenar_resultados(self, criterio):
        """Ordena os resultados por critério"""
        if not self.resultados:
            return
        
        # Alterna ordem se clicar no mesmo critério
        if self.ordem_atual == criterio:
            self.ordem_reversa = not self.ordem_reversa
        else:
            self.ordem_atual = criterio
            self.ordem_reversa = False
        
        # Ordena resultados
        if criterio == 'ip':
            def ip_key(r):
                try:
                    return ipaddress.IPv4Address(r['ip'])
                except:
                    return ipaddress.IPv4Address('0.0.0.0')
            self.resultados.sort(key=ip_key, reverse=self.ordem_reversa)
        elif criterio == 'status':
            def status_key(r):
                http = r.get('http', '')
                https = r.get('https', '')
                if 'OK' in http or 'OK' in https:
                    return 0  # OK primeiro
                elif 'Timeout' in http and 'Timeout' in https:
                    return 1  # Timeout segundo
                else:
                    return 2  # Error último
            self.resultados.sort(key=status_key, reverse=self.ordem_reversa)
        elif criterio == 'http':
            self.resultados.sort(key=lambda x: x.get('http', ''), reverse=self.ordem_reversa)
        elif criterio == 'https':
            self.resultados.sort(key=lambda x: x.get('https', ''), reverse=self.ordem_reversa)
        
        # Atualiza tabela
        self.tree.delete(*self.tree.get_children())
        for resultado in self.resultados:
            self._adicionar_resultado(resultado)
    
    def copiar_ips_ok(self):
        """Copia IPs com status OK para área de transferência"""
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum resultado disponível.")
            return
        
        ips_ok = []
        for r in self.resultados:
            http = r.get('http', '')
            https = r.get('https', '')
            if 'OK' in http or 'OK' in https:
                ips_ok.append(r['ip'])
        
        if not ips_ok:
            messagebox.showinfo("Info", "Nenhum IP com status OK encontrado.")
            return
        
        texto = '\n'.join(ips_ok)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        messagebox.showinfo("Sucesso", f"{len(ips_ok)} IP(s) com status OK copiado(s) para a área de transferência!")
    
    def copiar_ips_erro(self):
        """Copia IPs com erro para área de transferência"""
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhum resultado disponível.")
            return
        
        ips_erro = []
        for r in self.resultados:
            http = r.get('http', '')
            https = r.get('https', '')
            if 'OK' not in http and 'OK' not in https:
                ips_erro.append(r['ip'])
        
        if not ips_erro:
            messagebox.showinfo("Info", "Nenhum IP com erro encontrado.")
            return
        
        texto = '\n'.join(ips_erro)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        messagebox.showinfo("Sucesso", f"{len(ips_erro)} IP(s) com erro copiado(s) para a área de transferência!")
    
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
