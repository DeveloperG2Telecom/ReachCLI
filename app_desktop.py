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
import sys
import ctypes
import subprocess
import threading
import platform
import re
import time
import json
import os
import requests
import zipfile
import shutil

from services.http_tester import HTTPTester
from utils.file_reader import validar_ipv4
import config

# Configuração de DPI awareness para melhor nitidez (Windows)
if sys.platform == 'win32':
    try:
        # Windows 10/11 - Per Monitor DPI Aware v2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            # Windows 8.1 - System DPI Aware
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass


class AppDesktop:
    """Classe principal da aplicação desktop"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReachCLI - Sistema de Testes de Rede")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variáveis
        self.resultados = []
        self.executando = False
        self.ordem_atual = 'ip'  # 'ip', 'status', 'http', 'https'
        self.ordem_reversa = False
        self.ips_para_testar = []  # Lista de IPs sendo testados
        self.ips_testados = 0  # Contador de IPs testados
        self.tela_atual = 0  # Controle de navegação (0-4)
        self.telas = []  # Lista de frames de telas
        
        # Variáveis para DNS
        self.dns_testing = False
        self.dns_resultados = []
        self.os_type = platform.system().lower()
        
        # Variáveis para Monitoramento
        self.monitorando = False
        self.equipamentos = []
        self.monitoramento_thread = None
        self.monitoramento_intervalo = 30  # segundos
        self.config_json_path = "config.json"
        self.config_json_github_url = "https://raw.githubusercontent.com/DeveloperG2Telecom/ReachCLI/main/config.json"
        self.config_json_github_api_url = "https://api.github.com/repos/DeveloperG2Telecom/ReachCLI/contents/config.json"
        self.monitoramento_ordem_atual = None  # Coluna atual de ordenação (None = ordem padrão)
        self.monitoramento_ordem_reversa = False  # Ordem reversa
        
        # Variáveis para Atualização
        self.versao_atual = "1.0.0"  # Versão atual do software
        self.cloudflare_base_url = "https://pub-8e51d8dedc284555a7d22bfae1890f4a.r2.dev/releases"
        self.verificando_atualizacao = False  # Flag para evitar múltiplas verificações simultâneas
        
        # Espaçamentos padronizados
        self.padding_externo = 20
        self.padding_interno = 16
        self.spacing_vertical = 16
        
        # Configura estilo
        self.configurar_estilo()
        
        # Cria navbar
        self.criar_navbar()
        
        # Cria interface (telas)
        self.criar_telas()
        
        # Mostra primeira tela
        self.mostrar_tela(0)
        
        # Centraliza janela
        self.centralizar_janela()
    
    def configurar_estilo(self):
        """Configura o estilo visual da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores personalizadas modernas
        self.cor_primaria = "#2563eb"
        self.cor_primaria_hover = "#1e40af"
        self.cor_sucesso = "#10b981"
        self.cor_sucesso_hover = "#059669"
        self.cor_erro = "#ef4444"
        self.cor_erro_hover = "#dc2626"
        self.cor_timeout = "#f59e0b"
        self.cor_timeout_hover = "#d97706"
        self.cor_fundo = "#f8fafc"
        self.cor_secundaria = "#64748b"
        self.cor_secundaria_hover = "#475569"
        self.cor_borda = "#e2e8f0"
        
        # Configura cores do tema
        self.root.configure(bg=self.cor_fundo)
        
        # Estiliza ttk widgets
        style.configure('TLabelFrame', background='white', borderwidth=1, relief='flat')
        style.configure('TLabelFrame.Label', background='white', font=('Segoe UI', 14, 'bold'))
        style.configure('TFrame', background=self.cor_fundo)
        style.configure('TEntry', fieldbackground='white', borderwidth=1, relief='solid', padding=6)
        style.configure('TButton', padding=8, font=('Segoe UI', 13))
        
        # Estiliza Treeview (tabela) com fonte maior e arredondada
        style.configure('Treeview', font=('Segoe UI', 13), rowheight=30)
        style.configure('Treeview.Heading', font=('Segoe UI', 13, 'bold'))
        
        # Estiliza progressbar
        style.configure('TProgressbar', thickness=4, borderwidth=0, background=self.cor_primaria)
    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def criar_navbar(self):
        """Cria o navbar superior com 6 botões de navegação"""
        navbar_frame = tk.Frame(self.root, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        navbar_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Container para os botões
        buttons_container = tk.Frame(navbar_frame, bg='white')
        buttons_container.pack(fill=tk.X, padx=self.padding_externo, pady=12)
        
        # Lista de nomes das telas
        telas_nomes = [
            "📡 MONITORAMENTO",
            "🌐 HTTP/HTTPS",
            "🔒 Bloqueio DNS",
            "🔍 Port Scanner",
            "📊 Relatórios",
            "⚙️ Configurações"
        ]
        
        self.navbar_buttons = []
        for i, nome in enumerate(telas_nomes):
            btn = self.criar_botao_navbar(buttons_container, nome, i)
            btn.pack(side=tk.LEFT, padx=(0, 8))
            self.navbar_buttons.append(btn)
        
        # Container para conteúdo das telas
        self.content_container = tk.Frame(self.root, bg=self.cor_fundo)
        self.content_container.pack(fill=tk.BOTH, expand=True)
    
    def criar_botao_navbar(self, parent, text, index):
        """Cria um botão do navbar"""
        btn_bg = '#f1f5f9'
        btn_bg_hover = '#e2e8f0'
        btn_fg = '#475569'
        
        btn = tk.Button(
            parent,
            text=text,
            command=lambda: self.mostrar_tela(index),
            bg=btn_bg,
            fg=btn_fg,
            font=("Segoe UI", 13, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=btn_bg_hover,
            activeforeground=btn_fg,
            highlightthickness=0
        )
        
        # Hover
        def on_enter(e):
            if self.tela_atual != index:
                btn.config(bg=btn_bg_hover)
        def on_leave(e):
            if self.tela_atual != index:
                btn.config(bg=btn_bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def atualizar_navbar(self):
        """Atualiza os botões do navbar para mostrar o botão ativo"""
        for i, btn in enumerate(self.navbar_buttons):
            if i == self.tela_atual:
                btn.config(bg=self.cor_primaria, fg='white')
            else:
                btn.config(bg='#f1f5f9', fg='#475569')
    
    def mostrar_tela(self, index):
        """Mostra a tela selecionada e esconde as outras"""
        self.tela_atual = index
        
        # Esconde todas as telas
        for tela in self.telas:
            tela.pack_forget()
        
        # Mostra a tela selecionada
        if 0 <= index < len(self.telas):
            self.telas[index].pack(fill=tk.BOTH, expand=True)
        
        # Atualiza navbar
        self.atualizar_navbar()
    
    def criar_telas(self):
        """Cria todas as 6 telas"""
        # Tela 1: MONITORAMENTO
        tela_monitoramento = tk.Frame(self.content_container, bg=self.cor_fundo)
        self.criar_tela_monitoramento(tela_monitoramento)
        self.telas.append(tela_monitoramento)
        
        # Tela 2: HTTP/HTTPS
        tela_http = tk.Frame(self.content_container, bg=self.cor_fundo)
        self.criar_tela_http(tela_http)
        self.telas.append(tela_http)
        
        # Tela 3: Bloqueio DNS
        tela_dns = tk.Frame(self.content_container, bg=self.cor_fundo)
        self.criar_tela_dns(tela_dns)
        self.telas.append(tela_dns)
        
        # Tela 4: Port Scanner
        tela_port = tk.Frame(self.content_container, bg=self.cor_fundo)
        self.criar_tela_port(tela_port)
        self.telas.append(tela_port)
        
        # Tela 5: Relatórios
        tela_relatorios = tk.Frame(self.content_container, bg=self.cor_fundo)
        self.criar_tela_relatorios(tela_relatorios)
        self.telas.append(tela_relatorios)
        
        # Tela 6: Configurações
        tela_configuracoes = tk.Frame(self.content_container, bg=self.cor_fundo)
        self.criar_tela_configuracoes(tela_configuracoes)
        self.telas.append(tela_configuracoes)
    
    def criar_tela_http(self, parent):
        """Cria a tela de teste HTTP/HTTPS"""
        
        # Frame principal com padding padronizado e layout responsivo
        main_frame = tk.Frame(parent, bg=self.cor_fundo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        
        # Configura grid para responsividade
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)  # Linha dos resultados
        
        # Título
        title_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        title_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        
        title_label = tk.Label(
            title_frame,
            text="🌐 Teste de Conectividade HTTP/HTTPS",
            font=("Segoe UI", 29, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Sistema de teste para clientes IPv4",
            font=("Segoe UI", 15),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle_label.pack(pady=(6, 0))
        
        # Frame de configurações
        config_frame = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        config_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        config_frame.grid_columnconfigure(0, weight=1)
        
        config_title = tk.Label(
            config_frame,
            text="⚙️ Configurações",
            font=("Segoe UI", 15, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        config_title.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(self.padding_interno, 8))
        
        config_inner = tk.Frame(config_frame, bg='white')
        config_inner.grid(row=1, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, self.padding_interno))
        
        # Portas (múltiplas, separadas por vírgula)
        tk.Label(config_inner, text="Portas:", bg='white', font=("Segoe UI", 13)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        portas_padrao_str = ', '.join(map(str, config.PORTAS_PADRAO))
        self.portas_var = tk.StringVar(value=portas_padrao_str)
        portas_entry = tk.Entry(config_inner, textvariable=self.portas_var, width=40, font=("Segoe UI", 13), 
                               relief='solid', bd=1, highlightthickness=0, highlightbackground=self.cor_borda)
        portas_entry.grid(row=0, column=1, padx=(0, 24), sticky=tk.W)
        
        # Timeout
        tk.Label(config_inner, text="Timeout (segundos):", bg='white', font=("Segoe UI", 13)).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.timeout_var = tk.StringVar(value=str(config.TIMEOUT_PADRAO))
        timeout_entry = tk.Entry(config_inner, textvariable=self.timeout_var, width=12, font=("Segoe UI", 13),
                                relief='solid', bd=1, highlightthickness=0, highlightbackground=self.cor_borda)
        timeout_entry.grid(row=0, column=3, padx=(0, 24))
        
        # Verificar SSL
        self.verificar_ssl_var = tk.BooleanVar(value=config.VERIFICAR_SSL)
        ssl_check = tk.Checkbutton(
            config_inner,
            text="Verificar SSL",
            variable=self.verificar_ssl_var,
            bg='white',
            font=("Segoe UI", 13),
            activebackground='white',
            selectcolor='white'
        )
        ssl_check.grid(row=0, column=4, sticky=tk.W)
        
        # Frame de entrada de IPs
        input_frame = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        input_frame.grid(row=2, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(1, weight=1)
        
        input_title = tk.Label(
            input_frame,
            text="📝 Lista de IPs",
            font=("Segoe UI", 15, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        input_title.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(self.padding_interno, 8))
        
        # Textarea para IPs
        text_frame = tk.Frame(input_frame, bg='white')
        text_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=self.padding_interno, pady=(0, self.padding_interno))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.ips_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            font=("Consolas", 14),
            wrap=tk.WORD,
            relief='solid',
            bd=1,
            bg='#fafafa',
            fg='#1e293b',
            insertbackground=self.cor_primaria,
            highlightthickness=0
        )
        self.ips_text.grid(row=0, column=0, sticky=tk.NSEW)
        self.ips_text.insert("1.0", "187.10.10.1\n200.150.30.5\n179.40.22.9")
        
        # Botões de ação
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.grid(row=2, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, self.padding_interno))
        
        self.btn_testar = self.criar_botao(
            button_frame,
            "▶ Executar Testes",
            self.executar_testes,
            self.cor_primaria,
            self.cor_primaria_hover,
            bold=True
        )
        self.btn_testar.pack(side=tk.LEFT, padx=(0, 12))
        
        self.btn_parar = self.criar_botao(
            button_frame,
            "⏹ PARE",
            self.parar_testes,
            "#e2e8f0",
            "#cbd5e1",
            small=True
        )
        self.btn_parar.pack(side=tk.LEFT, padx=(0, 12))
        self.btn_parar.config(state=tk.DISABLED, fg="#64748b")
        
        btn_limpar = self.criar_botao(
            button_frame,
            "🗑 Limpar",
            self.limpar,
            "#e2e8f0",
            "#cbd5e1",
            small=True
        )
        btn_limpar.pack(side=tk.LEFT)
        btn_limpar.config(fg="#64748b")
        
        # Barra de progresso (entre input e resultados)
        progress_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        progress_frame.grid(row=3, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para progresso e status
        progress_inner = tk.Frame(progress_frame, bg=self.cor_fundo)
        progress_inner.grid(row=0, column=0, sticky=tk.EW)
        progress_inner.grid_columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(
            progress_inner,
            mode='indeterminate',
            style='TProgressbar'
        )
        self.progress.grid(row=0, column=0, sticky=tk.EW)
        
        # Label sutil para mostrar IP sendo testado e progressão (no canto)
        self.progress_status_label = tk.Label(
            progress_inner,
            text="",
            font=("Segoe UI", 13),
            fg="#64748b",
            bg=self.cor_fundo,
            anchor=tk.E
        )
        self.progress_status_label.grid(row=0, column=1, sticky=tk.E, padx=(8, 0))
        
        # Frame de resultados
        resultados_frame = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        resultados_frame.grid(row=4, column=0, sticky=tk.NSEW)
        resultados_frame.grid_columnconfigure(0, weight=1)
        resultados_frame.grid_rowconfigure(3, weight=1)  # Linha da tabela
        
        resultados_title = tk.Label(
            resultados_frame,
            text="📊 Resultados",
            font=("Segoe UI", 15, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        resultados_title.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(self.padding_interno, 8))
        
        # Frame para botões de ação dos resultados
        resultados_actions = tk.Frame(resultados_frame, bg='white')
        resultados_actions.grid(row=1, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, 12))
        resultados_actions.grid_columnconfigure(0, weight=1)
        
        # Botões de ordenação
        ordenar_frame = tk.Frame(resultados_actions, bg='white')
        ordenar_frame.grid(row=0, column=0, sticky=tk.W)
        
        tk.Label(ordenar_frame, text="Ordenar por:", bg='white', font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=(0, 10))
        
        btn_ord_ip = self.criar_botao_pequeno(ordenar_frame, "IP", lambda: self.ordenar_resultados('ip'))
        btn_ord_ip.pack(side=tk.LEFT, padx=(0, 6))
        
        btn_ord_status = self.criar_botao_pequeno(ordenar_frame, "Status", lambda: self.ordenar_resultados('status'))
        btn_ord_status.pack(side=tk.LEFT)
        
        # Botões de cópia
        copiar_frame = tk.Frame(resultados_actions, bg='white')
        copiar_frame.grid(row=0, column=1, sticky=tk.E)
        
        btn_copiar_ok = self.criar_botao(
            copiar_frame,
            "✅ Copiar IPs OK",
            self.copiar_ips_ok,
            self.cor_sucesso,
            self.cor_sucesso_hover,
            small=True
        )
        btn_copiar_ok.pack(side=tk.LEFT, padx=(0, 8))
        
        btn_exportar = self.criar_botao(
            copiar_frame,
            "📥 Exportar CSV",
            self.exportar_csv,
            self.cor_sucesso,
            self.cor_sucesso_hover,
            small=True
        )
        btn_exportar.pack(side=tk.LEFT, padx=(0, 8))
        
        btn_copiar_erro = self.criar_botao(
            copiar_frame,
            "❌ Copiar IPs Erro",
            self.copiar_ips_erro,
            self.cor_erro,
            self.cor_erro_hover,
            small=True
        )
        btn_copiar_erro.pack(side=tk.LEFT)
        
        # Estatísticas
        self.stats_frame = tk.Frame(resultados_frame, bg='white')
        self.stats_frame.grid(row=2, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, 12))
        
        # Tabela de resultados
        self.criar_tabela(resultados_frame)
    
    def criar_tela_dns(self, parent):
        """Cria a tela de teste de bloqueio DNS"""
        
        # Frame principal com padding padronizado e layout responsivo
        main_frame = tk.Frame(parent, bg=self.cor_fundo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        
        # Configura grid para responsividade
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)  # Linha dos resultados
        
        # Título
        title_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        title_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        
        title_label = tk.Label(
            title_frame,
            text="🔒 Teste de Bloqueio DNS",
            font=("Segoe UI", 29, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Sistema de teste para bloqueio de domínios",
            font=("Segoe UI", 15),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle_label.pack(pady=(6, 0))
        
        # Frame de entrada de domínios
        input_frame = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        input_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(1, weight=1)
        
        input_title = tk.Label(
            input_frame,
            text="📝 Lista de Domínios",
            font=("Segoe UI", 15, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        input_title.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(self.padding_interno, 8))
        
        # Textarea para domínios
        text_frame = tk.Frame(input_frame, bg='white')
        text_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=self.padding_interno, pady=(0, self.padding_interno))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.dns_domains_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            font=("Consolas", 14),
            wrap=tk.WORD,
            relief='solid',
            bd=1,
            bg='#fafafa',
            fg='#1e293b',
            insertbackground=self.cor_primaria,
            highlightthickness=0
        )
        self.dns_domains_text.grid(row=0, column=0, sticky=tk.NSEW)
        self.dns_domains_text.insert("1.0", "google.com\nyoutube.com\nfacebook.com")
        
        # Botões de ação
        button_frame = tk.Frame(input_frame, bg='white')
        button_frame.grid(row=2, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, self.padding_interno))
        
        self.btn_testar_dns = self.criar_botao(
            button_frame,
            "▶ Executar Testes DNS",
            self.executar_testes_dns,
            self.cor_primaria,
            self.cor_primaria_hover,
            bold=True
        )
        self.btn_testar_dns.pack(side=tk.LEFT, padx=(0, 12))
        
        btn_limpar_dns = self.criar_botao(
            button_frame,
            "🗑 Limpar",
            self.limpar_dns,
            self.cor_secundaria,
            self.cor_secundaria_hover
        )
        btn_limpar_dns.pack(side=tk.LEFT)
        
        # Barra de progresso
        progress_frame_dns = tk.Frame(main_frame, bg=self.cor_fundo)
        progress_frame_dns.grid(row=2, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        progress_frame_dns.grid_columnconfigure(0, weight=1)
        
        self.progress_dns = ttk.Progressbar(
            progress_frame_dns,
            mode='indeterminate',
            style='TProgressbar'
        )
        self.progress_dns.grid(row=0, column=0, sticky=tk.EW)
        
        # Frame de resultados
        resultados_frame_dns = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        resultados_frame_dns.grid(row=3, column=0, sticky=tk.NSEW)
        resultados_frame_dns.grid_columnconfigure(0, weight=1)
        resultados_frame_dns.grid_rowconfigure(3, weight=1)  # Linha da tabela
        
        resultados_title_dns = tk.Label(
            resultados_frame_dns,
            text="📊 Resultados",
            font=("Segoe UI", 15, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        resultados_title_dns.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(self.padding_interno, 8))
        
        # Frame para botões de ação dos resultados
        resultados_actions_dns = tk.Frame(resultados_frame_dns, bg='white')
        resultados_actions_dns.grid(row=1, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, 12))
        resultados_actions_dns.grid_columnconfigure(0, weight=1)
        
        # Botões de cópia
        copiar_frame_dns = tk.Frame(resultados_actions_dns, bg='white')
        copiar_frame_dns.grid(row=0, column=0, sticky=tk.E)
        
        btn_copiar_acessivel = self.criar_botao(
            copiar_frame_dns,
            "✅ Copiar Acessíveis",
            self.copiar_dns_acessiveis,
            self.cor_sucesso,
            self.cor_sucesso_hover,
            small=True
        )
        btn_copiar_acessivel.pack(side=tk.LEFT, padx=(0, 8))
        
        btn_copiar_bloqueado = self.criar_botao(
            copiar_frame_dns,
            "❌ Copiar Bloqueados",
            self.copiar_dns_bloqueados,
            self.cor_erro,
            self.cor_erro_hover,
            small=True
        )
        btn_copiar_bloqueado.pack(side=tk.LEFT)
        
        # Estatísticas
        self.stats_frame_dns = tk.Frame(resultados_frame_dns, bg='white')
        self.stats_frame_dns.grid(row=2, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(0, 12))
        
        # Tabela de resultados
        self.criar_tabela_dns(resultados_frame_dns)
        
        # Botão exportar
        exportar_frame_dns = tk.Frame(resultados_frame_dns, bg='white')
        exportar_frame_dns.grid(row=4, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(12, self.padding_interno))
        
        btn_exportar_dns = self.criar_botao(
            exportar_frame_dns,
            "💾 Exportar Resultados",
            self.exportar_dns,
            self.cor_sucesso,
            self.cor_sucesso_hover
        )
        btn_exportar_dns.pack()
    
    def criar_tabela_dns(self, parent):
        """Cria a tabela de resultados DNS"""
        # Frame para scrollbar com grid
        table_frame = tk.Frame(parent, bg='white')
        table_frame.grid(row=3, column=0, sticky=tk.NSEW, padx=self.padding_interno, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview (tabela) com estilo melhorado
        columns = ('Status', 'Domínio', 'Tempo (ms)', 'Resposta')
        self.tree_dns = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configura colunas
        self.tree_dns.heading('Status', text='Status')
        self.tree_dns.heading('Domínio', text='Domínio')
        self.tree_dns.heading('Tempo (ms)', text='Tempo (ms)')
        self.tree_dns.heading('Resposta', text='Resposta')
        
        self.tree_dns.column('Status', width=150, anchor=tk.CENTER, minwidth=120)
        self.tree_dns.column('Domínio', width=250, anchor=tk.W, minwidth=200)
        self.tree_dns.column('Tempo (ms)', width=120, anchor=tk.CENTER, minwidth=100)
        self.tree_dns.column('Resposta', width=250, anchor=tk.W, minwidth=200)
        
        # Scrollbar
        scrollbar_dns = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_dns.yview)
        self.tree_dns.configure(yscrollcommand=scrollbar_dns.set)
        
        # Grid
        self.tree_dns.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar_dns.grid(row=0, column=1, sticky=tk.NS)
        
        # Tags para cores
        self.tree_dns.tag_configure('acessivel', foreground='#059669')
        self.tree_dns.tag_configure('bloqueado', foreground='#dc2626')
    
    def validar_dominio_dns(self, domain):
        """Valida se o domínio tem formato válido"""
        domain = domain.strip()
        if not domain:
            return False
        
        # Regex simples para validar domínio
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def ping_dominio_dns(self, domain):
        """Executa ping no domínio e retorna o resultado com tempo de resposta"""
        domain = domain.strip()
        if not domain:
            return None, "Domínio vazio", None
        
        try:
            # Configurar comando ping baseado no OS (timeout de 5 segundos)
            if self.os_type == 'windows':
                cmd = ['ping', '-n', '2', '-w', '5000', domain]
            else:
                cmd = ['ping', '-c', '2', '-W', '5', domain]
            
            # Configurar flags para ocultar janela do CMD no Windows
            creation_flags = 0
            if self.os_type == 'windows':
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            # Medir tempo de resposta
            start_time = time.time()
            
            # Executar ping com timeout (ocultando janela do CMD)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=creation_flags
            )
            
            elapsed_time = time.time() - start_time
            elapsed_ms = int(elapsed_time * 1000)
            
            # Verificar resultado
            if result.returncode == 0:
                # Tentar extrair tempo médio do ping (se disponível)
                ping_time = self.extract_ping_time_dns(result.stdout, elapsed_ms)
                return True, "Acessível", ping_time
            else:
                return False, "Bloqueado ou inacessível", None
                
        except subprocess.TimeoutExpired:
            return False, "Timeout - Domínio não respondeu", None
        except Exception as e:
            return False, f"Erro: {str(e)}", None
    
    def extract_ping_time_dns(self, output, fallback_time):
        """Extrai o tempo médio do ping da saída do comando"""
        try:
            if self.os_type == 'windows':
                # Windows: "Média = XXXms"
                match = re.search(r'Média\s*=\s*(\d+)ms', output, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            else:
                # Linux/macOS: "min/avg/max/mdev = X.XXX/X.XXX/X.XXX/X.XXX ms"
                match = re.search(r'min/avg/max/[^=]*=\s*[\d.]+/([\d.]+)/[\d.]+', output)
                if match:
                    return int(float(match.group(1)) * 1000)
        except:
            pass
        
        # Retornar tempo medido como fallback
        return fallback_time
    
    def executar_testes_dns(self):
        """Inicia o teste de domínios em thread separada"""
        if self.dns_testing:
            return
        
        # Limpar resultados anteriores
        for item in self.tree_dns.get_children():
            self.tree_dns.delete(item)
        self.dns_resultados = []
        
        # Obter domínios do campo de texto
        domains_text = self.dns_domains_text.get("1.0", tk.END)
        domains = [d.strip() for d in domains_text.split('\n') if d.strip()]
        
        if not domains:
            messagebox.showwarning("Aviso", "Por favor, insira pelo menos um domínio para testar.")
            return
        
        # Filtrar domínios válidos
        valid_domains = []
        invalid_domains = []
        
        for domain in domains:
            if self.validar_dominio_dns(domain):
                valid_domains.append(domain)
            else:
                invalid_domains.append(domain)
        
        if not valid_domains:
            messagebox.showerror("Erro", "Nenhum domínio válido encontrado. Verifique o formato dos domínios.")
            return
        
        if invalid_domains:
            invalid_list = '\n'.join(invalid_domains[:5])
            if len(invalid_domains) > 5:
                invalid_list += f"\n... e mais {len(invalid_domains) - 5} domínio(s)"
            messagebox.showwarning(
                "Aviso", 
                f"Os seguintes domínios foram ignorados (formato inválido):\n\n{invalid_list}"
            )
        
        # Iniciar teste em thread separada
        self.dns_testing = True
        self.btn_testar_dns.config(state=tk.DISABLED, text="⏸ Testando...")
        self.progress_dns.start()
        
        thread = threading.Thread(target=self.run_testes_dns, args=(valid_domains,))
        thread.daemon = True
        thread.start()
    
    def run_testes_dns(self, domains):
        """Executa os testes de ping para cada domínio"""
        total = len(domains)
        accessible = 0
        blocked = 0
        
        for i, domain in enumerate(domains):
            if not self.dns_testing:  # Verificar se foi cancelado
                break
            
            # Executar ping
            is_accessible, response, ping_time = self.ping_dominio_dns(domain)
            
            # Atualizar contadores
            if is_accessible:
                accessible += 1
                status = "✓ Acessível"
            else:
                blocked += 1
                status = "✗ Bloqueado"
            
            # Atualizar interface na thread principal
            self.root.after(0, self.update_result_dns, domain, status, response, is_accessible, ping_time)
        
        # Finalizar
        self.root.after(0, self.finish_test_dns, total, accessible, blocked)
    
    def update_result_dns(self, domain, status, response, is_accessible, ping_time):
        """Atualiza a interface com resultado de um domínio"""
        # Formatar tempo
        time_str = str(ping_time) if ping_time is not None else "-"
        
        # Determinar tag baseada no status
        tag = 'acessivel' if is_accessible else 'bloqueado'
        
        # Inserir item
        self.tree_dns.insert('', tk.END, values=(status, domain, time_str, response), tags=(tag,))
        
        # Armazenar resultado
        self.dns_resultados.append({
            'domain': domain,
            'status': status,
            'response': response,
            'time': ping_time,
            'accessible': is_accessible
        })
    
    def finish_test_dns(self, total, accessible, blocked):
        """Finaliza o teste e atualiza estatísticas"""
        self.dns_testing = False
        self.progress_dns.stop()
        
        # Restaurar botão
        self.btn_testar_dns.config(state=tk.NORMAL, text="▶ Executar Testes DNS")
        
        # Atualizar estatísticas
        stats_text = f"📈 Total: {total}  |  ✅ Acessíveis: {accessible}  |  ❌ Bloqueados: {blocked}"
        
        # Limpar frame de estatísticas
        for widget in self.stats_frame_dns.winfo_children():
            widget.destroy()
        
        stats_label = tk.Label(
            self.stats_frame_dns,
            text=stats_text,
            font=("Segoe UI", 14),
            bg='white',
            fg=self.cor_primaria
        )
        stats_label.pack()
    
    def limpar_dns(self):
        """Limpa os campos e resultados DNS"""
        self.dns_domains_text.delete("1.0", tk.END)
        self.tree_dns.delete(*self.tree_dns.get_children())
        self.dns_resultados = []
        
        # Limpar estatísticas
        for widget in self.stats_frame_dns.winfo_children():
            widget.destroy()
    
    def copiar_dns_acessiveis(self):
        """Copia domínios acessíveis para a área de transferência"""
        acessiveis = [r['domain'] for r in self.dns_resultados if r['accessible']]
        if not acessiveis:
            messagebox.showinfo("Info", "Nenhum domínio acessível encontrado.")
            return
        
        text = '\n'.join(acessiveis)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copiado", f"{len(acessiveis)} domínio(s) acessível(is) copiado(s) para a área de transferência.")
    
    def copiar_dns_bloqueados(self):
        """Copia domínios bloqueados para a área de transferência"""
        bloqueados = [r['domain'] for r in self.dns_resultados if not r['accessible']]
        if not bloqueados:
            messagebox.showinfo("Info", "Nenhum domínio bloqueado encontrado.")
            return
        
        text = '\n'.join(bloqueados)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copiado", f"{len(bloqueados)} domínio(s) bloqueado(s) copiado(s) para a área de transferência.")
    
    def exportar_dns(self):
        """Exporta resultados DNS para arquivo de texto"""
        if not self.dns_resultados:
            messagebox.showwarning("Aviso", "Nenhum resultado para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Salvar resultados DNS"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("BlockDNS - Resultados do Teste\n")
                f.write("=" * 60 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                # Estatísticas
                accessible = len([r for r in self.dns_resultados if r['accessible']])
                blocked = len([r for r in self.dns_resultados if not r['accessible']])
                total = len(self.dns_resultados)
                f.write(f"Total: {total} | Acessíveis: {accessible} | Bloqueados: {blocked}\n\n")
                
                # Domínios acessíveis
                f.write("=" * 60 + "\n")
                f.write("DOMÍNIOS ACESSÍVEIS\n")
                f.write("=" * 60 + "\n")
                for result in self.dns_resultados:
                    if result['accessible']:
                        time_str = f" ({result['time']} ms)" if result['time'] is not None else ""
                        f.write(f"{result['domain']}{time_str}\n")
                
                f.write("\n")
                
                # Domínios bloqueados
                f.write("=" * 60 + "\n")
                f.write("DOMÍNIOS BLOQUEADOS\n")
                f.write("=" * 60 + "\n")
                for result in self.dns_resultados:
                    if not result['accessible']:
                        f.write(f"{result['domain']}\n")
                
                f.write("\n")
                
                # Detalhes completos
                f.write("=" * 60 + "\n")
                f.write("DETALHES COMPLETOS\n")
                f.write("=" * 60 + "\n")
                for result in self.dns_resultados:
                    time_str = f"{result['time']} ms" if result['time'] is not None else "-"
                    f.write(f"{result['status']} | {result['domain']} | {time_str} | {result['response']}\n")
            
            messagebox.showinfo("Sucesso", f"Resultados exportados para:\n{filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar resultados:\n{str(e)}")
    
    def criar_tela_monitoramento(self, parent):
        """Cria a tela de Monitoramento de Equipamentos"""
        # Frame principal
        main_frame = tk.Frame(parent, bg=self.cor_fundo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Título
        title_frame = tk.Frame(main_frame, bg=self.cor_fundo)
        title_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        
        title_label = tk.Label(
            title_frame,
            text="📡 MONITORAMENTO DE EQUIPAMENTOS",
            font=("Segoe UI", 29, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Monitoramento contínuo de equipamentos de rede",
            font=("Segoe UI", 15),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle_label.pack(pady=(6, 0))
        
        # Frame de controles
        controles_frame = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        controles_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, self.spacing_vertical))
        controles_frame.grid_columnconfigure(1, weight=1)
        
        controles_inner = tk.Frame(controles_frame, bg='white')
        controles_inner.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=self.padding_interno)
        controles_inner.grid_columnconfigure(1, weight=1)
        
        # Frame para botões à esquerda
        botoes_left_frame = tk.Frame(controles_inner, bg='white')
        botoes_left_frame.grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        
        # Botão Iniciar/Parar (estilo moderno - apenas ícone, tamanho maior)
        self.btn_monitorar_frame = self.criar_botao_moderno(
            botoes_left_frame,
            "Iniciar Monitoramento",
            self.toggle_monitoramento,
            cor_bg="#d1fae5",
            cor_fg="#065f46",
            cor_hover_bg="#a7f3d0",
            cor_hover_fg="#047857",
            icon="▶",
            apenas_icone=True,
            tamanho_icone=20
        )
        self.btn_monitorar_frame.pack(side=tk.LEFT, padx=(0, 12))
        self.btn_monitorar = self.btn_monitorar_frame._btn_interno  # Referência ao botão interno
        
        # Botão Adicionar Equipamento (estilo moderno - apenas ícone, tamanho maior)
        btn_adicionar = self.criar_botao_moderno(
            botoes_left_frame,
            "Adicionar",
            self.adicionar_equipamento,
            cor_bg="#dbeafe",
            cor_fg="#1e40af",
            cor_hover_bg="#bfdbfe",
            cor_hover_fg="#1e3a8a",
            icon="➕",
            apenas_icone=True,
            tamanho_icone=20
        )
        btn_adicionar.pack(side=tk.LEFT, padx=(0, 12))
        
        # Botão Atualizar do GitHub (estilo moderno - apenas ícone, tamanho maior)
        btn_atualizar = self.criar_botao_moderno(
            botoes_left_frame,
            "Atualizar do GitHub",
            self.atualizar_do_github,
            cor_bg="#f1f5f9",
            cor_fg="#475569",
            cor_hover_bg="#e2e8f0",
            cor_hover_fg="#1e293b",
            icon="🔄",
            apenas_icone=True,
            tamanho_icone=20
        )
        btn_atualizar.pack(side=tk.LEFT)
        
        # Frame para intervalo à direita
        intervalo_frame = tk.Frame(controles_inner, bg='white')
        intervalo_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Label acima do input
        intervalo_label = tk.Label(
            intervalo_frame,
            text="Intervalo (segundos):",
            bg='white',
            font=("Segoe UI", 13),
            fg="#64748b"
        )
        intervalo_label.pack(anchor=tk.W, pady=(0, 4))
        
        # Input estilizado melhorado
        self.intervalo_var = tk.StringVar(value=str(self.monitoramento_intervalo))
        intervalo_entry = tk.Entry(
            intervalo_frame,
            textvariable=self.intervalo_var,
            width=14,
            font=("Segoe UI", 14),
            relief='solid',
            bd=1,
            highlightthickness=2,
            highlightbackground="#e2e8f0",
            highlightcolor="#2563eb",
            bg="#ffffff",
            fg="#1e293b",
            insertbackground="#1e293b",
            justify=tk.CENTER
        )
        intervalo_entry.pack(anchor=tk.W)
        
        # Adicionar evento de foco para melhorar visual
        def on_entry_focus_in(e):
            intervalo_entry.config(highlightbackground="#2563eb")
        def on_entry_focus_out(e):
            intervalo_entry.config(highlightbackground="#e2e8f0")
        
        intervalo_entry.bind("<FocusIn>", on_entry_focus_in)
        intervalo_entry.bind("<FocusOut>", on_entry_focus_out)
        
        # Frame de resultados
        resultados_frame = tk.Frame(main_frame, bg='white', relief='flat', highlightbackground=self.cor_borda, highlightthickness=1)
        resultados_frame.grid(row=2, column=0, sticky=tk.NSEW)
        resultados_frame.grid_columnconfigure(0, weight=1)
        resultados_frame.grid_rowconfigure(1, weight=1)
        
        resultados_title = tk.Label(
            resultados_frame,
            text="📊 Equipamentos Monitorados",
            font=("Segoe UI", 15, "bold"),
            bg='white',
            fg=self.cor_primaria,
            anchor='w'
        )
        resultados_title.grid(row=0, column=0, sticky=tk.EW, padx=self.padding_interno, pady=(self.padding_interno, 8))
        
        # Tabela de equipamentos
        self.criar_tabela_monitoramento(resultados_frame)
        
        # Carregar equipamentos do JSON (tenta baixar do GitHub na primeira carga)
        try:
            print("Iniciando carregamento de configuração...")
            self.carregar_configuracao(tentar_github=True)
        except Exception as e:
            print(f"Erro ao carregar configuração inicial: {str(e)}")
            import traceback
            traceback.print_exc()
            # Se falhar, carregar do arquivo local
            try:
                self.carregar_configuracao(tentar_github=False)
            except Exception as e2:
                print(f"Erro ao carregar do arquivo local: {str(e2)}")
                self.equipamentos = []
    
    def criar_tabela_monitoramento(self, parent):
        """Cria a tabela de monitoramento de equipamentos"""
        table_frame = tk.Frame(parent, bg='white')
        table_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=self.padding_interno, pady=(0, self.padding_interno))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview (tabela)
        columns = ('Categoria', 'Nome', 'IP', 'Status', 'Latência', 'Última Verificação')
        self.tree_monitoramento = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configura colunas com ordenação ao clicar
        self.tree_monitoramento.heading('Categoria', text='Categoria', command=lambda: self.ordenar_tabela_monitoramento('Categoria'))
        self.tree_monitoramento.heading('Nome', text='Nome', command=lambda: self.ordenar_tabela_monitoramento('Nome'))
        self.tree_monitoramento.heading('IP', text='IP', command=lambda: self.ordenar_tabela_monitoramento('IP'))
        self.tree_monitoramento.heading('Status', text='Status', command=lambda: self.ordenar_tabela_monitoramento('Status'))
        self.tree_monitoramento.heading('Latência', text='Latência (ms)', command=lambda: self.ordenar_tabela_monitoramento('Latência'))
        self.tree_monitoramento.heading('Última Verificação', text='Última Verificação', command=lambda: self.ordenar_tabela_monitoramento('Última Verificação'))
        
        self.tree_monitoramento.column('Categoria', width=120, anchor=tk.W, minwidth=100)
        self.tree_monitoramento.column('Nome', width=200, anchor=tk.W, minwidth=150)
        self.tree_monitoramento.column('IP', width=150, anchor=tk.CENTER, minwidth=120)
        self.tree_monitoramento.column('Status', width=100, anchor=tk.CENTER, minwidth=80)
        self.tree_monitoramento.column('Latência', width=120, anchor=tk.CENTER, minwidth=100)
        self.tree_monitoramento.column('Última Verificação', width=180, anchor=tk.CENTER, minwidth=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_monitoramento.yview)
        self.tree_monitoramento.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.tree_monitoramento.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # Tags para cores (com fundo verde/vermelho e texto)
        self.tree_monitoramento.tag_configure('online', background='#d1fae5', foreground='#065f46')
        self.tree_monitoramento.tag_configure('offline', background='#fee2e2', foreground='#991b1b')
        self.tree_monitoramento.tag_configure('unknown', background='#f3f4f6', foreground='#6b7280')
        
        # Menu de contexto para editar/deletar
        self.menu_contexto_monitoramento = tk.Menu(self.root, tearoff=0)
        self.menu_contexto_monitoramento.add_command(label="✏️ Editar", command=self.editar_equipamento_selecionado)
        self.menu_contexto_monitoramento.add_command(label="🗑️ Deletar", command=self.deletar_equipamento_selecionado)
        
        # Bind eventos
        self.tree_monitoramento.bind("<Button-3>", self.mostrar_menu_contexto_monitoramento)  # Botão direito
        self.tree_monitoramento.bind("<Double-1>", lambda e: self.editar_equipamento_selecionado())  # Duplo clique
    
    def baixar_config_do_github(self):
        """Baixa o arquivo config.json do GitHub e salva localmente"""
        try:
            # Adicionar timestamp à URL para evitar cache
            timestamp = int(time.time() * 1000)  # Timestamp em milissegundos
            url_com_timestamp = f"{self.config_json_github_url}?t={timestamp}"
            
            print(f"Tentando baixar de: {self.config_json_github_url}")
            # Fazer requisição para o GitHub com headers para evitar cache
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url_com_timestamp, timeout=10, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            response.raise_for_status()  # Levanta exceção se status não for 200
            
            # Validar se é um JSON válido
            config_data = response.json()
            print(f"JSON recebido com {len(config_data.get('equipamentos', []))} equipamentos")
            
            # Validar estrutura básica
            if 'equipamentos' not in config_data:
                return False, "JSON do GitHub não contém campo 'equipamentos'"
            
            # Comparar com arquivo local (se existir) para verificar se mudou
            arquivo_mudou = True
            if os.path.exists(self.config_json_path):
                try:
                    with open(self.config_json_path, 'r', encoding='utf-8') as f:
                        dados_locais = json.load(f)
                    # Comparar apenas os dados permanentes (equipamentos)
                    equipamentos_locais = dados_locais.get('equipamentos', [])
                    equipamentos_github = config_data.get('equipamentos', [])
                    
                    # Comparar tamanho primeiro
                    if len(equipamentos_locais) == len(equipamentos_github):
                        # Comparar conteúdo (ordenar para comparar independente da ordem)
                        locais_ordenados = sorted(equipamentos_locais, key=lambda x: str(x))
                        github_ordenados = sorted(equipamentos_github, key=lambda x: str(x))
                        if locais_ordenados == github_ordenados:
                            arquivo_mudou = False
                            print("⚠️ Arquivo do GitHub é idêntico ao local (pode ser cache do GitHub)")
                except Exception as e:
                    print(f"Erro ao comparar com arquivo local: {e}")
            
            # Salvar no arquivo local (sempre sobrescrever)
            print(f"Salvando arquivo em: {os.path.abspath(self.config_json_path)}")
            with open(self.config_json_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Forçar sincronização do sistema de arquivos
            import sys
            if hasattr(sys, 'flush'):
                sys.stdout.flush()
            if os.name == 'nt':  # Windows
                import ctypes
                try:
                    ctypes.windll.kernel32.FlushFileBuffers(-1)
                except:
                    pass
            
            # Verificar se o arquivo foi realmente salvo
            if os.path.exists(self.config_json_path):
                with open(self.config_json_path, 'r', encoding='utf-8') as f:
                    dados_verificacao = json.load(f)
                    print(f"Arquivo verificado: {len(dados_verificacao.get('equipamentos', []))} equipamentos no arquivo salvo")
            
            mensagem_sucesso = f"Configuração atualizada do GitHub com sucesso!\n{len(config_data.get('equipamentos', []))} equipamentos carregados."
            if not arquivo_mudou:
                mensagem_sucesso += "\n\n⚠️ AVISO: O arquivo baixado é idêntico ao local. Pode ser cache do GitHub (espere alguns segundos após editar)."
            
            print("Arquivo salvo com sucesso")
            return True, mensagem_sucesso
        except requests.exceptions.Timeout:
            return False, "Timeout ao conectar ao GitHub. Verifique sua conexão com a internet."
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão com o GitHub. Verifique sua conexão com a internet."
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return False, f"Erro ao conectar ao GitHub:\n{str(e)}"
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {str(e)}")
            return False, f"Erro ao processar JSON do GitHub:\n{str(e)}"
        except Exception as e:
            print(f"Erro inesperado: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Erro inesperado ao baixar configuração:\n{type(e).__name__}: {str(e)}"
    
    def atualizar_do_github(self):
        """Atualiza a configuração do GitHub e recarrega os equipamentos"""
        try:
            # Mostrar mensagem de carregamento
            self.root.config(cursor="watch")
            self.root.update()  # Atualizar interface para mostrar cursor
            
            print("Botão atualizar do GitHub pressionado")
            # Tentar baixar do GitHub
            print("Iniciando download do GitHub...")
            sucesso, mensagem = self.baixar_config_do_github()
            
            if sucesso:
                print("Download bem-sucedido, recarregando configuração...")
                # Aguardar um pouco para garantir que o arquivo foi salvo
                time.sleep(0.2)
                # Limpar equipamentos antes de recarregar para forçar atualização
                self.equipamentos = []
                # Recarregar configuração local (sem tentar GitHub novamente)
                self.carregar_configuracao(tentar_github=False)
                # Forçar atualização da interface
                self.root.update_idletasks()
                messagebox.showinfo("Sucesso", mensagem)
            else:
                print(f"Download falhou: {mensagem}")
                # Se falhou, tentar usar arquivo local se existir
                if os.path.exists(self.config_json_path):
                    messagebox.showwarning(
                        "Aviso",
                        f"{mensagem}\n\nUsando arquivo local como fallback."
                    )
                    self.carregar_configuracao(tentar_github=False)
                else:
                    messagebox.showerror("Erro", f"{mensagem}\n\nNenhum arquivo local encontrado.")
        except Exception as e:
            print(f"Exceção ao atualizar do GitHub: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao atualizar do GitHub:\n{type(e).__name__}: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def carregar_configuracao(self, tentar_github=True):
        """Carrega configuração e equipamentos do arquivo JSON
        Se tentar_github=True e for o início do software, tenta baixar do GitHub primeiro"""
        try:
            # Na primeira carga (início do software), tentar baixar do GitHub
            if tentar_github:
                print("Tentando baixar do GitHub...")
                sucesso, mensagem = self.baixar_config_do_github()
                if sucesso:
                    print("Download do GitHub bem-sucedido!")
                else:
                    print(f"Falha no download do GitHub: {mensagem}")
                    # Se falhou, continuar com arquivo local (se existir)
                    if not os.path.exists(self.config_json_path):
                        # Se não há arquivo local e falhou GitHub, criar vazio
                        print("Criando arquivo vazio...")
                        self.equipamentos = []
                        self.salvar_configuracao()
                        return
                    else:
                        print("Usando arquivo local como fallback...")
            
            # Carregar do arquivo local
            if os.path.exists(self.config_json_path):
                with open(self.config_json_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # Carregar versão atual do config.json
                    self.versao_atual = config_data.get('versao', '1.0.0')
                    equipamentos_raw = config_data.get('equipamentos', [])
                    
                    # Inicializar campos dinâmicos para cada equipamento
                    self.equipamentos = []
                    for eq in equipamentos_raw:
                        equipamento = {
                            'categoria': eq.get('categoria', ''),
                            'nome': eq.get('nome', ''),
                            'ip': eq.get('ip', ''),
                            'status': 'Desconhecido',  # Campo dinâmico - não salvo no JSON
                            'latencia': None,  # Campo dinâmico - não salvo no JSON
                            'ultima_verificacao': 'Nunca'  # Campo dinâmico - não salvo no JSON
                        }
                        self.equipamentos.append(equipamento)
            else:
                # Se não existir, criar com dados padrão
                self.equipamentos = []
                self.salvar_configuracao()
            
            # Atualizar tabela
            self.atualizar_tabela_monitoramento()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configuração:\n{str(e)}")
            self.equipamentos = []
    
    def salvar_configuracao(self, mostrar_mensagem=True):
        """Salva configuração e equipamentos no arquivo JSON (apenas dados permanentes)"""
        try:
            # Filtrar apenas dados permanentes (excluir status, latencia, ultima_verificacao)
            equipamentos_para_salvar = []
            for eq in self.equipamentos:
                equipamento_limpo = {
                    'categoria': eq.get('categoria', ''),
                    'nome': eq.get('nome', ''),
                    'ip': eq.get('ip', '')
                }
                equipamentos_para_salvar.append(equipamento_limpo)
            
            config_data = {
                "nome": "ReachCLI",
                "versao": self.versao_atual,  # Usa a versão atual carregada
                "equipamentos": equipamentos_para_salvar
            }
            
            with open(self.config_json_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            if mostrar_mensagem:
                messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
        except Exception as e:
            if mostrar_mensagem:
                messagebox.showerror("Erro", f"Erro ao salvar configuração:\n{str(e)}")
            else:
                # Se erro silencioso, apenas logar
                print(f"Erro ao salvar configuração automaticamente: {str(e)}")
    
    def ordenar_tabela_monitoramento(self, coluna):
        """Ordena a tabela de monitoramento pela coluna clicada"""
        # Alterna ordem se clicar na mesma coluna
        if self.monitoramento_ordem_atual == coluna:
            self.monitoramento_ordem_reversa = not self.monitoramento_ordem_reversa
        else:
            self.monitoramento_ordem_atual = coluna
            self.monitoramento_ordem_reversa = False
        
        # Aplicar ordenação e atualizar tabela
        equipamentos_ordenados = self._aplicar_ordenacao_monitoramento(self.equipamentos)
        self._atualizar_tabela_monitoramento_ordenada(equipamentos_ordenados)
    
    def _ordenacao_padrao_monitoramento(self, equipamentos):
        """Aplica ordenação padrão: Offline primeiro, depois Online, depois Desconhecido"""
        equipamentos_ordenados = equipamentos.copy()
        
        def ordem_padrao_key(eq):
            status = eq.get('status', 'Desconhecido')
            if status == 'Offline':
                return (0, eq.get('nome', '').lower())  # Offline primeiro, ordenado por nome
            elif status == 'Online':
                return (1, eq.get('nome', '').lower())  # Online segundo, ordenado por nome
            else:
                return (2, eq.get('nome', '').lower())  # Desconhecido por último, ordenado por nome
        
        equipamentos_ordenados.sort(key=ordem_padrao_key)
        return equipamentos_ordenados
    
    def _aplicar_ordenacao_monitoramento(self, equipamentos):
        """Aplica a ordenação atual (manual ou padrão) aos equipamentos"""
        if self.monitoramento_ordem_atual:
            # Ordenação manual definida pelo usuário
            equipamentos_ordenados = equipamentos.copy()
            
            # Definir função de chave de ordenação baseada na coluna
            if self.monitoramento_ordem_atual == 'Categoria':
                equipamentos_ordenados.sort(key=lambda x: x.get('categoria', '').lower(), reverse=self.monitoramento_ordem_reversa)
            elif self.monitoramento_ordem_atual == 'Nome':
                equipamentos_ordenados.sort(key=lambda x: x.get('nome', '').lower(), reverse=self.monitoramento_ordem_reversa)
            elif self.monitoramento_ordem_atual == 'IP':
                def ip_key(eq):
                    try:
                        return ipaddress.IPv4Address(eq.get('ip', '0.0.0.0'))
                    except:
                        return ipaddress.IPv4Address('0.0.0.0')
                equipamentos_ordenados.sort(key=ip_key, reverse=self.monitoramento_ordem_reversa)
            elif self.monitoramento_ordem_atual == 'Status':
                def status_key(eq):
                    status = eq.get('status', 'Desconhecido')
                    if status == 'Online':
                        return 0
                    elif status == 'Offline':
                        return 1
                    else:
                        return 2
                equipamentos_ordenados.sort(key=status_key, reverse=self.monitoramento_ordem_reversa)
            elif self.monitoramento_ordem_atual == 'Latência':
                def latencia_key(eq):
                    latencia = eq.get('latencia', None)
                    if latencia is None:
                        return float('inf')  # Sem latência vai para o final
                    return latencia
                equipamentos_ordenados.sort(key=latencia_key, reverse=self.monitoramento_ordem_reversa)
            elif self.monitoramento_ordem_atual == 'Última Verificação':
                def tempo_key(eq):
                    tempo_str = eq.get('ultima_verificacao', 'Nunca')
                    if tempo_str == 'Nunca':
                        return (2, 0, 0, 0)  # Nunca vai para o final
                    try:
                        # Converter HH:MM:SS para tuple para ordenação
                        partes = tempo_str.split(':')
                        return (0, int(partes[0]), int(partes[1]), int(partes[2]))
                    except:
                        return (1, 0, 0, 0)  # Erro no meio
                equipamentos_ordenados.sort(key=tempo_key, reverse=self.monitoramento_ordem_reversa)
            
            return equipamentos_ordenados
        else:
            # Ordenação padrão: Offline primeiro
            return self._ordenacao_padrao_monitoramento(equipamentos)
    
    def _atualizar_tabela_monitoramento_ordenada(self, equipamentos_ordenados):
        """Atualiza a tabela com equipamentos já ordenados (usado internamente)"""
        # Limpar tabela
        for item in self.tree_monitoramento.get_children():
            self.tree_monitoramento.delete(item)
        
        # Adicionar equipamentos na ordem especificada
        for equipamento in equipamentos_ordenados:
            categoria = equipamento.get('categoria', 'N/A')
            nome = equipamento.get('nome', 'N/A')
            ip = equipamento.get('ip', 'N/A')
            status = equipamento.get('status', 'Desconhecido')
            latencia = equipamento.get('latencia', None)
            ultima_verificacao = equipamento.get('ultima_verificacao', 'Nunca')
            
            latencia_str = f"{latencia} ms" if latencia is not None else "-"
            
            # Tag baseada no status (já inclui fundo verde/vermelho)
            tag = 'unknown'
            if status == 'Online':
                tag = 'online'
            elif status == 'Offline':
                tag = 'offline'
            
            self.tree_monitoramento.insert('', tk.END, values=(
                categoria, nome, ip, status, latencia_str, ultima_verificacao
            ), tags=(tag,))
    
    def atualizar_tabela_monitoramento(self):
        """Atualiza a tabela com os equipamentos (respeitando ordenação atual sem alterá-la)"""
        # Aplicar ordenação atual (manual ou padrão) sem alterar a configuração
        equipamentos_ordenados = self._aplicar_ordenacao_monitoramento(self.equipamentos)
        self._atualizar_tabela_monitoramento_ordenada(equipamentos_ordenados)
    
    def ping_ip(self, ip: str) -> tuple:
        """Executa 2 pings em um IP e retorna a média da latência
        Retorna (sucesso, latencia_media_ms)"""
        num_pings = 2
        timeout_ping = 10  # segundos
        latencias = []
        
        for tentativa in range(num_pings):
            try:
                if self.os_type == 'windows':
                    # Windows: -n 1 (1 ping), -w timeout em ms
                    cmd = ['ping', '-n', '1', '-w', f'{timeout_ping * 1000}', ip]
                else:
                    # Linux: -c 1 (1 ping), -W timeout em segundos
                    cmd = ['ping', '-c', '1', '-W', str(timeout_ping), ip]
                
                creation_flags = 0
                if self.os_type == 'windows':
                    creation_flags = subprocess.CREATE_NO_WINDOW
                
                # Executar ping com timeout
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_ping + 1,  # Timeout ligeiramente maior que o ping
                    creationflags=creation_flags
                )
                
                if result.returncode == 0:
                    # Extrair latência diretamente do output do ping (mais preciso)
                    latencia = self.extract_ping_time_monitoramento(result.stdout)
                    if latencia is not None and latencia > 0:
                        latencias.append(latencia)
                    
            except subprocess.TimeoutExpired:
                # Timeout - ignorar este ping
                pass
            except Exception:
                # Qualquer outro erro - ignorar este ping
                pass
        
        # Se pelo menos um ping funcionou, calcular média
        if latencias:
            latencia_media = int(sum(latencias) / len(latencias))
            return True, latencia_media
        
        # Se nenhum ping funcionou
        return False, None
    
    def extract_ping_time_monitoramento(self, output):
        """Extrai tempo de ping diretamente do output (mais preciso)"""
        try:
            if self.os_type == 'windows':
                # Windows: "Resposta de X.X.X.X: bytes=32 tempo=XXms TTL=XX"
                # Padrão principal: "tempo=XXms" ou "tempo<XXms"
                match = re.search(r'tempo[<=](\d+)\s*ms', output, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            else:
                # Linux/macOS: "time=X.XXX ms" ou "time=X ms"
                match = re.search(r'time=([\d.]+)\s*ms', output)
                if match:
                    return int(float(match.group(1)))
        except:
            pass
        
        return None
    
    def toggle_monitoramento(self):
        """Inicia ou para o monitoramento"""
        if self.monitorando:
            # Parar monitoramento
            self.monitorando = False
            self.btn_monitorar.config(text="▶")
            # Restaurar cores do botão para estado "iniciar"
            if hasattr(self, 'btn_monitorar_frame'):
                self.btn_monitorar_frame._cor_bg = "#d1fae5"
                self.btn_monitorar_frame._cor_fg = "#065f46"
                self.btn_monitorar_frame._cor_hover_bg = "#a7f3d0"
                self.btn_monitorar_frame._cor_hover_fg = "#047857"
                self.btn_monitorar_frame._cor_borda = "#86efac"
                self.btn_monitorar_frame._cor_borda_hover = "#4ade80"
                self.btn_monitorar_frame.config(bg="#d1fae5", highlightbackground="#86efac")
                self.btn_monitorar.config(bg="#d1fae5", fg="#065f46", activebackground="#a7f3d0", activeforeground="#047857")
        else:
            # Iniciar monitoramento
            try:
                self.monitoramento_intervalo = int(self.intervalo_var.get())
                if self.monitoramento_intervalo < 5:
                    messagebox.showwarning("Aviso", "Intervalo mínimo é 5 segundos")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Intervalo deve ser um número válido")
                return
            
            if not self.equipamentos:
                messagebox.showwarning("Aviso", "Adicione pelo menos um equipamento para monitorar")
                return
            
            self.monitorando = True
            self.btn_monitorar.config(text="⏸")
            # Atualizar cores do botão para estado "parar"
            if hasattr(self, 'btn_monitorar_frame'):
                self.btn_monitorar_frame._cor_bg = "#fee2e2"
                self.btn_monitorar_frame._cor_fg = "#dc2626"
                self.btn_monitorar_frame._cor_hover_bg = "#fecaca"
                self.btn_monitorar_frame._cor_hover_fg = "#991b1b"
                self.btn_monitorar_frame._cor_borda = "#fca5a5"
                self.btn_monitorar_frame._cor_borda_hover = "#f87171"
                self.btn_monitorar_frame.config(bg="#fee2e2", highlightbackground="#fca5a5")
                self.btn_monitorar.config(bg="#fee2e2", fg="#dc2626", activebackground="#fecaca", activeforeground="#991b1b")
            
            # Iniciar thread de monitoramento
            self.monitoramento_thread = threading.Thread(target=self.loop_monitoramento, daemon=True)
            self.monitoramento_thread.start()
    
    def loop_monitoramento(self):
        """Loop de monitoramento em thread separada - roda sempre em segundo plano"""
        while self.monitorando:
            # Fazer cópia da lista para evitar problemas de concorrência
            equipamentos_copy = self.equipamentos.copy()
            
            if not equipamentos_copy:
                # Se não houver equipamentos, aguardar intervalo (ler valor atualizado)
                try:
                    intervalo_atual = int(self.intervalo_var.get())
                    if intervalo_atual < 5:
                        intervalo_atual = 5
                    self.monitoramento_intervalo = intervalo_atual
                except (ValueError, AttributeError):
                    pass
                
                for _ in range(self.monitoramento_intervalo):
                    if not self.monitorando:
                        break
                    time.sleep(1)
                continue
            
            # Executar pings em paralelo usando ThreadPoolExecutor
            # Limitar workers para não sobrecarregar o sistema
            num_workers = min(len(equipamentos_copy), 10) if len(equipamentos_copy) > 0 else 1
            
            if num_workers > 0:
                executor = ThreadPoolExecutor(max_workers=num_workers)
                futures = {}
                
                try:
                    # Criar dicionário de futures: {future: ip}
                    for equipamento in equipamentos_copy:
                        if not self.monitorando:
                            break
                        
                        ip = equipamento.get('ip', '')
                        if not ip:
                            continue
                        
                        # Submeter ping para execução paralela
                        future = executor.submit(self.ping_ip, ip)
                        futures[future] = ip
                    
                    # Processar resultados conforme completam
                    for future in as_completed(futures):
                        if not self.monitorando:
                            break
                        
                        ip = futures[future]
                        try:
                            # Obter resultado do ping (com timeout para evitar travamento)
                            sucesso, latencia = future.result(timeout=25)  # Timeout: 2 pings * 10s + margem
                            
                            # Atualizar equipamento (buscar na lista original pelo IP)
                            for eq in self.equipamentos:
                                if eq.get('ip') == ip:
                                    eq['status'] = 'Online' if sucesso else 'Offline'
                                    eq['latencia'] = latencia if sucesso else None
                                    eq['ultima_verificacao'] = datetime.now().strftime('%H:%M:%S')
                                    break
                            
                            # Atualizar interface na thread principal (sempre, mesmo em outras abas)
                            try:
                                self.root.after(0, self.atualizar_tabela_monitoramento)
                            except:
                                pass  # Se a janela foi fechada, ignorar
                                
                        except Exception as e:
                            # Em caso de erro no futuro, marcar como offline
                            for eq in self.equipamentos:
                                if eq.get('ip') == ip:
                                    eq['status'] = 'Offline'
                                    eq['latencia'] = None
                                    eq['ultima_verificacao'] = datetime.now().strftime('%H:%M:%S')
                                    break
                            try:
                                self.root.after(0, self.atualizar_tabela_monitoramento)
                            except:
                                pass
                finally:
                    # Garantir que o executor seja fechado e recursos liberados
                    executor.shutdown(wait=False)  # wait=False para não bloquear se algum ping estiver demorando
            
            # Aguardar intervalo antes da próxima rodada (ler valor atualizado do campo)
            try:
                intervalo_atual = int(self.intervalo_var.get())
                if intervalo_atual < 5:
                    intervalo_atual = 5  # Mínimo de 5 segundos
                self.monitoramento_intervalo = intervalo_atual
            except (ValueError, AttributeError):
                # Se houver erro ao ler, usar o último valor válido
                pass
            
            for _ in range(self.monitoramento_intervalo):
                if not self.monitorando:
                    break
                time.sleep(1)
    
    def adicionar_equipamento(self):
        """Abre diálogo para adicionar novo equipamento"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Equipamento")
        dialog.geometry("550x380")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#f1f5f9')
        
        # Centralizar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame externo com sombra (simulada com borda)
        shadow_frame = tk.Frame(dialog, bg='#cbd5e1', padx=2, pady=2)
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Main frame estilizado
        main_frame = tk.Frame(shadow_frame, bg='white', relief=tk.FLAT, bd=0, 
                             highlightbackground='#e2e8f0', highlightthickness=1)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = tk.Frame(main_frame, bg='white')
        title_frame.pack(fill=tk.X, pady=(25, 20))
        
        title_label = tk.Label(
            title_frame,
            text="➕ Adicionar Equipamento",
            bg='white',
            font=("Segoe UI", 18, "bold"),
            fg=self.cor_primaria
        )
        title_label.pack()
        
        # Frame de conteúdo com padding
        content_frame = tk.Frame(main_frame, bg='white', padx=35, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Categoria
        tk.Label(content_frame, text="Categoria:", bg='white', font=("Segoe UI", 13, "bold"), 
                fg="#475569").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))
        categoria_var = tk.StringVar()
        categorias = ["OLT", "MIKROTIK", "ENERGIA", "CONCENTRADOR", "RADIO", "BORDA", "SERVIDOR"]
        categoria_combo = ttk.Combobox(
            content_frame, 
            textvariable=categoria_var, 
            width=32, 
            font=("Segoe UI", 13),
            values=categorias,
            state='readonly'
        )
        categoria_combo.grid(row=0, column=1, sticky=tk.EW, pady=(0, 18), padx=(15, 0))
        categoria_combo.current(0)
        
        # Nome
        tk.Label(content_frame, text="Nome:", bg='white', font=("Segoe UI", 13, "bold"), 
                fg="#475569").grid(row=1, column=0, sticky=tk.W, pady=(0, 6))
        nome_var = tk.StringVar()
        nome_entry = tk.Entry(
            content_frame, 
            textvariable=nome_var, 
            width=35, 
            font=("Segoe UI", 13),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            highlightcolor="#2563eb",
            bg="#ffffff",
            fg="#1e293b",
            insertbackground="#1e293b"
        )
        nome_entry.grid(row=1, column=1, sticky=tk.EW, pady=(0, 18), padx=(15, 0))
        
        # IP
        tk.Label(content_frame, text="IP:", bg='white', font=("Segoe UI", 13, "bold"), 
                fg="#475569").grid(row=2, column=0, sticky=tk.W, pady=(0, 6))
        ip_var = tk.StringVar()
        ip_entry = tk.Entry(
            content_frame, 
            textvariable=ip_var, 
            width=35, 
            font=("Segoe UI", 13),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            highlightcolor="#2563eb",
            bg="#ffffff",
            fg="#1e293b",
            insertbackground="#1e293b"
        )
        ip_entry.grid(row=2, column=1, sticky=tk.EW, pady=(0, 25), padx=(15, 0))
        
        content_frame.grid_columnconfigure(1, weight=1)
        
        def salvar():
            categoria = categoria_var.get().strip()
            nome = nome_var.get().strip()
            ip = ip_var.get().strip()
            
            if not categoria or not nome or not ip:
                messagebox.showwarning("Aviso", "Preencha todos os campos")
                return
            
            if not validar_ipv4(ip):
                messagebox.showerror("Erro", "IP inválido")
                return
            
            # Verificar se IP já existe
            for eq in self.equipamentos:
                if eq.get('ip') == ip:
                    messagebox.showerror("Erro", "Este IP já está sendo usado por outro equipamento")
                    return
            
            # Adicionar equipamento
            self.equipamentos.append({
                'categoria': categoria,
                'nome': nome,
                'ip': ip,
                'status': 'Desconhecido',
                'latencia': None,
                'ultima_verificacao': 'Nunca'
            })
            
            self.atualizar_tabela_monitoramento()
            # Salvar automaticamente no JSON
            self.salvar_configuracao(mostrar_mensagem=False)
            dialog.destroy()
        
        # Botões estilizados
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(fill=tk.X, pady=(0, 25), padx=35)
        
        btn_cancelar = tk.Button(
            btn_frame, 
            text="Cancelar", 
            command=dialog.destroy,
            font=("Segoe UI", 13),
            padx=25,
            pady=10,
            bg="#f1f5f9",
            fg="#475569",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground="#e2e8f0",
            activeforeground="#1e293b",
            highlightthickness=0
        )
        
        btn_ok = tk.Button(
            btn_frame, 
            text="Adicionar", 
            command=salvar,
            font=("Segoe UI", 13, "bold"),
            padx=30,
            pady=10,
            bg=self.cor_primaria,
            fg='white',
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=self.cor_primaria_hover,
            activeforeground="white",
            highlightthickness=0
        )
        btn_ok.pack(side=tk.RIGHT, padx=(15, 0))
        btn_cancelar.pack(side=tk.RIGHT)
    
    def mostrar_menu_contexto_monitoramento(self, event):
        """Mostra menu de contexto ao clicar com botão direito"""
        item = self.tree_monitoramento.selection()[0] if self.tree_monitoramento.selection() else None
        if item:
            self.menu_contexto_monitoramento.post(event.x_root, event.y_root)
    
    def get_equipamento_selecionado_index(self):
        """Retorna o índice do equipamento selecionado na tabela"""
        selection = self.tree_monitoramento.selection()
        if not selection:
            return None
        
        item = selection[0]
        try:
            # Obter valores para encontrar o IP e buscar na lista
            values = self.tree_monitoramento.item(item, 'values')
            if values and len(values) >= 3:
                ip_selecionado = values[2]  # IP está na 3ª coluna (índice 2)
                # Buscar índice na lista de equipamentos
                for i, eq in enumerate(self.equipamentos):
                    if eq.get('ip') == ip_selecionado:
                        return i
        except:
            pass
        return None
    
    def editar_equipamento_selecionado(self):
        """Edita o equipamento selecionado na tabela"""
        index = self.get_equipamento_selecionado_index()
        if index is None or index >= len(self.equipamentos):
            messagebox.showwarning("Aviso", "Selecione um equipamento para editar")
            return
        
        equipamento = self.equipamentos[index]
        
        # Diálogo de edição (similar ao de adicionar)
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Equipamento")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Categoria
        tk.Label(main_frame, text="Categoria:", bg='white', font=("Segoe UI", 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        categoria_var = tk.StringVar(value=equipamento.get('categoria', ''))
        categoria_combo = ttk.Combobox(main_frame, textvariable=categoria_var, width=30, font=("Segoe UI", 12),
                                      values=["Roteador", "Switch", "Access Point", "Servidor", "Gateway", "Outro"])
        categoria_combo.grid(row=0, column=1, sticky=tk.EW, pady=(0, 8))
        
        # Nome
        tk.Label(main_frame, text="Nome:", bg='white', font=("Segoe UI", 12)).grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
        nome_var = tk.StringVar(value=equipamento.get('nome', ''))
        nome_entry = tk.Entry(main_frame, textvariable=nome_var, width=32, font=("Segoe UI", 12))
        nome_entry.grid(row=1, column=1, sticky=tk.EW, pady=(0, 8))
        
        # IP
        tk.Label(main_frame, text="IP:", bg='white', font=("Segoe UI", 12)).grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        ip_var = tk.StringVar(value=equipamento.get('ip', ''))
        ip_entry = tk.Entry(main_frame, textvariable=ip_var, width=32, font=("Segoe UI", 12))
        ip_entry.grid(row=2, column=1, sticky=tk.EW, pady=(0, 20))
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        def salvar():
            categoria = categoria_var.get().strip()
            nome = nome_var.get().strip()
            ip = ip_var.get().strip()
            
            if not categoria or not nome or not ip:
                messagebox.showwarning("Aviso", "Preencha todos os campos")
                return
            
            if not validar_ipv4(ip):
                messagebox.showerror("Erro", "IP inválido")
                return
            
            # Verificar se IP já existe em outro equipamento
            ip_antigo = equipamento.get('ip', '')
            if ip != ip_antigo:
                for i, eq in enumerate(self.equipamentos):
                    if i != index and eq.get('ip') == ip:
                        messagebox.showerror("Erro", "Este IP já está sendo usado por outro equipamento")
                        return
            
            # Atualizar equipamento
            equipamento['categoria'] = categoria
            equipamento['nome'] = nome
            equipamento['ip'] = ip
            # Manter status, latência e última verificação
            
            self.atualizar_tabela_monitoramento()
            # Salvar automaticamente no JSON
            self.salvar_configuracao(mostrar_mensagem=False)
            dialog.destroy()
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        
        btn_cancelar = tk.Button(btn_frame, text="Cancelar", command=dialog.destroy,
                                font=("Segoe UI", 12), padx=20, pady=8)
        btn_cancelar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_ok = tk.Button(btn_frame, text="Salvar", command=salvar,
                          font=("Segoe UI", 12), padx=20, pady=8,
                          bg=self.cor_primaria, fg='white', relief=tk.FLAT)
        btn_ok.pack(side=tk.LEFT)
        
        # Focar no campo nome
        nome_entry.focus()
        nome_entry.select_range(0, tk.END)
    
    def deletar_equipamento_selecionado(self):
        """Deleta o equipamento selecionado da tabela"""
        index = self.get_equipamento_selecionado_index()
        if index is None or index >= len(self.equipamentos):
            messagebox.showwarning("Aviso", "Selecione um equipamento para deletar")
            return
        
        equipamento = self.equipamentos[index]
        nome = equipamento.get('nome', 'Equipamento')
        
        # Confirmar deleção
        resposta = messagebox.askyesno(
            "Confirmar Deleção",
            f"Deseja realmente deletar o equipamento:\n{nome} ({equipamento.get('ip', '')})?",
            icon='warning'
        )
        
        if resposta:
            # Remover equipamento
            del self.equipamentos[index]
            self.atualizar_tabela_monitoramento()
            # Salvar automaticamente no JSON
            self.salvar_configuracao(mostrar_mensagem=False)
    
    def criar_tela_ping(self, parent):
        """Cria a tela de teste Ping"""
        content_frame = tk.Frame(parent, bg=self.cor_fundo)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        
        title = tk.Label(
            content_frame,
            text="📡 Teste Ping",
            font=("Segoe UI", 27, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title.pack(pady=50)
        
        subtitle = tk.Label(
            content_frame,
            text="Funcionalidade em desenvolvimento",
            font=("Segoe UI", 15),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle.pack()
    
    def criar_tela_port(self, parent):
        """Cria a tela de Port Scanner"""
        content_frame = tk.Frame(parent, bg=self.cor_fundo)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        
        title = tk.Label(
            content_frame,
            text="🔍 Port Scanner",
            font=("Segoe UI", 27, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title.pack(pady=50)
        
        subtitle = tk.Label(
            content_frame,
            text="Funcionalidade em desenvolvimento",
            font=("Segoe UI", 15),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle.pack()
    
    def criar_tela_relatorios(self, parent):
        """Cria a tela de Relatórios"""
        content_frame = tk.Frame(parent, bg=self.cor_fundo)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        
        title = tk.Label(
            content_frame,
            text="📊 Relatórios",
            font=("Segoe UI", 27, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title.pack(pady=50)
        
        subtitle = tk.Label(
            content_frame,
            text="Funcionalidade em desenvolvimento",
            font=("Segoe UI", 15),
            fg="#64748b",
            bg=self.cor_fundo
        )
        subtitle.pack()
    
    def criar_tela_configuracoes(self, parent):
        """Cria a tela de Configurações"""
        content_frame = tk.Frame(parent, bg=self.cor_fundo)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=self.padding_externo, pady=self.padding_externo)
        
        # Título
        title = tk.Label(
            content_frame,
            text="⚙️ Configurações",
            font=("Segoe UI", 27, "bold"),
            fg=self.cor_primaria,
            bg=self.cor_fundo
        )
        title.pack(pady=(20, 40))
        
        # Frame para informações da versão
        info_frame = tk.LabelFrame(
            content_frame,
            text="Informações do Sistema",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.cor_primaria,
            padx=self.padding_interno,
            pady=self.padding_interno,
            relief=tk.FLAT,
            borderwidth=1
        )
        info_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Versão atual
        versao_label = tk.Label(
            info_frame,
            text=f"Versão Atual: {self.versao_atual}",
            font=("Segoe UI", 13),
            bg="white",
            fg="#475569"
        )
        versao_label.pack(anchor=tk.W, pady=5)
        
        # Frame para atualizações
        update_frame = tk.LabelFrame(
            content_frame,
            text="Atualizações",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.cor_primaria,
            padx=self.padding_interno,
            pady=self.padding_interno,
            relief=tk.FLAT,
            borderwidth=1
        )
        update_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Status da atualização com loading
        status_container = tk.Frame(update_frame, bg="white")
        status_container.pack(anchor=tk.W, pady=(0, 15), fill=tk.X)
        
        self.status_atualizacao_label = tk.Label(
            status_container,
            text="Status: Não verificado",
            font=("Segoe UI", 12),
            bg="white",
            fg="#64748b"
        )
        self.status_atualizacao_label.pack(side=tk.LEFT)
        
        # Label para loading (escondido inicialmente)
        self.loading_label = tk.Label(
            status_container,
            text="⏳",
            font=("Segoe UI", 14),
            bg="white",
            fg="#f59e0b"
        )
        self.loading_label.pack_forget()  # Esconder inicialmente
        
        # Frame para botões com espaçamento
        botoes_frame = tk.Frame(update_frame, bg="white")
        botoes_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Botão Verificar Atualizações (estilo moderno e sutil)
        btn_verificar = self.criar_botao_moderno(
            botoes_frame,
            "Verificar Atualizações",
            self.verificar_atualizacoes,
            cor_bg="#f1f5f9",
            cor_fg="#475569",
            cor_hover_bg="#e2e8f0",
            cor_hover_fg="#1e293b",
            icon="🔍"
        )
        btn_verificar.pack(side=tk.LEFT, padx=(0, 12))
        
        # Botão Atualizar (estilo moderno e sutil)
        self.btn_atualizar = self.criar_botao_moderno(
            botoes_frame,
            "Atualizar Agora",
            self.baixar_atualizacao,
            cor_bg="#dbeafe",
            cor_fg="#1e40af",
            cor_hover_bg="#bfdbfe",
            cor_hover_fg="#1e3a8a",
            icon="⬇️"
        )
        self.btn_atualizar.pack(side=tk.LEFT)
        self.btn_atualizar.config(state=tk.DISABLED)  # Desabilitado até verificar
    
    def verificar_atualizacoes(self):
        """Verifica se há atualizações disponíveis na Cloudflare"""
        if self.verificando_atualizacao:
            messagebox.showinfo("Aviso", "Verificação de atualização já em andamento...")
            return
        
        self.verificando_atualizacao = True
        self.root.config(cursor="watch")
        self.status_atualizacao_label.config(text="Status: Verificando atualizações...", fg="#f59e0b")
        self.btn_atualizar.config(state=tk.DISABLED)
        
        # Mostrar loading
        self.loading_label.pack(side=tk.LEFT, padx=(10, 0))
        self._animar_loading()
        
        def verificar_thread():
            try:
                # Tentar encontrar a versão mais recente
                # Como não temos API para listar, vamos tentar versões comuns
                versao_disponivel = None
                versao_atual_num = self._parse_versao(self.versao_atual)
                major, minor, patch = versao_atual_num
                
                # Lista de versões para testar (patch, minor, major)
                versoes_para_testar = []
                
                # Testar patches (1.0.1, 1.0.2, ... até 1.0.10)
                for p in range(patch + 1, patch + 11):
                    versoes_para_testar.append((major, minor, p))
                
                # Testar minor (1.1.0, 1.2.0, ... até 1.10.0)
                for m in range(minor + 1, minor + 11):
                    versoes_para_testar.append((major, m, 0))
                
                # Testar major (2.0.0, 3.0.0, ... até 10.0.0)
                for ma in range(major + 1, major + 10):
                    versoes_para_testar.append((ma, 0, 0))
                
                # Testar cada versão
                for versao_teste in versoes_para_testar:
                    versao_str = f"{versao_teste[0]}.{versao_teste[1]}.{versao_teste[2]}"
                    url_teste = f"{self.cloudflare_base_url}/reachcli_v{versao_str}.zip"
                    
                    try:
                        response = requests.head(url_teste, timeout=5, allow_redirects=True)
                        if response.status_code == 200:
                            versao_disponivel = versao_str
                            print(f"Versão encontrada: {versao_str}")
                            break
                    except Exception as e:
                        print(f"Erro ao verificar {versao_str}: {str(e)}")
                        continue
                
                # Atualizar UI na thread principal
                self.root.after(0, lambda: self._atualizar_status_verificacao(versao_disponivel))
                
            except Exception as e:
                print(f"Erro ao verificar atualizações: {str(e)}")
                self.root.after(0, lambda: self._atualizar_status_verificacao(None, str(e)))
            finally:
                self.verificando_atualizacao = False
                self.root.after(0, lambda: self.root.config(cursor=""))
                self.root.after(0, lambda: self.loading_label.pack_forget())  # Esconder loading
        
        threading.Thread(target=verificar_thread, daemon=True).start()
    
    def _animar_loading(self):
        """Anima o indicador de loading"""
        if self.verificando_atualizacao:
            emojis = ["⏳", "🔄", "⏳", "🔄"]
            current = self.loading_label.cget("text")
            try:
                index = emojis.index(current) if current in emojis else 0
                next_emoji = emojis[(index + 1) % len(emojis)]
            except:
                next_emoji = "⏳"
            self.loading_label.config(text=next_emoji)
            self.root.after(500, self._animar_loading)  # Atualizar a cada 500ms
    
    def _atualizar_status_verificacao(self, versao_disponivel, erro=None):
        """Atualiza o status da verificação na UI"""
        # Esconder loading
        self.loading_label.pack_forget()
        
        if erro:
            self.status_atualizacao_label.config(
                text=f"Status: Erro ao verificar - {erro}",
                fg=self.cor_erro
            )
            messagebox.showerror("Erro", f"Erro ao verificar atualizações:\n{erro}")
        elif versao_disponivel:
            if self._comparar_versoes(versao_disponivel, self.versao_atual) > 0:
                self.status_atualizacao_label.config(
                    text=f"Status: Nova versão disponível! (v{versao_disponivel})",
                    fg=self.cor_sucesso
                )
                self.btn_atualizar.config(state=tk.NORMAL)
                self.versao_disponivel = versao_disponivel
                messagebox.showinfo(
                    "Atualização Disponível",
                    f"Uma nova versão está disponível!\n\nVersão Atual: {self.versao_atual}\nNova Versão: {versao_disponivel}\n\nClique em 'Atualizar Agora' para baixar e instalar."
                )
            else:
                self.status_atualizacao_label.config(
                    text=f"Status: Você está usando a versão mais recente (v{self.versao_atual})",
                    fg=self.cor_sucesso
                )
                self.btn_atualizar.config(state=tk.DISABLED)
                messagebox.showinfo("Atualização", "Você está usando a versão mais recente!")
        else:
            self.status_atualizacao_label.config(
                text="Status: Nenhuma atualização encontrada",
                fg="#64748b"
            )
            self.btn_atualizar.config(state=tk.DISABLED)
    
    def baixar_atualizacao(self):
        """Baixa e instala a atualização"""
        if not hasattr(self, 'versao_disponivel') or not self.versao_disponivel:
            messagebox.showwarning("Aviso", "Nenhuma atualização disponível. Verifique atualizações primeiro.")
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Atualização",
            f"Tem certeza que deseja atualizar para a versão {self.versao_disponivel}?\n\n"
            "O aplicativo será reiniciado após a atualização."
        )
        
        if not resposta:
            return
        
        self.root.config(cursor="watch")
        self.btn_atualizar.config(state=tk.DISABLED)
        self.status_atualizacao_label.config(text="Status: Baixando atualização...", fg="#f59e0b")
        
        def baixar_thread():
            try:
                url_zip = f"{self.cloudflare_base_url}/reachcli_v{self.versao_disponivel}.zip"
                zip_path = f"reachcli_v{self.versao_disponivel}.zip"
                
                # Baixar ZIP
                print(f"Baixando atualização de: {url_zip}")
                response = requests.get(url_zip, timeout=30, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progresso = (downloaded / total_size) * 100
                                self.root.after(0, lambda p=progresso: self.status_atualizacao_label.config(
                                    text=f"Status: Baixando... {p:.1f}%"
                                ))
                
                # Extrair ZIP
                self.root.after(0, lambda: self.status_atualizacao_label.config(
                    text="Status: Extraindo arquivos...", fg="#f59e0b"
                ))
                
                # Criar diretório temporário para extração
                temp_dir = "update_temp"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Atualizar arquivos (copiar do temp_dir para o diretório atual, exceto config.json)
                self.root.after(0, lambda: self.status_atualizacao_label.config(
                    text="Status: Instalando atualização...", fg="#f59e0b"
                ))
                
                # Lista de arquivos a ignorar durante a atualização
                ignorar = ['config.json', '__pycache__', '.git']
                
                for root, dirs, files in os.walk(temp_dir):
                    # Filtrar diretórios a ignorar
                    dirs[:] = [d for d in dirs if d not in ignorar]
                    
                    for file in files:
                        if file in ignorar:
                            continue
                        
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, temp_dir)
                        dst_path = os.path.join('.', rel_path)
                        
                        # Criar diretório de destino se não existir
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        
                        # Copiar arquivo
                        shutil.copy2(src_path, dst_path)
                
                # Limpar arquivos temporários
                shutil.rmtree(temp_dir)
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                
                # Atualizar versão no config.json
                self.versao_atual = self.versao_disponivel
                self.salvar_configuracao(mostrar_mensagem=False)
                
                # Sucesso
                self.root.after(0, lambda: self._finalizar_atualizacao(True))
                
            except Exception as e:
                print(f"Erro ao baixar/instalar atualização: {str(e)}")
                self.root.after(0, lambda: self._finalizar_atualizacao(False, str(e)))
            finally:
                self.root.after(0, lambda: self.root.config(cursor=""))
        
        threading.Thread(target=baixar_thread, daemon=True).start()
    
    def _finalizar_atualizacao(self, sucesso, erro=None):
        """Finaliza o processo de atualização"""
        if sucesso:
            self.status_atualizacao_label.config(
                text=f"Status: Atualização instalada com sucesso! (v{self.versao_disponivel})",
                fg=self.cor_sucesso
            )
            messagebox.showinfo(
                "Atualização Concluída",
                f"Atualização para versão {self.versao_disponivel} instalada com sucesso!\n\n"
                "O aplicativo precisa ser reiniciado para aplicar as mudanças.\n"
                "Por favor, feche e abra o aplicativo novamente."
            )
            self.btn_atualizar.config(state=tk.DISABLED)
        else:
            self.status_atualizacao_label.config(
                text=f"Status: Erro ao instalar atualização - {erro}",
                fg=self.cor_erro
            )
            messagebox.showerror("Erro", f"Erro ao instalar atualização:\n{erro}")
            self.btn_atualizar.config(state=tk.NORMAL)
    
    def _parse_versao(self, versao_str):
        """Converte string de versão (ex: '1.0.0') para tupla (1, 0, 0)"""
        try:
            partes = versao_str.split('.')
            return (int(partes[0]), int(partes[1]), int(partes[2]))
        except:
            return (1, 0, 0)
    
    def _incrementar_versao(self, versao_tupla, incremento):
        """Incrementa a versão (major, minor, patch)"""
        major, minor, patch = versao_tupla
        patch += incremento
        while patch >= 100:
            patch -= 100
            minor += 1
        while minor >= 100:
            minor -= 100
            major += 1
        return (major, minor, patch)
    
    def _comparar_versoes(self, versao1_str, versao2_str):
        """Compara duas versões. Retorna 1 se versao1 > versao2, -1 se versao1 < versao2, 0 se iguais"""
        v1 = self._parse_versao(versao1_str)
        v2 = self._parse_versao(versao2_str)
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
    
    def criar_botao(self, parent, text, command, bg, bg_hover, bold=False, small=False):
        """Cria um botão estilizado com hover simples"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="white",
            font=("Segoe UI", 13 if small else 14, "bold" if bold else "normal"),
            padx=18 if not small else 14,
            pady=10 if not small else 7,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=bg_hover,
            activeforeground="white",
            highlightthickness=0
        )
        
        # Hover simples
        def on_enter(e):
            btn.config(bg=bg_hover)
        def on_leave(e):
            btn.config(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def criar_botao_moderno(self, parent, text, command, cor_bg="#f1f5f9", cor_fg="#475569", 
                            cor_hover_bg="#e2e8f0", cor_hover_fg="#1e293b", icon=None, apenas_icone=False, tamanho_icone=14):
        """Cria um botão moderno e sutil com estilo flat design, borda bonita e hover melhorado"""
        # Cor da borda baseada na cor de fundo (mais escura)
        if cor_bg == "#d1fae5":  # Verde claro
            cor_borda_base = "#86efac"
            cor_borda_hover_base = "#4ade80"
        elif cor_bg == "#dbeafe":  # Azul claro
            cor_borda_base = "#93c5fd"
            cor_borda_hover_base = "#60a5fa"
        elif cor_bg == "#fee2e2":  # Vermelho claro
            cor_borda_base = "#fca5a5"
            cor_borda_hover_base = "#f87171"
        else:  # Cinza claro (padrão)
            cor_borda_base = "#cbd5e1"
            cor_borda_hover_base = "#94a3b8"
        
        # Frame interno para padding e borda bonita
        btn_frame = tk.Frame(parent, bg=cor_bg, relief=tk.FLAT, bd=0, highlightbackground=cor_borda_base, highlightthickness=1)
        
        # Texto do botão - apenas ícone se apenas_icone=True
        if apenas_icone and icon:
            texto_completo = icon
            padx_val = 10
            pady_val = 8
            font_size = tamanho_icone
        else:
            texto_completo = f"{icon} {text}" if icon else text
            padx_val = 20
            pady_val = 10
            font_size = 12
        
        btn = tk.Button(
            btn_frame,
            text=texto_completo,
            command=command,
            bg=cor_bg,
            fg=cor_fg,
            font=("Segoe UI", font_size, "normal"),
            padx=padx_val,
            pady=pady_val,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=cor_hover_bg,
            activeforeground=cor_hover_fg,
            highlightthickness=0,
            borderwidth=0
        )
        btn.pack(fill=tk.BOTH, expand=True)
        
        # Armazenar cores originais
        btn_frame._cor_bg = cor_bg
        btn_frame._cor_fg = cor_fg
        btn_frame._cor_hover_bg = cor_hover_bg
        btn_frame._cor_hover_fg = cor_hover_fg
        btn_frame._cor_borda = cor_borda_base
        btn_frame._cor_borda_hover = cor_borda_hover_base
        btn_frame._btn_interno = btn
        
        # Hover melhorado com borda
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=cor_hover_bg, fg=cor_hover_fg)
                btn_frame.config(bg=cor_hover_bg, highlightbackground=btn_frame._cor_borda_hover, highlightthickness=1)
        
        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=cor_bg, fg=cor_fg)
                btn_frame.config(bg=cor_bg, highlightbackground=btn_frame._cor_borda, highlightthickness=1)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        
        # Método config customizado para o frame
        def config_btn_frame(**kwargs):
            if 'state' in kwargs:
                state = kwargs['state']
                if state == tk.DISABLED:
                    btn.config(bg="#f8fafc", fg="#cbd5e1", cursor="arrow", state=tk.DISABLED)
                    btn_frame.config(bg="#f8fafc", highlightbackground="#e2e8f0", highlightthickness=1)
                else:
                    btn.config(bg=cor_bg, fg=cor_fg, cursor="hand2", state=tk.NORMAL)
                    btn_frame.config(bg=cor_bg, highlightbackground=btn_frame._cor_borda, highlightthickness=1)
            # Repassar outros configs para o botão interno
            outros_kwargs = {k: v for k, v in kwargs.items() if k != 'state'}
            if outros_kwargs:
                btn.config(**outros_kwargs)
            return {}
        
        btn_frame.config = config_btn_frame
        
        return btn_frame
    
    def criar_botao_pequeno(self, parent, text, command):
        """Cria um botão pequeno para ordenação com hover simples"""
        btn_bg = '#e2e8f0'
        btn_bg_hover = '#cbd5e1'
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=btn_bg,
            fg='#475569',
            font=("Segoe UI", 13),
            padx=12,
            pady=5,
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            activebackground=btn_bg_hover,
            activeforeground='#1e293b',
            highlightthickness=0
        )
        
        # Hover simples
        def on_enter(e):
            btn.config(bg=btn_bg_hover)
        def on_leave(e):
            btn.config(bg=btn_bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def criar_tabela(self, parent):
        """Cria a tabela de resultados com layout responsivo"""
        # Frame para scrollbar com grid
        table_frame = tk.Frame(parent, bg='white')
        table_frame.grid(row=3, column=0, sticky=tk.NSEW, padx=self.padding_interno, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview (tabela) com estilo melhorado
        columns = ('IP', 'Porta', 'HTTP', 'HTTPS', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=25)
        
        # Configura colunas
        self.tree.heading('IP', text='IP')
        self.tree.heading('Porta', text='Porta')
        self.tree.heading('HTTP', text='HTTP')
        self.tree.heading('HTTPS', text='HTTPS')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('IP', width=180, anchor=tk.W, minwidth=150)
        self.tree.column('Porta', width=100, anchor=tk.CENTER, minwidth=80)
        self.tree.column('HTTP', width=180, anchor=tk.W, minwidth=150)
        self.tree.column('HTTPS', width=180, anchor=tk.W, minwidth=150)
        self.tree.column('Status', width=120, anchor=tk.CENTER, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
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
    
    def processar_portas(self) -> List[int]:
        """Processa texto de portas (separadas por vírgula) e retorna lista válida"""
        texto = self.portas_var.get().strip()
        if not texto:
            return []
        
        portas_validas = []
        partes = texto.split(',')
        
        for parte in partes:
            porta_str = parte.strip()
            if porta_str:
                try:
                    porta = int(porta_str)
                    if 1 <= porta <= 65535:  # Validação de porta válida
                        if porta not in portas_validas:  # Evita duplicatas
                            portas_validas.append(porta)
                except ValueError:
                    continue  # Ignora portas inválidas
        
        return portas_validas
    
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
            portas = self.processar_portas()
            timeout = int(self.timeout_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Timeout deve ser um número válido.")
            return
        
        if not portas:
            messagebox.showwarning("Aviso", "Por favor, insira pelo menos uma porta válida.")
            return
        
        # Limpa resultados anteriores
        self.tree.delete(*self.tree.get_children())
        self.resultados = []
        
        # Desabilita botão e inicia progresso
        self.executando = True
        self.ips_para_testar = ips.copy()
        self.ips_testados = 0
        self.btn_testar.config(state=tk.DISABLED, text="Executando...")
        self.btn_parar.config(state=tk.NORMAL)
        self.progress.start()
        self.progress_status_label.config(text="")
        
        # Executa em thread separada (por enquanto usa apenas a primeira porta)
        # TODO: Implementar múltiplas portas completamente
        porta = portas[0] if portas else 8080
        thread = threading.Thread(target=self._executar_testes_thread, args=(ips, porta, timeout))
        thread.daemon = True
        thread.start()
    
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
                total_ips = len(ips)
                
                for future in as_completed(futures):
                    if not self.executando:  # Verificar se foi cancelado
                        break
                    
                    ip = futures[future]
                    try:
                        resultado = future.result()
                        # Adiciona porta ao resultado
                        resultado['porta'] = porta
                        resultados.append(resultado)
                        self.ips_testados += 1
                        
                        # Atualiza interface
                        self.root.after(0, lambda r=resultado, i=ip, t=total_ips: self._adicionar_resultado(r, i, t))
                        
                    except Exception as e:
                        if self.executando:  # Só adiciona erro se não foi cancelado
                            resultado = {
                                'ip': ip,
                                'porta': porta,
                                'http': f'Erro: {str(e)}',
                                'https': f'Erro: {str(e)}'
                            }
                            resultados.append(resultado)
                            self.ips_testados += 1
                            self.root.after(0, lambda r=resultado, i=ip, t=total_ips: self._adicionar_resultado(r, i, t))
            
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
    
    def _adicionar_resultado(self, resultado: Dict, ip_atual: str = None, total: int = 0):
        """Adiciona um resultado à tabela"""
        ip = resultado['ip']
        porta = resultado.get('porta', 'N/A')
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
        
        # Insere na tabela (IP, Porta, HTTP, HTTPS, Status)
        self.tree.insert('', tk.END, values=(ip, porta, http, https, status), tags=(tag,))
        
        # Atualiza label de progresso
        if ip_atual and total > 0:
            self.progress_status_label.config(text=f"Testando: {ip_atual} ({self.ips_testados}/{total})")
    
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
                font=("Segoe UI", 13, "bold"),
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
        self.btn_parar.config(state=tk.DISABLED)
        self.progress.stop()
        self.progress_status_label.config(text="")
    
    def parar_testes(self):
        """Para os testes em andamento"""
        if self.executando:
            self.executando = False
            self.btn_testar.config(state=tk.NORMAL, text="▶ Executar Testes")
            self.btn_parar.config(state=tk.DISABLED)
            self.progress.stop()
            self.progress_status_label.config(text=f"Interrompido - {self.ips_testados} IP(s) testado(s)")
            # Atualiza estatísticas com os resultados já obtidos
            self._atualizar_estatisticas()
    
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
    
    # Melhora a nitidez configurando escala de fonte
    try:
        # Ajusta escala para melhor renderização
        root.tk.call('tk', 'scaling', 1.0)
    except:
        pass
    
    app = AppDesktop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
