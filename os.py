#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kali SmartOps Manager - Complete OS Utility
ALL features use PowerShell backend with full File Manager UI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import subprocess
import threading
import os
import math
import psutil
import platform
import socket
from datetime import datetime

class CompleteOSUtility:
    def __init__(self, root):
        self.root = root
        self.root.title("KALI SMARTOPS - COMPLETE OS UTILITY")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')
        self.root.minsize(1200, 700)
        
        # Colors
        self.colors = {
            'bg': '#0a0a0a', 'panel': '#1a1a1a', 'primary': '#00ff9d',
            'secondary': '#00d4ff', 'warning': '#ff3366', 'accent': '#ff00ff',
            'text': '#e0e0e0', 'text_dim': '#888888', 'grid': '#252525',
            'folder': '#ffaa00', 'file': '#00d4ff', 'success': '#00ff9d',
            'card': '#1e1e1e'
        }
        
        # Path to PowerShell backend
        self.ps_script = os.path.expanduser("~/complete_os.ps1")
        
        if not os.path.exists(self.ps_script):
            messagebox.showerror("Error", f"PowerShell script not found!\n\n{self.ps_script}")
            self.root.destroy()
            return
        
        # File manager variables
        self.current_directory = os.path.expanduser("~")
        self.clipboard_source = None
        self.clipboard_action = None
        self.current_process = None
        self.search_content = tk.BooleanVar(value=False)
        
        # Bootable drive variables
        self.usb_devices = []
        self.usb_drive = tk.StringVar()
        self.usb_drive_info = tk.StringVar()
        self.iso_path = tk.StringVar()
        
        # Storage format variables
        self.format_device = tk.StringVar()
        self.fs_type = tk.StringVar(value="ext4")
        self.volume_label = tk.StringVar()
        
        self.create_main_layout()
        self.start_system_monitors()
        
    def create_main_layout(self):
        """Create organized main layout"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header()
        
        # Content area
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Left Panel - System Monitor (Car Gauges)
        left_panel = tk.Frame(content_frame, bg=self.colors['panel'], width=450)
        left_panel.pack(side='left', fill='both', expand=False, padx=(0, 10))
        left_panel.pack_propagate(False)
        self.create_system_monitor_panel(left_panel)
        
        # Right Panel - Tabs
        right_panel = tk.Frame(content_frame, bg=self.colors['panel'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create all tabs
        self.create_file_manager_tab()
        self.create_process_tab()
        self.create_network_tab()
        self.create_security_tab()
        self.create_services_tab()
        self.create_packages_tab()
        self.create_disk_tab()
        self.create_cleanup_tab()
        self.create_hardware_tab()
        self.create_realtime_tab()
        self.create_bootable_drive_tab()    # COMPACT VERSION
        self.create_storage_format_tab()    # COMPACT VERSION
        
        self.create_status_bar()
        
    def create_header(self):
        header = tk.Frame(self.main_frame, bg=self.colors['primary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        logo_frame = tk.Frame(header, bg=self.colors['primary'])
        logo_frame.pack(side='left', padx=20)
        
        logo = tk.Label(logo_frame, text="⚡ KALI SMARTOPS", 
                       font=('Courier', 16, 'bold'),
                       bg=self.colors['primary'], fg='#000000')
        logo.pack()
        
        subtitle = tk.Label(logo_frame, text="Complete OS Utility Suite",
                           font=('Courier', 8), bg=self.colors['primary'], fg='#000000')
        subtitle.pack()
        
        stats_frame = tk.Frame(header, bg=self.colors['primary'])
        stats_frame.pack(side='left', padx=50)
        
        self.quick_cpu = tk.Label(stats_frame, text="CPU: 0%", font=('Courier', 10, 'bold'),
                                  bg=self.colors['primary'], fg='#000000')
        self.quick_cpu.pack(side='left', padx=10)
        
        self.quick_mem = tk.Label(stats_frame, text="RAM: 0%", font=('Courier', 10, 'bold'),
                                  bg=self.colors['primary'], fg='#000000')
        self.quick_mem.pack(side='left', padx=10)
        
        self.quick_disk = tk.Label(stats_frame, text="DISK: 0%", font=('Courier', 10, 'bold'),
                                   bg=self.colors['primary'], fg='#000000')
        self.quick_disk.pack(side='left', padx=10)
        
        time_frame = tk.Frame(header, bg=self.colors['primary'])
        time_frame.pack(side='right', padx=20)
        
        self.time_label = tk.Label(time_frame, text="", font=('Courier', 12, 'bold'),
                                   bg=self.colors['primary'], fg='#000000')
        self.time_label.pack()
        self.update_time()
        
        self.stop_btn = tk.Button(header, text="⏹️ STOP", command=self.stop_process,
                                  bg=self.colors['warning'], fg='#000000',
                                  font=('Courier', 10, 'bold'), relief='flat',
                                  padx=15, pady=5)
        self.stop_btn.pack(side='right', padx=20)
        
    def create_system_monitor_panel(self, parent):
        title = tk.Label(parent, text="SYSTEM TELEMETRY", font=('Courier', 14, 'bold'),
                        bg=self.colors['panel'], fg=self.colors['primary'])
        title.pack(pady=15)
        
        # CPU Gauge
        cpu_container = tk.Frame(parent, bg=self.colors['card'], relief='ridge', bd=1)
        cpu_container.pack(fill='x', padx=15, pady=10)
        self.cpu_frame = cpu_container
        self.create_speedometer(cpu_container, "CPU USAGE", self.colors['primary'])
        
        # Memory Gauge
        mem_container = tk.Frame(parent, bg=self.colors['card'], relief='ridge', bd=1)
        mem_container.pack(fill='x', padx=15, pady=10)
        self.mem_frame = mem_container
        self.create_fuel_gauge(mem_container, "MEMORY USAGE", self.colors['secondary'])
        
        # Disk Gauge
        disk_container = tk.Frame(parent, bg=self.colors['card'], relief='ridge', bd=1)
        disk_container.pack(fill='x', padx=15, pady=10)
        self.disk_frame = disk_container
        self.create_temp_gauge(disk_container, "DISK USAGE", self.colors['warning'])
        
        info_frame = tk.Frame(parent, bg=self.colors['card'], relief='ridge', bd=1)
        info_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        tk.Label(info_frame, text="SYSTEM INFORMATION", font=('Courier', 10, 'bold'),
                bg=self.colors['card'], fg=self.colors['accent']).pack(pady=5)
        
        self.system_info_text = tk.Text(info_frame, height=8, bg=self.colors['grid'],
                                        fg=self.colors['text'], font=('Courier', 9),
                                        relief='flat', wrap='word')
        self.system_info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.run_powershell_feature(1, self.system_info_text, is_text_widget=True)
        
    def create_speedometer(self, parent, title, color):
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill='x', pady=5)
        
        tk.Label(frame, text=title, font=('Courier', 11, 'bold'),
                bg=self.colors['card'], fg=color).pack()
        
        canvas = tk.Canvas(parent, width=280, height=150, bg=self.colors['card'],
                          highlightthickness=0)
        canvas.pack(pady=5)
        
        canvas.create_arc(30, 20, 250, 140, start=180, extent=180,
                         outline=color, width=5, style='arc')
        
        for angle in range(0, 181, 18):
            rad = math.radians(180 - angle)
            x1 = 140 + 90 * math.cos(rad)
            y1 = 80 - 90 * math.sin(rad)
            x2 = 140 + 100 * math.cos(rad)
            y2 = 80 - 100 * math.sin(rad)
            canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
            
        labels = [('0%', 180), ('25%', 135), ('50%', 90), ('75%', 45), ('100%', 0)]
        for text, angle in labels:
            rad = math.radians(180 - angle)
            x = 140 + 115 * math.cos(rad)
            y = 80 - 115 * math.sin(rad)
            canvas.create_text(x, y, text=text, fill=self.colors['text_dim'],
                              font=('Courier', 7))
        
        needle = canvas.create_line(140, 80, 140, 25, width=3, fill=color, capstyle='round')
        canvas.create_oval(135, 75, 145, 85, fill=color, outline='')
        
        display = tk.Label(parent, text="0%", font=('Courier', 20, 'bold'),
                          bg=self.colors['card'], fg=color)
        display.pack(pady=5)
        
        parent.canvas = canvas
        parent.needle = needle
        parent.display = display
        
    def create_fuel_gauge(self, parent, title, color):
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill='x', pady=5)
        
        tk.Label(frame, text=title, font=('Courier', 11, 'bold'),
                bg=self.colors['card'], fg=color).pack()
        
        canvas = tk.Canvas(parent, width=280, height=150, bg=self.colors['card'],
                          highlightthickness=0)
        canvas.pack(pady=5)
        
        canvas.create_rectangle(90, 25, 190, 125, fill=self.colors['grid'], 
                               outline=color, width=2)
        fill_bar = canvas.create_rectangle(92, 123, 188, 123, fill=color, outline='')
        
        for y, label in [(123, 'EMPTY'), (74, 'HALF'), (27, 'FULL')]:
            canvas.create_line(85, y, 90, y, fill=color, width=2)
            canvas.create_text(75, y, text=label, fill=self.colors['text_dim'],
                              font=('Courier', 6), anchor='e')
        
        display = tk.Label(parent, text="0%", font=('Courier', 20, 'bold'),
                          bg=self.colors['card'], fg=color)
        display.pack(pady=5)
        
        parent.canvas = canvas
        parent.fill_bar = fill_bar
        parent.display = display
        
    def create_temp_gauge(self, parent, title, color):
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill='x', pady=5)
        
        tk.Label(frame, text=title, font=('Courier', 11, 'bold'),
                bg=self.colors['card'], fg=color).pack()
        
        canvas = tk.Canvas(parent, width=280, height=150, bg=self.colors['card'],
                          highlightthickness=0)
        canvas.pack(pady=5)
        
        zones = [(180, 135, self.colors['success']),
                 (135, 90, '#ffff00'),
                 (90, 45, '#ff6600'),
                 (45, 0, self.colors['warning'])]
        
        for start, end, zone_color in zones:
            canvas.create_arc(50, 30, 230, 150, start=start, extent=45,
                             outline=zone_color, width=8, style='arc')
        
        needle = canvas.create_line(140, 90, 140, 45, width=3, fill=color, capstyle='round')
        canvas.create_oval(135, 85, 145, 95, fill=color, outline='')
        
        for text, angle in [('GOOD', 160), ('WARN', 115), ('HIGH', 70), ('CRITICAL', 25)]:
            rad = math.radians(180 - angle)
            x = 140 + 115 * math.cos(rad)
            y = 90 - 115 * math.sin(rad)
            canvas.create_text(x, y, text=text, fill=self.colors['text_dim'],
                              font=('Courier', 6))
        
        display = tk.Label(parent, text="0%", font=('Courier', 20, 'bold'),
                          bg=self.colors['card'], fg=color)
        display.pack(pady=5)
        
        parent.canvas = canvas
        parent.needle = needle
        parent.display = display
        
    # ============ FILE MANAGER TAB ============
    def create_file_manager_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="📁 FILE MANAGER")
        
        # Top toolbar
        toolbar = tk.Frame(tab, bg=self.colors['panel'], height=35)
        toolbar.pack(fill='x', padx=5, pady=5)
        toolbar.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("◀", self.go_back), ("▶", self.go_forward), ("⬆", self.go_up),
            ("🏠", self.go_home), ("🔄", self.refresh_files)
        ]
        for text, cmd in nav_buttons:
            btn = tk.Button(toolbar, text=text, command=cmd,
                           bg=self.colors['primary'], fg='#000000',
                           font=('Courier', 9), width=3)
            btn.pack(side='left', padx=2)
        
        tk.Label(toolbar, text="│", bg=self.colors['panel'], fg=self.colors['text_dim']).pack(side='left', padx=5)
        
        # File operation buttons
        file_buttons = [
            ("📋 COPY", self.copy_file), ("✂ CUT", self.cut_file), ("📌 PASTE", self.paste_file),
            ("🗑 DELETE", self.delete_file), ("✏ RENAME", self.rename_file), ("📁 NEW", self.new_folder)
        ]
        for text, cmd in file_buttons:
            btn = tk.Button(toolbar, text=text, command=cmd,
                           bg=self.colors['secondary'], fg='#000000',
                           font=('Courier', 9))
            btn.pack(side='left', padx=2)
        
        tk.Label(toolbar, text="│", bg=self.colors['panel'], fg=self.colors['text_dim']).pack(side='left', padx=5)
        
        # Search
        self.search_entry = tk.Entry(toolbar, bg=self.colors['grid'], fg=self.colors['text'],
                                     font=('Courier', 9), width=20)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', self.search_files)
        
        tk.Button(toolbar, text="🔍", command=self.search_files,
                 bg=self.colors['secondary'], fg='#000000').pack(side='left', padx=2)
        
        # Search inside files checkbox
        tk.Checkbutton(toolbar, text="Search inside files", variable=self.search_content,
                       bg=self.colors['panel'], fg=self.colors['text'],
                       selectcolor=self.colors['panel']).pack(side='left', padx=5)
        
        self.path_label = tk.Label(toolbar, text=self.current_directory,
                                   bg=self.colors['panel'], fg=self.colors['secondary'],
                                   font=('Courier', 9))
        self.path_label.pack(side='left', padx=20)
        
        # Main content area - Treeview for file list
        self.file_tree = ttk.Treeview(tab, columns=('SIZE', 'MODIFIED', 'PERMS'),
                                      show='tree headings', selectmode='extended')
        self.file_tree.heading('#0', text='NAME')
        self.file_tree.heading('SIZE', text='SIZE')
        self.file_tree.heading('MODIFIED', text='MODIFIED')
        self.file_tree.heading('PERMS', text='PERMISSIONS')
        
        self.file_tree.column('#0', width=400)
        self.file_tree.column('SIZE', width=100)
        self.file_tree.column('MODIFIED', width=150)
        self.file_tree.column('PERMS', width=80)
        
        # Scrollbars
        v_scroll = tk.Scrollbar(tab, orient='vertical', command=self.file_tree.yview)
        h_scroll = tk.Scrollbar(tab, orient='horizontal', command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.file_tree.pack(fill='both', expand=True, padx=5, pady=5, side='left')
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        
        # Preview panel
        preview_frame = tk.Frame(tab, bg=self.colors['panel'], height=120)
        preview_frame.pack(fill='x', padx=5, pady=5)
        preview_frame.pack_propagate(False)
        
        tk.Label(preview_frame, text="📄 PREVIEW", font=('Courier', 9, 'bold'),
                bg=self.colors['panel'], fg=self.colors['primary']).pack(pady=2)
        
        self.preview_text = tk.Text(preview_frame, height=5, bg=self.colors['grid'],
                                    fg=self.colors['text'], font=('Courier', 9),
                                    relief='flat', wrap='word')
        self.preview_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.refresh_files()
        
    def refresh_files(self):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        try:
            items = os.listdir(self.current_directory)
            for item in sorted(items):
                full_path = os.path.join(self.current_directory, item)
                try:
                    stat_info = os.stat(full_path)
                    size = self.format_size(stat_info.st_size)
                    modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    perms = oct(stat_info.st_mode)[-3:]
                    
                    if os.path.isdir(full_path):
                        icon = "📁"
                        tag = 'dir'
                    elif os.access(full_path, os.X_OK):
                        icon = "⚡"
                        tag = 'exec'
                    else:
                        icon = "📄"
                        tag = 'file'
                    
                    self.file_tree.insert('', 'end', text=f"{icon} {item}",
                                         values=(size, modified, perms),
                                         tags=(tag,))
                except:
                    pass
            
            self.file_tree.tag_configure('dir', foreground=self.colors['folder'])
            self.file_tree.tag_configure('exec', foreground=self.colors['warning'])
            self.file_tree.tag_configure('file', foreground=self.colors['file'])
            
            self.path_label.config(text=self.current_directory)
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"Error: {e}")
            
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
        
    def on_file_double_click(self, event):
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name = item['text'][2:]
            full_path = os.path.join(self.current_directory, name)
            
            if os.path.isdir(full_path):
                self.current_directory = full_path
                self.refresh_files()
            else:
                self.preview_file(full_path)
                
    def preview_file(self, path):
        self.preview_text.delete(1.0, tk.END)
        if path.endswith(('.txt', '.py', '.sh', '.md', '.conf', '.json', '.xml')):
            try:
                with open(path, 'r') as f:
                    content = f.read(5000)
                    self.preview_text.insert(1.0, content)
                    if len(content) >= 5000:
                        self.preview_text.insert(tk.END, "\n\n... (truncated)")
            except:
                self.preview_text.insert(1.0, "Cannot preview file")
        else:
            try:
                stat_info = os.stat(path)
                info = f"File: {os.path.basename(path)}\n"
                info += f"Size: {self.format_size(stat_info.st_size)}\n"
                info += f"Modified: {datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                info += f"Permissions: {oct(stat_info.st_mode)[-3:]}"
                self.preview_text.insert(1.0, info)
            except:
                self.preview_text.insert(1.0, "Cannot preview this file type")
                
    def go_back(self):
        parent = os.path.dirname(self.current_directory)
        if parent != self.current_directory:
            self.current_directory = parent
            self.refresh_files()
            
    def go_forward(self):
        self.go_home()
        
    def go_up(self):
        parent = os.path.dirname(self.current_directory)
        if parent != self.current_directory:
            self.current_directory = parent
            self.refresh_files()
            
    def go_home(self):
        self.current_directory = os.path.expanduser("~")
        self.refresh_files()
        
    def copy_file(self):
        selection = self.file_tree.selection()
        if selection:
            name = self.file_tree.item(selection[0])['text'][2:]
            self.clipboard_source = os.path.join(self.current_directory, name)
            self.clipboard_action = 'copy'
            self.status_text.config(text=f"Copied: {name}")
            
    def cut_file(self):
        selection = self.file_tree.selection()
        if selection:
            name = self.file_tree.item(selection[0])['text'][2:]
            self.clipboard_source = os.path.join(self.current_directory, name)
            self.clipboard_action = 'cut'
            self.status_text.config(text=f"Cut: {name}")
            
    def paste_file(self):
        if not self.clipboard_source:
            return
        
        dest = os.path.join(self.current_directory, os.path.basename(self.clipboard_source))
        
        if self.clipboard_action == 'copy':
            self.run_powershell_feature(14, None, extra_args={'Source': self.clipboard_source, 'Destination': dest})
        else:
            self.run_powershell_feature(15, None, extra_args={'Source': self.clipboard_source, 'Destination': dest})
        
        self.refresh_files()
        self.clipboard_source = None
        self.status_text.config(text="Paste completed")
        
    def delete_file(self):
        selection = self.file_tree.selection()
        if selection and messagebox.askyesno("Confirm Delete", "Delete selected item(s)?"):
            for item in selection:
                name = self.file_tree.item(item)['text'][2:]
                path = os.path.join(self.current_directory, name)
                self.run_powershell_feature(16, None, extra_args={'Path': path})
            self.refresh_files()
            
    def rename_file(self):
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            old_name = self.file_tree.item(item)['text'][2:]
            new_name = simpledialog.askstring("Rename", "New name:", initialvalue=old_name)
            if new_name:
                old_path = os.path.join(self.current_directory, old_name)
                self.run_powershell_feature(17, None, extra_args={'Path': old_path, 'Destination': new_name})
                self.refresh_files()
                
    def new_folder(self):
        name = simpledialog.askstring("New Folder", "Folder name:")
        if name:
            path = os.path.join(self.current_directory, name)
            self.run_powershell_feature(18, None, extra_args={'Path': path})
            self.refresh_files()
            
    def search_files(self, event=None):
        pattern = self.search_entry.get()
        if not pattern:
            return
        
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        search_in_content = self.search_content.get()
        
        def search():
            found = 0
            for root, dirs, files in os.walk(self.current_directory):
                for name in files + dirs:
                    if pattern.lower() in name.lower():
                        full_path = os.path.join(root, name)
                        try:
                            stat_info = os.stat(full_path)
                            size = self.format_size(stat_info.st_size)
                            modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                            perms = oct(stat_info.st_mode)[-3:]
                            rel_path = os.path.relpath(full_path, self.current_directory)
                            self.file_tree.insert('', 'end', text=f"📄 {rel_path}",
                                                 values=(size, modified, perms))
                            found += 1
                        except:
                            pass
                    
                    if search_in_content and not os.path.isdir(os.path.join(root, name)):
                        if name.endswith(('.txt', '.py', '.sh', '.md', '.conf', '.log')):
                            try:
                                with open(os.path.join(root, name), 'r', errors='ignore') as f:
                                    content = f.read(50000)
                                    if pattern.lower() in content.lower():
                                        full_path = os.path.join(root, name)
                                        stat_info = os.stat(full_path)
                                        size = self.format_size(stat_info.st_size)
                                        modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                                        perms = oct(stat_info.st_mode)[-3:]
                                        rel_path = os.path.relpath(full_path, self.current_directory)
                                        self.file_tree.insert('', 'end', text=f"📄 {rel_path} (content match)",
                                                             values=(size, modified, perms))
                                        found += 1
                            except:
                                pass
            
            self.status_text.config(text=f"Search completed - found {found} matches")
        
        threading.Thread(target=search, daemon=True).start()
        
    # ============ COMPACT BOOTABLE DRIVE TAB ============
    def create_bootable_drive_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="💿 BOOTABLE DRIVE")
        
        # Warning banner (smaller)
        warning_frame = tk.Frame(tab, bg=self.colors['warning'], height=25)
        warning_frame.pack(fill='x', padx=20, pady=5)
        warning_frame.pack_propagate(False)
        tk.Label(warning_frame, text="⚠️ WARNING: This will DESTROY ALL DATA on the selected drive! ⚠️",
                font=('Courier', 9, 'bold'), bg=self.colors['warning'], fg='#000000').pack(pady=3)
        
        card = self.create_compact_card(tab, "Create Bootable USB Drive", 
                                         "Write ISO image to USB drive")
        output = self.create_compact_output_area(card, height=8)
        
        # Two-column layout for compactness
        top_frame = tk.Frame(card, bg=self.colors['card'])
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Left column - USB Device
        left_frame = tk.Frame(top_frame, bg=self.colors['card'])
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(left_frame, text="USB Device:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Courier', 9)).pack(anchor='w')
        
        usb_menu = ttk.Combobox(left_frame, textvariable=self.usb_drive, width=35)
        usb_menu.pack(pady=2, fill='x')
        
        # Device info label (smaller)
        device_info_label = tk.Label(left_frame, textvariable=self.usb_drive_info, 
                                      bg=self.colors['card'], fg=self.colors['text_dim'],
                                      font=('Courier', 7))
        device_info_label.pack(anchor='w')
        
        # Right column - ISO File
        right_frame = tk.Frame(top_frame, bg=self.colors['card'])
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        tk.Label(right_frame, text="ISO File:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Courier', 9)).pack(anchor='w')
        
        iso_entry = tk.Entry(right_frame, textvariable=self.iso_path, width=35,
                             bg=self.colors['grid'], fg=self.colors['text'])
        iso_entry.pack(pady=2, fill='x')
        
        # Button row
        btn_frame = tk.Frame(card, bg=self.colors['card'])
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        def refresh_usb_drives():
            output.delete(1.0, tk.END)
            output.insert(tk.END, "🔍 Detecting USB drives...\n", 'info')
            
            def execute():
                result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,MODEL,TRAN', '-n'], 
                                       capture_output=True, text=True)
                drives = []
                self.usb_devices = []
                
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 2:
                            name = parts[0]
                            size = parts[1]
                            model = parts[2] if len(parts) > 2 else "USB Drive"
                            transport = parts[3] if len(parts) > 3 else ""
                            
                            is_usb = transport == 'usb' or name.startswith('sd')
                            
                            if name != 'sda' and name != 'nvme0n1' and is_usb:
                                display_text = f"/dev/{name} - {size}"
                                drives.append(display_text)
                                self.usb_devices.append({'device': f"/dev/{name}", 'size': size, 'model': model})
                                output.insert(tk.END, f"  💾 {display_text}\n", 'info')
                
                usb_menu['values'] = drives
                if drives and not self.usb_drive.get():
                    self.usb_drive.set(drives[0])
                    self.usb_drive_info.set(f"{self.usb_devices[0]['device']} ({self.usb_devices[0]['size']})")
                
                if not drives:
                    output.insert(tk.END, "⚠️ No USB drives found\n", 'warning')
                else:
                    output.insert(tk.END, f"\n✅ Found {len(drives)} drive(s)\n", 'success')
            
            threading.Thread(target=execute, daemon=True).start()
        
        def on_device_select(event):
            selection = self.usb_drive.get()
            for drive in self.usb_devices:
                if selection.startswith(drive['device']):
                    self.usb_drive_info.set(f"{drive['device']} ({drive['size']})")
                    break
        
        usb_menu.bind('<<ComboboxSelected>>', on_device_select)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Refresh", command=refresh_usb_drives,
                                bg=self.colors['secondary'], fg='#000000', font=('Courier', 8))
        refresh_btn.pack(side='left', padx=2)
        
        browse_btn = tk.Button(btn_frame, text="📁 Browse", command=self.browse_iso_file,
                               bg=self.colors['secondary'], fg='#000000', font=('Courier', 8))
        browse_btn.pack(side='left', padx=2)
        
        def auto_detect_iso():
            output.insert(tk.END, "🔍 Searching for ISO files...\n", 'info')
            
            def execute():
                iso_found = []
                search_paths = ['~/Downloads', '~/Desktop', '~/']
                
                for search_path in search_paths:
                    expanded_path = os.path.expanduser(search_path)
                    if os.path.exists(expanded_path):
                        try:
                            for file in os.listdir(expanded_path):
                                if file.lower().endswith('.iso') and os.path.isfile(os.path.join(expanded_path, file)):
                                    full_path = os.path.join(expanded_path, file)
                                    size_mb = os.path.getsize(full_path) / (1024 * 1024)
                                    iso_found.append(full_path)
                                    output.insert(tk.END, f"  💿 Found: {file} ({size_mb:.0f} MB)\n", 'info')
                        except:
                            pass
                
                if iso_found and not self.iso_path.get():
                    iso_found.sort(key=lambda x: os.path.getsize(x), reverse=True)
                    self.iso_path.set(iso_found[0])
                    output.insert(tk.END, f"\n✅ Auto-selected: {os.path.basename(iso_found[0])}\n", 'success')
                elif not iso_found:
                    output.insert(tk.END, "ℹ️ No ISO files found\n", 'info')
            
            threading.Thread(target=execute, daemon=True).start()
        
        auto_iso_btn = tk.Button(btn_frame, text="🔍 Auto ISO", command=auto_detect_iso,
                                  bg=self.colors['accent'], fg='#000000', font=('Courier', 8))
        auto_iso_btn.pack(side='left', padx=2)
        
        # Create button
        def create_bootable():
            device = self.usb_drive.get().split()[0] if ' ' in self.usb_drive.get() else self.usb_drive.get()
            iso = self.iso_path.get()
            
            if not device or not iso:
                output.insert(tk.END, "❌ Please select device and ISO\n", 'error')
                return
            
            if not os.path.exists(device) or not os.path.exists(iso):
                output.insert(tk.END, "❌ Device or ISO not found\n", 'error')
                return
            
            device_size = subprocess.run(f'lsblk -d -o SIZE -n {device} 2>/dev/null | head -1', 
                                         shell=True, capture_output=True, text=True).stdout.strip()
            iso_size_mb = os.path.getsize(iso) / (1024 * 1024)
            
            if messagebox.askyesno("⚠️ DESTRUCTIVE OPERATION ⚠️", 
                                   f"Device: {device} ({device_size})\nISO: {os.path.basename(iso)} ({iso_size_mb:.0f} MB)\n\n"
                                   f"This will COMPLETELY WIPE all data on {device}!\n\nContinue?"):
                output.delete(1.0, tk.END)
                output.insert(tk.END, f"📀 Creating bootable drive on {device}...\n", 'info')
                output.insert(tk.END, "⚠️ This may take several minutes\n", 'warning')
                
                def execute():
                    try:
                        subprocess.run(f'sudo umount {device}* 2>/dev/null', shell=True)
                        cmd = f'sudo dd if="{iso}" of={device} bs=4M status=progress conv=fsync'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            output.insert(tk.END, "\n✅ Bootable USB created successfully!\n", 'success')
                        else:
                            output.insert(tk.END, f"\n❌ Error: {result.stderr}\n", 'error')
                    except Exception as e:
                        output.insert(tk.END, f"\n❌ Error: {str(e)}\n", 'error')
                
                threading.Thread(target=execute, daemon=True).start()
        
        create_btn = tk.Button(card, text="💿 CREATE BOOTABLE DRIVE", command=create_bootable,
                               bg=self.colors['warning'], fg='#000000',
                               font=('Courier', 10, 'bold'), padx=10, pady=5)
        create_btn.pack(pady=5)
        
        refresh_usb_drives()
        
    # ============ COMPACT STORAGE FORMAT TAB ============
    def create_storage_format_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="💾 STORAGE FORMAT")
        
        # Warning banner (smaller)
        warning_frame = tk.Frame(tab, bg=self.colors['warning'], height=25)
        warning_frame.pack(fill='x', padx=20, pady=5)
        warning_frame.pack_propagate(False)
        tk.Label(warning_frame, text="⚠️ WARNING: Formatting will DESTROY ALL DATA on the selected device! ⚠️",
                font=('Courier', 9, 'bold'), bg=self.colors['warning'], fg='#000000').pack(pady=3)
        
        card = self.create_compact_card(tab, "Format Storage Device", 
                                         "Format USB drive or partition")
        output = self.create_compact_output_area(card, height=8)
        
        # Two-column layout
        top_frame = tk.Frame(card, bg=self.colors['card'])
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Left column - Device
        left_frame = tk.Frame(top_frame, bg=self.colors['card'])
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(left_frame, text="Device:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Courier', 9)).pack(anchor='w')
        
        device_menu = ttk.Combobox(left_frame, textvariable=self.format_device, width=35)
        device_menu.pack(pady=2, fill='x')
        
        self.format_device_info = tk.StringVar()
        device_info_label = tk.Label(left_frame, textvariable=self.format_device_info, 
                                      bg=self.colors['card'], fg=self.colors['text_dim'],
                                      font=('Courier', 7))
        device_info_label.pack(anchor='w')
        
        # Right column - Filesystem
        right_frame = tk.Frame(top_frame, bg=self.colors['card'])
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        tk.Label(right_frame, text="Filesystem:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Courier', 9)).pack(anchor='w')
        
        fs_menu = ttk.Combobox(right_frame, textvariable=self.fs_type, 
                               values=['ext4', 'ntfs', 'fat32', 'exfat'], width=20)
        fs_menu.pack(pady=2, anchor='w')
        
        tk.Label(right_frame, text="Label (optional):", bg=self.colors['card'], fg=self.colors['text'],
                font=('Courier', 8)).pack(anchor='w')
        label_entry = tk.Entry(right_frame, textvariable=self.volume_label, width=20,
                               bg=self.colors['grid'], fg=self.colors['text'])
        label_entry.pack(pady=2, anchor='w')
        
        # Button row
        btn_frame = tk.Frame(card, bg=self.colors['card'])
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        def refresh_devices():
            output.delete(1.0, tk.END)
            output.insert(tk.END, "🔍 Detecting storage devices...\n", 'info')
            
            def execute():
                result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT', '-n'], 
                                       capture_output=True, text=True)
                devices = []
                self.storage_devices = []
                
                for line in result.stdout.split('\n'):
                    if line.strip() and ('disk' in line or 'part' in line):
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            size = parts[1]
                            dtype = parts[2] if len(parts) > 2 else 'disk'
                            mount = parts[3] if len(parts) > 3 and parts[3] else ''
                            mount_info = f" (mounted)" if mount else ""
                            
                            if name != 'sda' and name != 'nvme0n1':
                                display_text = f"/dev/{name} ({size}) - {dtype}{mount_info}"
                                devices.append(display_text)
                                self.storage_devices.append({'device': f"/dev/{name}", 'size': size, 'type': dtype, 'mount': mount})
                                output.insert(tk.END, f"  💾 {display_text}\n", 'info')
                
                device_menu['values'] = devices
                if not devices:
                    output.insert(tk.END, "⚠️ No additional storage devices found\n", 'warning')
                else:
                    output.insert(tk.END, f"\n✅ Found {len(devices)} device(s)\n", 'success')
            
            threading.Thread(target=execute, daemon=True).start()
        
        def on_device_select_format(event):
            selection = self.format_device.get()
            for device in getattr(self, 'storage_devices', []):
                if selection.startswith(device['device']):
                    mount_info = f" - MOUNTED" if device['mount'] else ""
                    self.format_device_info.set(f"{device['device']} ({device['size']}) - {device['type']}{mount_info}")
                    break
        
        device_menu.bind('<<ComboboxSelected>>', on_device_select_format)
        
        refresh_btn = tk.Button(btn_frame, text="🔄 Refresh", command=refresh_devices,
                                bg=self.colors['secondary'], fg='#000000', font=('Courier', 8))
        refresh_btn.pack(side='left', padx=2)
        
        def format_device():
            device = self.format_device.get().split()[0] if ' ' in self.format_device.get() else self.format_device.get()
            fs = self.fs_type.get()
            label = self.volume_label.get()
            
            if not device:
                output.insert(tk.END, "❌ Please select a device\n", 'error')
                return
            
            if not os.path.exists(device):
                output.insert(tk.END, f"❌ Device {device} does not exist!\n", 'error')
                return
            
            # Check if mounted
            result = subprocess.run(f'mount | grep {device}', shell=True, capture_output=True, text=True)
            if result.stdout:
                output.insert(tk.END, f"⚠️ {device} is mounted. Please unmount first.\n", 'warning')
                return
            
            if messagebox.askyesno("⚠️ DESTRUCTIVE OPERATION ⚠️", 
                                   f"Device: {device}\n\nThis will COMPLETELY ERASE all data!\n\n"
                                   f"Format as {fs}?\n\nContinue?"):
                output.delete(1.0, tk.END)
                output.insert(tk.END, f"💾 Formatting {device} as {fs}...\n", 'info')
                
                def execute():
                    try:
                        if fs == 'ext4':
                            cmd = f'sudo mkfs.ext4 -F {device}'
                            if label:
                                cmd = f'sudo mkfs.ext4 -F -L "{label}" {device}'
                        elif fs == 'ntfs':
                            cmd = f'sudo mkfs.ntfs -F {device}'
                            if label:
                                cmd = f'sudo mkfs.ntfs -F -L "{label}" {device}'
                        elif fs == 'fat32':
                            cmd = f'sudo mkfs.fat -F 32 {device}'
                            if label:
                                cmd = f'sudo mkfs.fat -F 32 -n "{label}" {device}'
                        elif fs == 'exfat':
                            cmd = f'sudo mkfs.exfat {device}'
                            if label:
                                cmd = f'sudo mkfs.exfat -n "{label}" {device}'
                        else:
                            output.insert(tk.END, f"❌ Unsupported filesystem: {fs}\n", 'error')
                            return
                        
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.returncode == 0:
                            output.insert(tk.END, f"\n✅ Device formatted successfully as {fs}!\n", 'success')
                            if label:
                                output.insert(tk.END, f"🏷️ Label: {label}\n", 'success')
                        else:
                            output.insert(tk.END, f"\n❌ Error: {result.stderr}\n", 'error')
                    except Exception as e:
                        output.insert(tk.END, f"\n❌ Error: {str(e)}\n", 'error')
                
                threading.Thread(target=execute, daemon=True).start()
        
        format_btn = tk.Button(btn_frame, text="💾 FORMAT", command=format_device,
                               bg=self.colors['warning'], fg='#000000',
                               font=('Courier', 10, 'bold'))
        format_btn.pack(side='left', padx=2)
        
        refresh_devices()
        
    def create_compact_card(self, parent, title, description):
        """Create a compact feature card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='ridge', bd=1)
        card.pack(fill='x', padx=20, pady=5)
        
        if title:
            tk.Label(card, text=title, font=('Courier', 10, 'bold'),
                    bg=self.colors['card'], fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(5,0))
        if description:
            tk.Label(card, text=description, font=('Courier', 7),
                    bg=self.colors['card'], fg=self.colors['text_dim']).pack(anchor='w', padx=10)
        return card
    
    def create_compact_output_area(self, parent, height=6):
        """Create a compact output area"""
        output_frame = tk.Frame(parent, bg=self.colors['grid'])
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        output_text = tk.Text(output_frame, wrap=tk.WORD, font=('Consolas', 8),
                               bg=self.colors['grid'], fg=self.colors['text'],
                               relief='flat', height=height)
        scrollbar = tk.Scrollbar(output_frame, orient='vertical', command=output_text.yview)
        output_text.configure(yscrollcommand=scrollbar.set)
        output_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        output_text.tag_config('info', foreground=self.colors['secondary'])
        output_text.tag_config('success', foreground=self.colors['primary'])
        output_text.tag_config('warning', foreground=self.colors['warning'])
        output_text.tag_config('error', foreground=self.colors['warning'])
        output_text.tag_config('header', foreground=self.colors['accent'])
        
        return output_text
        
    def browse_iso_file(self):
        """Browse for ISO file"""
        filename = filedialog.askopenfilename(
            title="Select ISO File",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        if filename:
            self.iso_path.set(filename)
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            if hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, f"📀 Selected: {os.path.basename(filename)} ({size_mb:.0f} MB)\n", 'info')
        
    # ============ OTHER FEATURE TABS ============
    def create_process_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🔍 PROCESS MANAGER")
        card = self.create_feature_card(tab, "Process Manager", "View and manage running processes")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Process Monitor", 
                       command=lambda: self.run_powershell_feature(2, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_network_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🌐 NETWORK TOOLS")
        
        canvas = tk.Canvas(tab, bg=self.colors['bg'], highlightthickness=0)
        v_scrollbar = tk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        inner_frame = tk.Frame(canvas, bg=self.colors['bg'])
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        
        card1 = self.create_feature_card(inner_frame, "Network Information", "")
        output1 = self.create_output_area(card1)
        btn1 = tk.Button(card1, text="▶ Show Network Info", 
                        command=lambda: self.run_powershell_feature(4, output1, clear_first=True),
                        bg=self.colors['secondary'], fg='#000000',
                        font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn1.pack(pady=10)
        
        card2 = self.create_feature_card(inner_frame, "Bandwidth Statistics", "")
        output2 = self.create_output_area(card2)
        btn2 = tk.Button(card2, text="▶ Show Bandwidth Stats", 
                        command=lambda: self.run_powershell_feature(5, output2, clear_first=True),
                        bg=self.colors['secondary'], fg='#000000',
                        font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn2.pack(pady=10)
        
        card3 = self.create_feature_card(inner_frame, "Port Scanner", "")
        output3 = self.create_output_area(card3)
        btn3 = tk.Button(card3, text="▶ Run Port Scan", 
                        command=lambda: self.run_powershell_feature(6, output3, clear_first=True),
                        bg=self.colors['secondary'], fg='#000000',
                        font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn3.pack(pady=10)
        
        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(1, width=e.width))
        
    def create_security_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🔒 SECURITY")
        card = self.create_feature_card(tab, "Security Check", "Detect suspicious processes")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Security Check", 
                       command=lambda: self.run_powershell_feature(10, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_services_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🔄 SERVICES")
        card = self.create_feature_card(tab, "Service Manager", "Manage system services")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Service Manager", 
                       command=lambda: self.run_powershell_feature(7, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_packages_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="📦 PACKAGES")
        card = self.create_feature_card(tab, "Package Manager", "Update system packages")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Check Package Updates", 
                       command=lambda: self.run_powershell_feature(11, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_disk_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="💾 DISK ANALYZER")
        card = self.create_feature_card(tab, "Disk Analysis", "Analyze disk usage")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Disk Analysis", 
                       command=lambda: self.run_powershell_feature(8, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_cleanup_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🧹 CLEANUP TOOLS")
        card = self.create_feature_card(tab, "Cleanup Tools", "Remove temporary files")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Cleanup Tools", 
                       command=lambda: self.run_powershell_feature(9, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_hardware_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="💻 HARDWARE INFO")
        card = self.create_feature_card(tab, "Hardware Information", "View system hardware")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Hardware Info", 
                       command=lambda: self.run_powershell_feature(12, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_realtime_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="📈 REAL-TIME MONITOR")
        card = self.create_feature_card(tab, "Real-time Monitor", "Live system monitoring")
        output = self.create_output_area(card)
        btn = tk.Button(card, text="▶ Run Real-time Monitor", 
                       command=lambda: self.run_powershell_feature(3, output, clear_first=True),
                       bg=self.colors['secondary'], fg='#000000',
                       font=('Courier', 10, 'bold'), relief='flat', padx=20, pady=8)
        btn.pack(pady=10)
        
    def create_feature_card(self, parent, title, description):
        card = tk.Frame(parent, bg=self.colors['card'], relief='ridge', bd=1)
        card.pack(fill='both', expand=True, padx=20, pady=10)
        
        if title:
            tk.Label(card, text=title, font=('Courier', 12, 'bold'),
                    bg=self.colors['card'], fg=self.colors['primary']).pack(anchor='w', padx=15, pady=(10,0))
        if description:
            tk.Label(card, text=description, font=('Courier', 9),
                    bg=self.colors['card'], fg=self.colors['text_dim']).pack(anchor='w', padx=15)
        return card
        
    def create_output_area(self, parent, expand=True):
        output_frame = tk.Frame(parent, bg=self.colors['grid'])
        output_frame.pack(fill='both', expand=expand, padx=15, pady=(10, 10))
        
        output_text = tk.Text(output_frame, wrap=tk.WORD, font=('Consolas', 9),
                               bg=self.colors['grid'], fg=self.colors['text'],
                               relief='flat', padx=5, pady=5)
        scrollbar = tk.Scrollbar(output_frame, orient='vertical', command=output_text.yview)
        output_text.configure(yscrollcommand=scrollbar.set)
        output_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        output_text.tag_config('info', foreground=self.colors['secondary'])
        output_text.tag_config('success', foreground=self.colors['primary'])
        output_text.tag_config('warning', foreground=self.colors['warning'])
        output_text.tag_config('error', foreground=self.colors['warning'])
        output_text.tag_config('header', foreground=self.colors['accent'])
        
        return output_text
        
    def create_status_bar(self):
        status_frame = tk.Frame(self.main_frame, bg=self.colors['panel'], height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.led = tk.Label(status_frame, text="●", font=('Arial', 12),
                           bg=self.colors['panel'], fg=self.colors['success'])
        self.led.pack(side='left', padx=10)
        
        self.status_text = tk.Label(status_frame, text="SYSTEM READY",
                                    bg=self.colors['panel'], fg=self.colors['text_dim'],
                                    font=('Courier', 9))
        self.status_text.pack(side='left', padx=5)
        
    # ============ MONITORING FUNCTIONS ============
    def start_system_monitors(self):
        self.update_cpu_gauge()
        self.update_memory_gauge()
        self.update_disk_gauge()
        self.update_quick_stats()
        
    def update_cpu_gauge(self):
        try:
            cpu = psutil.cpu_percent()
            angle = 180 - (cpu / 100) * 180
            rad = math.radians(angle)
            x = 140 + 90 * math.cos(rad)
            y = 80 - 90 * math.sin(rad)
            self.cpu_frame.canvas.coords(self.cpu_frame.needle, 140, 80, x, y)
            self.cpu_frame.display.config(text=f"{cpu:.1f}%")
            color = self.colors['warning'] if cpu > 80 else (self.colors['accent'] if cpu > 60 else self.colors['primary'])
            self.cpu_frame.display.config(fg=color)
        except:
            pass
        self.root.after(1000, self.update_cpu_gauge)
        
    def update_memory_gauge(self):
        try:
            mem = psutil.virtual_memory()
            height = 98 * (mem.percent / 100)
            y1 = 123 - height
            self.mem_frame.canvas.coords(self.mem_frame.fill_bar, 92, y1, 188, 123)
            self.mem_frame.display.config(text=f"{mem.percent:.1f}%")
        except:
            pass
        self.root.after(1000, self.update_memory_gauge)
        
    def update_disk_gauge(self):
        try:
            disk = psutil.disk_usage('/')
            angle = 180 - (disk.percent / 100) * 180
            rad = math.radians(angle)
            x = 140 + 90 * math.cos(rad)
            y = 90 - 90 * math.sin(rad)
            self.disk_frame.canvas.coords(self.disk_frame.needle, 140, 90, x, y)
            self.disk_frame.display.config(text=f"{disk.percent:.1f}%")
        except:
            pass
        self.root.after(1000, self.update_disk_gauge)
        
    def update_quick_stats(self):
        try:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            self.quick_cpu.config(text=f"CPU: {cpu:.0f}%")
            self.quick_mem.config(text=f"RAM: {mem:.0f}%")
            self.quick_disk.config(text=f"DISK: {disk:.0f}%")
        except:
            pass
        self.root.after(2000, self.update_quick_stats)
        
    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
        
    def stop_process(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
        self.stop_btn.config(state='disabled')
        self.led.config(fg=self.colors['success'])
        self.status_text.config(text="SYSTEM READY")
        self.current_process = None
        
    def run_powershell_feature(self, feature_num, output_widget, clear_first=False, 
                                extra_args=None, is_text_widget=False):
        def execute():
            if clear_first and output_widget:
                output_widget.delete(1.0, tk.END)
            
            cmd = ['pwsh', '-File', self.ps_script, '-Feature', str(feature_num)]
            if extra_args:
                for key, value in extra_args.items():
                    if value:
                        cmd.extend([f'-{key}', str(value)])
            
            if not is_text_widget and output_widget:
                output_widget.insert(tk.END, f"{'='*60}\n", 'header')
                output_widget.insert(tk.END, f"FEATURE {feature_num}\n", 'header')
                output_widget.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')}\n", 'header')
                output_widget.insert(tk.END, f"{'='*60}\n\n", 'header')
            
            try:
                self.current_process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
                )
                for line in self.current_process.stdout:
                    if output_widget:
                        output_widget.insert(tk.END, line, 'info')
                        output_widget.see(tk.END)
                self.current_process.wait()
                stderr = self.current_process.stderr.read()
                if stderr and output_widget:
                    output_widget.insert(tk.END, f"\n{stderr}\n", 'error')
                if not is_text_widget and output_widget:
                    output_widget.insert(tk.END, f"\n{'='*60}\n✅ COMPLETED\n{'='*60}\n", 'success')
            except Exception as e:
                if output_widget:
                    output_widget.insert(tk.END, f"\n❌ ERROR: {e}\n", 'error')
            finally:
                self.current_process = None
                
        threading.Thread(target=execute, daemon=True).start()

def main():
    root = tk.Tk()
    app = CompleteOSUtility(root)
    
    root.update_idletasks()
    w, h = 1400, 900
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f'{w}x{h}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
