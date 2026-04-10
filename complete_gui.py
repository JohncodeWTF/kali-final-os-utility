#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kali SmartOps Manager - Enhanced GUI
ONLY THE PYTHON GUI IS CHANGED - PowerShell backend (complete_os.ps1) is untouched.
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


# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
PALETTE = {
    'bg':           '#080c10',
    'bg2':          '#0d1117',
    'panel':        '#0f1923',
    'border':       '#1a2d3d',
    'border_hi':    '#00ffe1',
    'primary':      '#00ffe1',      # Cyan-mint
    'primary_dim':  '#00a89c',
    'secondary':    '#4fc3f7',      # Sky blue
    'accent':       '#ff4081',      # Hot pink
    'accent2':      '#ffd740',      # Amber
    'success':      '#69ff82',
    'warning':      '#ff6b35',
    'danger':       '#ff1744',
    'text':         '#cdd9e5',
    'text_dim':     '#4d6a7a',
    'text_hi':      '#ffffff',
    'folder':       '#ffd740',
    'file':         '#4fc3f7',
    'exec':         '#69ff82',
    'card':         '#111c26',
    'card2':        '#13202e',
    'grid':         '#0d1822',
    'scrollbar':    '#1e3045',
}

FONTS = {
    'mono_large':   ('Courier New', 14, 'bold'),
    'mono_med':     ('Courier New', 11, 'bold'),
    'mono_small':   ('Courier New', 9),
    'mono_tiny':    ('Courier New', 8),
    'mono_xsmall':  ('Courier New', 7),
    'header':       ('Courier New', 18, 'bold'),
    'gauge':        ('Courier New', 16, 'bold'),
    'gauge_sm':     ('Courier New', 11, 'bold'),
    'label':        ('Courier New', 9, 'bold'),
}


def apply_ttk_style():
    style = ttk.Style()
    style.theme_use('clam')

    # Notebook
    style.configure('Cyber.TNotebook',
                    background=PALETTE['bg'],
                    borderwidth=0,
                    tabmargins=[2, 5, 2, 0])
    style.configure('Cyber.TNotebook.Tab',
                    background=PALETTE['panel'],
                    foreground=PALETTE['text_dim'],
                    padding=[14, 8],
                    font=FONTS['mono_tiny'],
                    borderwidth=0,
                    focuscolor='none')
    style.map('Cyber.TNotebook.Tab',
              background=[('selected', PALETTE['card']),
                          ('active', PALETTE['border'])],
              foreground=[('selected', PALETTE['primary']),
                          ('active', PALETTE['text'])],
              relief=[('selected', 'flat')])

    # Treeview
    style.configure('Cyber.Treeview',
                    background=PALETTE['grid'],
                    foreground=PALETTE['text'],
                    fieldbackground=PALETTE['grid'],
                    borderwidth=0,
                    rowheight=22,
                    font=FONTS['mono_tiny'])
    style.configure('Cyber.Treeview.Heading',
                    background=PALETTE['panel'],
                    foreground=PALETTE['primary'],
                    font=FONTS['label'],
                    relief='flat',
                    borderwidth=0)
    style.map('Cyber.Treeview',
              background=[('selected', PALETTE['border'])],
              foreground=[('selected', PALETTE['primary'])])

    # Scrollbar
    style.configure('Cyber.Vertical.TScrollbar',
                    background=PALETTE['scrollbar'],
                    troughcolor=PALETTE['grid'],
                    borderwidth=0,
                    arrowcolor=PALETTE['primary'],
                    arrowsize=12)
    style.configure('Cyber.Horizontal.TScrollbar',
                    background=PALETTE['scrollbar'],
                    troughcolor=PALETTE['grid'],
                    borderwidth=0,
                    arrowcolor=PALETTE['primary'],
                    arrowsize=12)

    # Combobox
    style.configure('Cyber.TCombobox',
                    fieldbackground=PALETTE['grid'],
                    background=PALETTE['panel'],
                    foreground=PALETTE['text'],
                    bordercolor=PALETTE['border'],
                    lightcolor=PALETTE['border'],
                    darkcolor=PALETTE['border'],
                    selectbackground=PALETTE['border'],
                    selectforeground=PALETTE['primary'],
                    insertcolor=PALETTE['primary'],
                    font=FONTS['mono_tiny'])


# ─────────────────────────────────────────────────────────────────────────────
#  REUSABLE WIDGET HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def cyber_btn(parent, text, command, color=None, text_color='#000000',
              font=None, padx=16, pady=6, **kwargs):
    color = color or PALETTE['primary']
    font  = font  or FONTS['mono_small']
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=text_color,
                    font=font, relief='flat',
                    activebackground=PALETTE['primary_dim'],
                    activeforeground='#000000',
                    cursor='hand2',
                    padx=padx, pady=pady, bd=0,
                    highlightthickness=0, **kwargs)
    return btn


def corner_frame(parent, color=None, bg=None, thickness=1):
    """A Frame with a thin coloured top+left border."""
    color = color or PALETTE['border']
    bg    = bg    or PALETTE['card']
    f = tk.Frame(parent, bg=color)
    inner = tk.Frame(f, bg=bg)
    inner.pack(fill='both', expand=True,
               padx=(thickness, 0), pady=(thickness, 0))
    return f, inner


def section_label(parent, text, color=None):
    color = color or PALETTE['primary']
    row = tk.Frame(parent, bg=parent.cget('bg'))
    row.pack(fill='x', padx=0, pady=(8, 2))
    tk.Label(row, text='▸ ', font=FONTS['label'],
             bg=parent.cget('bg'), fg=color).pack(side='left')
    tk.Label(row, text=text, font=FONTS['label'],
             bg=parent.cget('bg'), fg=color).pack(side='left')
    tk.Frame(row, bg=PALETTE['border'], height=1).pack(
        side='left', fill='x', expand=True, padx=8, pady=5)


def make_output_text(parent, height=None, font=None):
    font = font or FONTS['mono_tiny']
    txt = tk.Text(parent, wrap=tk.WORD,
                  font=font,
                  bg=PALETTE['grid'],
                  fg=PALETTE['text'],
                  insertbackground=PALETTE['primary'],
                  relief='flat', bd=0,
                  selectbackground=PALETTE['border'],
                  selectforeground=PALETTE['primary'],
                  padx=10, pady=8,
                  **({"height": height} if height else {}))
    for tag, fg in [('info',    PALETTE['secondary']),
                    ('success', PALETTE['success']),
                    ('warning', PALETTE['accent2']),
                    ('error',   PALETTE['danger']),
                    ('header',  PALETTE['primary']),
                    ('dim',     PALETTE['text_dim'])]:
        txt.tag_config(tag, foreground=fg)
    return txt


def scrolled_output(parent, height=None, font=None):
    frame = tk.Frame(parent, bg=PALETTE['grid'],
                     highlightbackground=PALETTE['border'],
                     highlightthickness=1)
    txt = make_output_text(frame, height=height, font=font)
    sb = ttk.Scrollbar(frame, orient='vertical',
                       command=txt.yview,
                       style='Cyber.Vertical.TScrollbar')
    txt.configure(yscrollcommand=sb.set)
    txt.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')
    return frame, txt


# ─────────────────────────────────────────────────────────────────────────────
#  ANIMATED GAUGE CANVAS
# ─────────────────────────────────────────────────────────────────────────────

class ArcGauge(tk.Canvas):
    """Semi-circular arc gauge with glow needle and animated tick marks."""

    def __init__(self, parent, title, color, **kwargs):
        kwargs.setdefault('width', 260)
        kwargs.setdefault('height', 155)
        super().__init__(parent, bg=PALETTE['card'],
                         highlightthickness=0, **kwargs)
        self.color = color
        self.title = title
        self._value = 0
        self._draw_static()

    def _draw_static(self):
        w, h = int(self['width']), int(self['height'])
        cx, cy, r = w // 2, 105, 80

        # Background arc track
        self.create_arc(cx - r, cy - r, cx + r, cy + r,
                        start=0, extent=180,
                        outline=PALETTE['border'], width=10,
                        style='arc')

        # Coloured arc overlay (full 0-100) - dim version of color
        dim_color = PALETTE['border']
        self.create_arc(cx - r, cy - r, cx + r, cy + r,
                        start=0, extent=180,
                        outline=dim_color, width=10,
                        style='arc')

        # Tick marks
        for i in range(0, 181, 18):
            rad = math.radians(i)
            lx1 = cx + (r - 14) * math.cos(rad)
            ly1 = cy - (r - 14) * math.sin(rad)
            lx2 = cx + (r - 5)  * math.cos(rad)
            ly2 = cy - (r - 5)  * math.sin(rad)
            self.create_line(lx1, ly1, lx2, ly2,
                             fill=PALETTE['text_dim'], width=1)

        # Percent labels
        for pct, angle in [(0, 180), (25, 135), (50, 90), (75, 45), (100, 0)]:
            rad = math.radians(angle)
            tx = cx + (r + 18) * math.cos(rad)
            ty = cy - (r + 18) * math.sin(rad)
            self.create_text(tx, ty, text=f"{pct}",
                             fill=PALETTE['text_dim'],
                             font=FONTS['mono_xsmall'])

        # Centre hub
        self.create_oval(cx - 7, cy - 7, cx + 7, cy + 7,
                         fill=self.color, outline='')

        # Needle placeholder
        self._needle = self.create_line(cx, cy, cx, cy - r + 14,
                                        width=3, fill=self.color,
                                        capstyle='round')

        # Value text
        self._val_text = self.create_text(cx, cy + 22,
                                          text="0%",
                                          font=FONTS['gauge_sm'],
                                          fill=self.color)
        # Title
        self.create_text(cx, cy + 38, text=self.title,
                         font=FONTS['mono_xsmall'],
                         fill=PALETTE['text_dim'])

    def set_value(self, value):
        self._value = max(0, min(100, value))
        self._redraw_needle()

    def _redraw_needle(self):
        w, h = int(self['width']), int(self['height'])
        cx, cy, r = w // 2, 105, 80
        angle = 180 - self._value * 1.8      # 0% = 180°, 100% = 0°
        rad = math.radians(angle)
        nx = cx + (r - 14) * math.cos(rad)
        ny = cy - (r - 14) * math.sin(rad)
        self.coords(self._needle, cx, cy, nx, ny)
        col = (PALETTE['danger'] if self._value > 85 else
               PALETTE['warning'] if self._value > 65 else
               self.color)
        self.itemconfig(self._needle, fill=col)
        self.itemconfig(self._val_text,
                        text=f"{self._value:.1f}%",
                        fill=col)


class BarGauge(tk.Canvas):
    """Vertical fill-bar gauge."""

    def __init__(self, parent, title, color, **kwargs):
        kwargs.setdefault('width', 260)
        kwargs.setdefault('height', 155)
        super().__init__(parent, bg=PALETTE['card'],
                         highlightthickness=0, **kwargs)
        self.color = color
        self.title = title
        self._value = 0
        self._draw_static()

    def _draw_static(self):
        w, h = int(self['width']), int(self['height'])
        bx1, bx2 = w // 2 - 30, w // 2 + 30
        by1, by2 = 15, 115

        # Background bar
        self.create_rectangle(bx1, by1, bx2, by2,
                              fill=PALETTE['grid'],
                              outline=PALETTE['border'], width=1)

        # Fill bar (dynamic)
        self._fill = self.create_rectangle(bx1 + 2, by2 - 2,
                                           bx2 - 2, by2 - 2,
                                           fill=self.color, outline='')

        # Gridlines
        for i, pct in enumerate([0, 25, 50, 75, 100]):
            y = by2 - (by2 - by1) * pct // 100
            self.create_line(bx1 - 5, y, bx1, y,
                             fill=PALETTE['text_dim'], width=1)
            self.create_text(bx1 - 10, y, text=f"{pct}%",
                             fill=PALETTE['text_dim'],
                             font=FONTS['mono_xsmall'],
                             anchor='e')

        # Value text
        self._val_text = self.create_text(w // 2, by2 + 16,
                                          text="0%",
                                          font=FONTS['gauge_sm'],
                                          fill=self.color)
        self.create_text(w // 2, by2 + 30, text=self.title,
                         font=FONTS['mono_xsmall'],
                         fill=PALETTE['text_dim'])

        # Store geometry
        self._bx1, self._bx2 = bx1, bx2
        self._by1, self._by2 = by1, by2

    def set_value(self, value):
        self._value = max(0, min(100, value))
        fill_h = (self._by2 - self._by1) * self._value / 100
        y1 = self._by2 - fill_h
        self.coords(self._fill,
                    self._bx1 + 2, y1,
                    self._bx2 - 2, self._by2 - 2)
        col = (PALETTE['danger'] if self._value > 90 else
               PALETTE['warning'] if self._value > 75 else
               self.color)
        self.itemconfig(self._fill, fill=col)
        self.itemconfig(self._val_text,
                        text=f"{self._value:.1f}%",
                        fill=col)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class CompleteOSUtility:

    def __init__(self, root):
        self.root = root
        self.root.title("KALI SMARTOPS MANAGER PRO")
        self.root.geometry("1440x900")
        self.root.configure(bg=PALETTE['bg'])
        self.root.minsize(1200, 720)

        apply_ttk_style()

        # ── State
        self.ps_script       = os.path.expanduser("~/complete_os.ps1")
        self.current_dir     = os.path.expanduser("~")
        self.clip_src        = None
        self.clip_action     = None
        self.current_proc    = None
        self.search_content  = tk.BooleanVar(value=False)
        self.usb_devices     = []
        self.storage_devices = []
        self.usb_drive       = tk.StringVar()
        self.usb_drive_info  = tk.StringVar()
        self.iso_path        = tk.StringVar()
        self.format_device   = tk.StringVar()
        self.format_dev_info = tk.StringVar()
        self.fs_type         = tk.StringVar(value='ext4')
        self.volume_label    = tk.StringVar()
        self._start_time     = datetime.now()   # runtime clock

        if not os.path.exists(self.ps_script):
            messagebox.showerror("Error",
                f"PowerShell backend not found!\n\n{self.ps_script}\n\n"
                "Place complete_os.ps1 in your home directory.")
            self.root.destroy()
            return

        self._build_ui()
        self._start_monitors()

    # ══════════════════════════════════════════════════════════════════════════
    #  UI BUILD
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        # Header bar
        self._build_header()

        # Body: left telemetry | right notebook
        body = tk.Frame(self.root, bg=PALETTE['bg'])
        body.pack(fill='both', expand=True, padx=12, pady=(0, 6))

        self._build_telemetry_panel(body)
        self._build_notebook(body)

        # Status bar
        self._build_statusbar()

    # ─── HEADER ──────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=PALETTE['panel'], height=58)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        # Left accent stripe
        tk.Frame(hdr, bg=PALETTE['primary'], width=4).pack(side='left', fill='y')

        # Logo
        logo_frame = tk.Frame(hdr, bg=PALETTE['panel'])
        logo_frame.pack(side='left', padx=18, pady=0)

        tk.Label(logo_frame, text="⚡ KALI SMARTOPS",
                 font=('Courier New', 17, 'bold'),
                 bg=PALETTE['panel'], fg=PALETTE['primary']).pack(anchor='w')
        tk.Label(logo_frame, text="Complete OS Utility Suite  ▸  Kali Linux",
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['panel'], fg=PALETTE['text_dim']).pack(anchor='w')

        # Separator
        tk.Frame(hdr, bg=PALETTE['border'], width=1).pack(
            side='left', fill='y', padx=18, pady=10)

        # Quick stats pills
        self._q_cpu   = self._header_pill(hdr, "CPU",  "0%")
        self._q_mem   = self._header_pill(hdr, "RAM",  "0%")
        self._q_disk  = self._header_pill(hdr, "DISK", "0%")

        # Right-side controls
        right = tk.Frame(hdr, bg=PALETTE['panel'])
        right.pack(side='right', padx=14)

        self._time_lbl = tk.Label(right, text="",
                                  font=('Courier New', 13, 'bold'),
                                  bg=PALETTE['panel'], fg=PALETTE['accent2'])
        self._time_lbl.pack(side='right', padx=(14, 0))
        self._tick_time()

        cyber_btn(right, "⏹  STOP",
                  self._stop_process,
                  color=PALETTE['danger'],
                  text_color='#ffffff',
                  font=FONTS['label']).pack(side='right', padx=4)

    def _header_pill(self, parent, label, initial):
        pill = tk.Frame(parent, bg=PALETTE['card'],
                        highlightbackground=PALETTE['border'],
                        highlightthickness=1)
        pill.pack(side='left', padx=5, pady=10)
        tk.Label(pill, text=label, font=FONTS['mono_xsmall'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(padx=10, pady=(4, 0))
        val_lbl = tk.Label(pill, text=initial,
                           font=('Courier New', 11, 'bold'),
                           bg=PALETTE['card'], fg=PALETTE['primary'])
        val_lbl.pack(padx=10, pady=(0, 4))
        return val_lbl

    # ─── LEFT TELEMETRY PANEL ────────────────────────────────────────────────

    def _build_telemetry_panel(self, parent):
        panel = tk.Frame(parent, bg=PALETTE['panel'],
                         highlightbackground=PALETTE['border'],
                         highlightthickness=1,
                         width=290)
        panel.pack(side='left', fill='y', pady=(10, 0), padx=(0, 10))
        panel.pack_propagate(False)

        tk.Label(panel,
                 text="SYSTEM TELEMETRY",
                 font=FONTS['label'],
                 bg=PALETTE['panel'],
                 fg=PALETTE['primary']).pack(pady=(12, 4))
        tk.Frame(panel, bg=PALETTE['border'], height=1).pack(fill='x', padx=14)

        # ── CPU Arc Gauge
        cpu_card = self._tele_card(panel)
        self._gauge_cpu = ArcGauge(cpu_card, "CPU USAGE",
                                   PALETTE['primary'],
                                   width=260, height=160)
        self._gauge_cpu.pack(pady=(4, 4))

        # ── Memory Bar Gauge
        mem_card = self._tele_card(panel)
        self._gauge_mem = BarGauge(mem_card, "MEMORY USAGE",
                                   PALETTE['secondary'],
                                   width=260, height=160)
        self._gauge_mem.pack(pady=(4, 4))

        # ── Disk Arc Gauge (reuse ArcGauge in warning colour)
        dsk_card = self._tele_card(panel)
        self._gauge_dsk = ArcGauge(dsk_card, "DISK USAGE",
                                   PALETTE['warning'],
                                   width=260, height=160)
        self._gauge_dsk.pack(pady=(4, 4))

        # ── System info box
        info_card = self._tele_card(panel, expand=True)
        tk.Label(info_card, text="SYSTEM SNAPSHOT",
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['card2'],
                 fg=PALETTE['accent']).pack(pady=(6, 0))

        _, self._sysinfo_txt = scrolled_output(info_card,
                                               font=FONTS['mono_xsmall'])
        self._sysinfo_txt.master.pack(fill='both', expand=True,
                                      padx=8, pady=8)

        self._run_ps(1, self._sysinfo_txt, is_text=True)

    def _tele_card(self, parent, expand=False):
        card = tk.Frame(parent, bg=PALETTE['card2'],
                        highlightbackground=PALETTE['border'],
                        highlightthickness=1)
        card.pack(fill='x' if not expand else 'both',
                  expand=expand, padx=12, pady=4)
        return card

    # ─── RIGHT NOTEBOOK ──────────────────────────────────────────────────────

    def _build_notebook(self, parent):
        self.nb = ttk.Notebook(parent, style='Cyber.TNotebook')
        self.nb.pack(side='right', fill='both', expand=True, pady=(10, 0))

        self._tab_file_manager()
        self._tab_simple("🔍 PROCESSES",     2, "Process Monitor",    "Top processes by CPU & memory")
        self._tab_network()
        self._tab_simple("🔒 SECURITY",     10, "Security Check",     "Suspicious process detection")
        self._tab_simple("🔄 SERVICES",      7, "Service Manager",    "Running & failed services")
        self._tab_simple("📦 PACKAGES",     11, "Package Updates",    "Available apt updates")
        self._tab_simple("💾 DISK",          8, "Disk Analysis",      "Largest dirs & file counts")
        self._tab_simple("🧹 CLEANUP",       9, "Cleanup Tools",      "Cache / logs / tmp sizes")
        self._tab_simple("💻 HARDWARE",     12, "Hardware Info",      "CPU, GPU, NIC details")
        self._tab_simple("📈 REALTIME",      3, "Real-time Monitor",  "Live CPU / MEM / DISK")
        self._tab_bootable()
        self._tab_storage_format()

    # ─── FILE MANAGER TAB ────────────────────────────────────────────────────

    def _tab_file_manager(self):
        tab = tk.Frame(self.nb, bg=PALETTE['bg2'])
        self.nb.add(tab, text="📁  FILE MANAGER")

        # ── Toolbar
        tb = tk.Frame(tab, bg=PALETTE['panel'],
                      highlightbackground=PALETTE['border'],
                      highlightthickness=1,
                      height=42)
        tb.pack(fill='x', padx=6, pady=(6, 0))
        tb.pack_propagate(False)

        nav_grp = tk.Frame(tb, bg=PALETTE['panel'])
        nav_grp.pack(side='left', padx=6)
        for txt, cmd in [("◀", self._fm_back), ("▲", self._fm_up),
                         ("🏠", self._fm_home), ("↺", self._fm_refresh)]:
            cyber_btn(nav_grp, txt, cmd,
                      color=PALETTE['border'],
                      text_color=PALETTE['primary'],
                      font=FONTS['mono_small'],
                      padx=8, pady=4).pack(side='left', padx=2)

        tk.Frame(tb, bg=PALETTE['border'], width=1).pack(
            side='left', fill='y', pady=8, padx=4)

        ops_grp = tk.Frame(tb, bg=PALETTE['panel'])
        ops_grp.pack(side='left', padx=6)
        for txt, cmd, col in [
            ("COPY",   self._fm_copy,   PALETTE['secondary']),
            ("CUT",    self._fm_cut,    PALETTE['accent2']),
            ("PASTE",  self._fm_paste,  PALETTE['success']),
            ("DELETE", self._fm_delete, PALETTE['danger']),
            ("RENAME", self._fm_rename, PALETTE['accent']),
            ("NEW DIR",self._fm_newdir, PALETTE['primary']),
        ]:
            cyber_btn(ops_grp, txt, cmd,
                      color=col, text_color='#000000',
                      font=FONTS['mono_xsmall'],
                      padx=8, pady=4).pack(side='left', padx=2)

        tk.Frame(tb, bg=PALETTE['border'], width=1).pack(
            side='left', fill='y', pady=8, padx=4)

        srch_grp = tk.Frame(tb, bg=PALETTE['panel'])
        srch_grp.pack(side='left', padx=4)

        self._srch_var = tk.StringVar()
        srch_e = tk.Entry(srch_grp, textvariable=self._srch_var,
                          bg=PALETTE['grid'], fg=PALETTE['text'],
                          insertbackground=PALETTE['primary'],
                          font=FONTS['mono_tiny'],
                          relief='flat', bd=0, width=22,
                          highlightbackground=PALETTE['border'],
                          highlightthickness=1)
        srch_e.pack(side='left', padx=4, ipady=4)
        srch_e.bind('<Return>', self._fm_search)

        cyber_btn(srch_grp, "⌕ SEARCH", self._fm_search,
                  color=PALETTE['secondary'], text_color='#000000',
                  font=FONTS['mono_xsmall'],
                  padx=8, pady=4).pack(side='left', padx=2)

        tk.Checkbutton(srch_grp, text="in content",
                       variable=self.search_content,
                       bg=PALETTE['panel'], fg=PALETTE['text_dim'],
                       selectcolor=PALETTE['grid'],
                       activebackground=PALETTE['panel'],
                       font=FONTS['mono_xsmall'],
                       highlightthickness=0).pack(side='left', padx=4)

        # Path breadcrumb
        path_bar = tk.Frame(tab, bg=PALETTE['card'],
                            highlightbackground=PALETTE['border'],
                            highlightthickness=1)
        path_bar.pack(fill='x', padx=6, pady=(2, 0))
        tk.Label(path_bar, text="PATH ▸ ", font=FONTS['mono_xsmall'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(side='left', padx=6)
        self._path_lbl = tk.Label(path_bar, text=self.current_dir,
                                  font=FONTS['mono_tiny'],
                                  bg=PALETTE['card'],
                                  fg=PALETTE['primary'])
        self._path_lbl.pack(side='left')

        # ── Main pane: tree + preview
        pane = tk.PanedWindow(tab, orient='vertical',
                              bg=PALETTE['bg2'], sashwidth=4,
                              sashrelief='flat', sashpad=2)
        pane.pack(fill='both', expand=True, padx=6, pady=4)

        # File tree
        tree_frame = tk.Frame(pane, bg=PALETTE['grid'])
        self.file_tree = ttk.Treeview(tree_frame,
                                      columns=('SIZE', 'MODIFIED', 'PERMS'),
                                      show='tree headings',
                                      selectmode='extended',
                                      style='Cyber.Treeview')
        for col, txt, w in [('#0', 'NAME', 380),
                             ('SIZE', 'SIZE', 90),
                             ('MODIFIED', 'MODIFIED', 145),
                             ('PERMS', 'PERMS', 70)]:
            self.file_tree.heading(col, text=txt)
            self.file_tree.column(col, width=w, minwidth=50)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical',
                            command=self.file_tree.yview,
                            style='Cyber.Vertical.TScrollbar')
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal',
                            command=self.file_tree.xview,
                            style='Cyber.Horizontal.TScrollbar')
        self.file_tree.configure(yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set)
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.file_tree.bind('<Double-1>', self._fm_double_click)
        self.file_tree.bind('<<TreeviewSelect>>', self._fm_on_select)

        # Preview
        prev_frame = tk.Frame(pane, bg=PALETTE['panel'],
                              highlightbackground=PALETTE['border'],
                              highlightthickness=1)
        tk.Label(prev_frame, text="▸ PREVIEW",
                 font=FONTS['label'],
                 bg=PALETTE['panel'],
                 fg=PALETTE['accent']).pack(anchor='w', padx=10, pady=4)

        _, self._preview_txt = scrolled_output(prev_frame, height=6,
                                               font=FONTS['mono_tiny'])
        self._preview_txt.master.pack(fill='both', expand=True,
                                      padx=8, pady=(0, 8))

        pane.add(tree_frame, height=480)
        pane.add(prev_frame, height=140)

        self._fm_refresh()

    # ── File Manager helpers ──────────────────────────────────────────────────

    def _fm_refresh(self, *_):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        try:
            items = sorted(os.listdir(self.current_dir))
            for name in items:
                fp = os.path.join(self.current_dir, name)
                try:
                    st = os.stat(fp)
                    size = self._fmt_size(st.st_size)
                    mod  = datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')
                    perm = oct(st.st_mode)[-3:]
                    if os.path.isdir(fp):
                        icon, tag = "📁 ", 'dir'
                        size = "—"
                    elif os.access(fp, os.X_OK):
                        icon, tag = "⚡ ", 'exec'
                    else:
                        icon, tag = "📄 ", 'file'
                    self.file_tree.insert('', 'end',
                                         text=f"{icon}{name}",
                                         values=(size, mod, perm),
                                         tags=(tag,))
                except Exception:
                    pass
            self.file_tree.tag_configure('dir',  foreground=PALETTE['folder'])
            self.file_tree.tag_configure('exec', foreground=PALETTE['exec'])
            self.file_tree.tag_configure('file', foreground=PALETTE['file'])
            self._path_lbl.config(text=self.current_dir)
        except Exception as e:
            self._status(f"Error: {e}")

    def _fmt_size(self, sz):
        for u in ['B', 'KB', 'MB', 'GB', 'TB']:
            if sz < 1024: return f"{sz:.1f} {u}"
            sz /= 1024
        return f"{sz:.1f} TB"

    def _fm_double_click(self, _):
        sel = self.file_tree.selection()
        if not sel: return
        name = self.file_tree.item(sel[0])['text'].lstrip("📁 ⚡📄").strip()
        fp = os.path.join(self.current_dir, name)
        if os.path.isdir(fp):
            self.current_dir = fp
            self._fm_refresh()
        else:
            self._fm_preview(fp)

    def _fm_on_select(self, _):
        sel = self.file_tree.selection()
        if not sel: return
        name = self.file_tree.item(sel[0])['text'].lstrip("📁 ⚡📄").strip()
        fp = os.path.join(self.current_dir, name)
        if not os.path.isdir(fp):
            self._fm_preview(fp)

    def _fm_preview(self, path):
        self._preview_txt.delete(1.0, tk.END)
        if path.endswith(('.txt','.py','.sh','.md','.conf','.json','.xml','.log','.yaml','.toml')):
            try:
                with open(path, 'r', errors='replace') as f:
                    content = f.read(8000)
                self._preview_txt.insert(1.0, content)
                if len(content) >= 8000:
                    self._preview_txt.insert(tk.END, "\n\n…  (truncated)")
            except Exception as e:
                self._preview_txt.insert(1.0, f"Cannot read file: {e}")
        else:
            try:
                st = os.stat(path)
                self._preview_txt.insert(1.0,
                    f"File    : {os.path.basename(path)}\n"
                    f"Size    : {self._fmt_size(st.st_size)}\n"
                    f"Modified: {datetime.fromtimestamp(st.st_mtime):%Y-%m-%d %H:%M:%S}\n"
                    f"Perms   : {oct(st.st_mode)[-3:]}\n"
                    f"Type    : {path.rsplit('.',1)[-1].upper() if '.' in path else 'binary'}")
            except Exception:
                self._preview_txt.insert(1.0, "Cannot preview this file type.")

    def _fm_back(self):
        p = os.path.dirname(self.current_dir)
        if p != self.current_dir:
            self.current_dir = p; self._fm_refresh()

    def _fm_up(self):   self._fm_back()
    def _fm_home(self): self.current_dir = os.path.expanduser("~"); self._fm_refresh()

    def _fm_copy(self):
        sel = self.file_tree.selection()
        if sel:
            name = self.file_tree.item(sel[0])['text'].lstrip("📁 ⚡📄").strip()
            self.clip_src = os.path.join(self.current_dir, name)
            self.clip_action = 'copy'
            self._status(f"Copied: {name}")

    def _fm_cut(self):
        sel = self.file_tree.selection()
        if sel:
            name = self.file_tree.item(sel[0])['text'].lstrip("📁 ⚡📄").strip()
            self.clip_src = os.path.join(self.current_dir, name)
            self.clip_action = 'cut'
            self._status(f"Cut: {name}")

    def _fm_paste(self):
        if not self.clip_src: return
        dest = os.path.join(self.current_dir, os.path.basename(self.clip_src))
        feat = 14 if self.clip_action == 'copy' else 15
        self._run_ps(feat, None, extra={'Source': self.clip_src, 'Destination': dest})
        self._fm_refresh()
        self.clip_src = None
        self._status("Paste complete")

    def _fm_delete(self):
        sel = self.file_tree.selection()
        if sel and messagebox.askyesno("Confirm Delete", "Delete selected item(s)?"):
            for item in sel:
                name = self.file_tree.item(item)['text'].lstrip("📁 ⚡📄").strip()
                self._run_ps(16, None, extra={'Path': os.path.join(self.current_dir, name)})
            self._fm_refresh()

    def _fm_rename(self):
        sel = self.file_tree.selection()
        if sel:
            old = self.file_tree.item(sel[0])['text'].lstrip("📁 ⚡📄").strip()
            new = simpledialog.askstring("Rename", "New name:", initialvalue=old)
            if new:
                self._run_ps(17, None, extra={
                    'Path': os.path.join(self.current_dir, old),
                    'Destination': new})
                self._fm_refresh()

    def _fm_newdir(self):
        name = simpledialog.askstring("New Folder", "Folder name:")
        if name:
            self._run_ps(18, None, extra={'Path': os.path.join(self.current_dir, name)})
            self._fm_refresh()

    def _fm_search(self, *_):
        pattern = self._srch_var.get().strip()
        if not pattern: return
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        in_content = self.search_content.get()
        self._status(f"Searching for '{pattern}'…")

        def _search():
            found = 0
            for root, dirs, files in os.walk(self.current_dir):
                for name in dirs + files:
                    fp = os.path.join(root, name)
                    match = pattern.lower() in name.lower()
                    if not match and in_content and os.path.isfile(fp):
                        if name.endswith(('.txt','.py','.sh','.md','.conf','.log')):
                            try:
                                with open(fp,'r',errors='ignore') as f:
                                    match = pattern.lower() in f.read(60000).lower()
                                    if match: name += " (content)"
                            except Exception:
                                pass
                    if match:
                        try:
                            st = os.stat(fp)
                            rel = os.path.relpath(fp, self.current_dir)
                            self.file_tree.insert(
                                '', 'end', text=f"📄 {rel}",
                                values=(self._fmt_size(st.st_size),
                                        datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M'),
                                        oct(st.st_mode)[-3:]))
                            found += 1
                        except Exception:
                            pass
                    if found >= 200: break
            self._status(f"Search done — {found} match(es)")

        threading.Thread(target=_search, daemon=True).start()

    # ─── SIMPLE FEATURE TAB ──────────────────────────────────────────────────

    def _tab_simple(self, label, feat_num, title, desc):
        tab = tk.Frame(self.nb, bg=PALETTE['bg2'])
        self.nb.add(tab, text=f"  {label}  ")

        # Title strip
        strip = tk.Frame(tab, bg=PALETTE['panel'],
                         highlightbackground=PALETTE['border'],
                         highlightthickness=1,
                         height=46)
        strip.pack(fill='x', padx=6, pady=(6, 0))
        strip.pack_propagate(False)
        tk.Frame(strip, bg=PALETTE['primary'], width=3).pack(side='left', fill='y')
        tk.Label(strip, text=f"  {title}",
                 font=FONTS['mono_med'],
                 bg=PALETTE['panel'],
                 fg=PALETTE['primary']).pack(side='left')
        tk.Label(strip, text=f"  —  {desc}",
                 font=FONTS['mono_tiny'],
                 bg=PALETTE['panel'],
                 fg=PALETTE['text_dim']).pack(side='left')

        # Output area
        out_wrap = tk.Frame(tab, bg=PALETTE['bg2'])
        out_wrap.pack(fill='both', expand=True, padx=6, pady=4)
        _, out = scrolled_output(out_wrap)
        out.master.pack(fill='both', expand=True)

        # Run button
        btn_bar = tk.Frame(tab, bg=PALETTE['panel'], height=46)
        btn_bar.pack(fill='x', padx=6, pady=(0, 6))
        btn_bar.pack_propagate(False)
        cyber_btn(btn_bar, f"▶  RUN  {title.upper()}",
                  lambda o=out, n=feat_num: self._run_ps(n, o, clear=True),
                  color=PALETTE['primary'],
                  text_color='#000000',
                  font=FONTS['label']).pack(side='left', padx=14, pady=8)

    # ─── NETWORK TAB ─────────────────────────────────────────────────────────

    def _tab_network(self):
        tab = tk.Frame(self.nb, bg=PALETTE['bg2'])
        self.nb.add(tab, text="  🌐 NETWORK  ")

        canvas = tk.Canvas(tab, bg=PALETTE['bg2'], highlightthickness=0)
        vsb = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview,
                            style='Cyber.Vertical.TScrollbar')
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        inner = tk.Frame(canvas, bg=PALETTE['bg2'])
        cwin = canvas.create_window((0, 0), window=inner, anchor='nw')

        def _resize(e):
            canvas.itemconfig(cwin, width=e.width)
            canvas.configure(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', _resize)

        for feat, title, desc in [
            (4, "Network Interfaces", "Active interfaces & connection list"),
            (5, "Bandwidth Stats",    "Per-interface RX / TX totals"),
            (6, "Port Scanner",       "Listening ports & services"),
        ]:
            self._net_section(inner, feat, title, desc)

    def _net_section(self, parent, feat, title, desc):
        strip = tk.Frame(parent, bg=PALETTE['panel'],
                         highlightbackground=PALETTE['border'],
                         highlightthickness=1, height=36)
        strip.pack(fill='x', padx=6, pady=(8, 0))
        strip.pack_propagate(False)
        tk.Frame(strip, bg=PALETTE['secondary'], width=3).pack(side='left', fill='y')
        tk.Label(strip, text=f"  {title}",
                 font=FONTS['label'],
                 bg=PALETTE['panel'], fg=PALETTE['secondary']).pack(side='left')
        tk.Label(strip, text=f"  —  {desc}",
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['panel'], fg=PALETTE['text_dim']).pack(side='left')

        _, out = scrolled_output(parent, height=8)
        out.master.pack(fill='x', padx=6, pady=(2, 0))

        btn_row = tk.Frame(parent, bg=PALETTE['bg2'])
        btn_row.pack(fill='x', padx=6, pady=2)
        cyber_btn(btn_row, f"▶ Run {title}",
                  lambda o=out, n=feat: self._run_ps(n, o, clear=True),
                  color=PALETTE['secondary'], text_color='#000000',
                  font=FONTS['mono_xsmall'], padx=12, pady=4).pack(side='left')

    # ─── BOOTABLE DRIVE TAB ──────────────────────────────────────────────────

    def _tab_bootable(self):
        tab = tk.Frame(self.nb, bg=PALETTE['bg2'])
        self.nb.add(tab, text="  💿 BOOTABLE  ")

        # Warning banner
        warn = tk.Frame(tab, bg=PALETTE['danger'], height=28)
        warn.pack(fill='x', padx=6, pady=(6, 0))
        warn.pack_propagate(False)
        tk.Label(warn,
                 text="⚠  WARNING: This will PERMANENTLY ERASE all data on the selected drive!  ⚠",
                 font=FONTS['label'],
                 bg=PALETTE['danger'], fg='#ffffff').pack(pady=4)

        # Card
        card = tk.Frame(tab, bg=PALETTE['card'],
                        highlightbackground=PALETTE['border'],
                        highlightthickness=1)
        card.pack(fill='both', expand=True, padx=6, pady=6)

        # Output
        section_label(card, "OPERATION LOG")
        _, self._boot_out = scrolled_output(card, height=8)
        self._boot_out.master.pack(fill='x', padx=12, pady=4)

        # Controls row
        ctrl = tk.Frame(card, bg=PALETTE['card'])
        ctrl.pack(fill='x', padx=12, pady=4)

        # Left: USB device
        left = tk.Frame(ctrl, bg=PALETTE['card'])
        left.pack(side='left', fill='both', expand=True, padx=(0,10))

        tk.Label(left, text="USB DEVICE", font=FONTS['label'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w')

        self._usb_menu = ttk.Combobox(left, textvariable=self.usb_drive,
                                      style='Cyber.TCombobox', width=38)
        self._usb_menu.pack(fill='x', pady=2)
        self._usb_menu.bind('<<ComboboxSelected>>', self._boot_dev_selected)

        tk.Label(left, textvariable=self.usb_drive_info,
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w')

        # Right: ISO
        right = tk.Frame(ctrl, bg=PALETTE['card'])
        right.pack(side='right', fill='both', expand=True)

        tk.Label(right, text="ISO FILE", font=FONTS['label'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w')

        iso_row = tk.Frame(right, bg=PALETTE['card'])
        iso_row.pack(fill='x', pady=2)
        tk.Entry(iso_row, textvariable=self.iso_path,
                 bg=PALETTE['grid'], fg=PALETTE['text'],
                 insertbackground=PALETTE['primary'],
                 font=FONTS['mono_tiny'], relief='flat', bd=0,
                 highlightbackground=PALETTE['border'],
                 highlightthickness=1).pack(side='left', fill='x',
                                            expand=True, ipady=4)
        cyber_btn(iso_row, "…", self._browse_iso,
                  color=PALETTE['secondary'], text_color='#000000',
                  font=FONTS['label'], padx=6, pady=4).pack(side='right', padx=(4,0))

        # Action buttons
        act = tk.Frame(card, bg=PALETTE['card'])
        act.pack(fill='x', padx=12, pady=8)

        cyber_btn(act, "↺  REFRESH DRIVES", self._boot_refresh,
                  color=PALETTE['panel'], text_color=PALETTE['primary'],
                  font=FONTS['label']).pack(side='left', padx=4)
        cyber_btn(act, "⌕  AUTO-DETECT ISO", self._boot_auto_iso,
                  color=PALETTE['panel'], text_color=PALETTE['accent'],
                  font=FONTS['label']).pack(side='left', padx=4)
        cyber_btn(act, "💿  CREATE BOOTABLE DRIVE",
                  self._boot_create,
                  color=PALETTE['danger'],
                  text_color='#ffffff',
                  font=FONTS['mono_med'],
                  padx=20, pady=8).pack(side='right', padx=4)

        self._boot_refresh()

    def _boot_refresh(self):
        self._boot_out.delete(1.0, tk.END)
        self._boot_out.insert(tk.END, "🔍 Scanning for USB drives…\n", 'info')

        def _exec():
            res = subprocess.run(['lsblk','-d','-o','NAME,SIZE,MODEL,TRAN','-n'],
                                 capture_output=True, text=True)
            drives = []
            self.usb_devices = []
            for line in res.stdout.split('\n'):
                if not line.strip(): continue
                parts = line.split(None, 3)
                if len(parts) < 2: continue
                name = parts[0]; size = parts[1]
                model = parts[2] if len(parts) > 2 else "Unknown"
                tran  = parts[3] if len(parts) > 3 else ""
                if name in ('sda', 'nvme0n1'): continue
                if 'usb' in tran.lower() or name.startswith('sd'):
                    label = f"/dev/{name}  [{size}]"
                    drives.append(label)
                    self.usb_devices.append({'device': f"/dev/{name}", 'size': size, 'model': model})
                    self._boot_out.insert(tk.END, f"  💾 {label}\n", 'success')
            self._usb_menu['values'] = drives
            if drives and not self.usb_drive.get():
                self.usb_drive.set(drives[0])
                d = self.usb_devices[0]
                self.usb_drive_info.set(f"{d['device']}  —  {d['size']}  —  {d['model']}")
            if not drives:
                self._boot_out.insert(tk.END, "⚠  No USB drives detected\n", 'warning')
            else:
                self._boot_out.insert(tk.END, f"\n✅  {len(drives)} drive(s) found\n", 'success')

        threading.Thread(target=_exec, daemon=True).start()

    def _boot_dev_selected(self, _):
        sel = self.usb_drive.get()
        for d in self.usb_devices:
            if sel.startswith(d['device']):
                self.usb_drive_info.set(f"{d['device']}  —  {d['size']}  —  {d['model']}")
                break

    def _browse_iso(self):
        fn = filedialog.askopenfilename(
            title="Select ISO File",
            filetypes=[("ISO images","*.iso"),("All files","*.*")])
        if fn:
            self.iso_path.set(fn)
            sz = os.path.getsize(fn) / (1024**2)
            self._boot_out.insert(tk.END,
                f"📀 Selected: {os.path.basename(fn)} ({sz:.0f} MB)\n", 'info')

    def _boot_auto_iso(self):
        self._boot_out.insert(tk.END, "🔍 Searching for ISO files…\n", 'info')

        def _exec():
            found = []
            for d in ['~/Downloads','~/Desktop','~']:
                p = os.path.expanduser(d)
                if not os.path.exists(p): continue
                try:
                    for f in os.listdir(p):
                        if f.lower().endswith('.iso'):
                            fp = os.path.join(p, f)
                            found.append(fp)
                            sz = os.path.getsize(fp)/(1024**2)
                            self._boot_out.insert(tk.END, f"  💿 {f} ({sz:.0f} MB)\n", 'info')
                except Exception:
                    pass
            if found:
                found.sort(key=lambda x: os.path.getsize(x), reverse=True)
                if not self.iso_path.get():
                    self.iso_path.set(found[0])
                    self._boot_out.insert(tk.END,
                        f"✅ Auto-selected: {os.path.basename(found[0])}\n", 'success')
            else:
                self._boot_out.insert(tk.END, "ℹ  No ISO files found.\n", 'dim')

        threading.Thread(target=_exec, daemon=True).start()

    def _boot_create(self):
        device = self.usb_drive.get().split()[0]
        iso    = self.iso_path.get()
        if not device or not iso:
            self._boot_out.insert(tk.END, "❌ Select a device and ISO first.\n", 'error')
            return
        if not os.path.exists(device):
            self._boot_out.insert(tk.END, f"❌ Device not found: {device}\n", 'error')
            return
        if not os.path.exists(iso):
            self._boot_out.insert(tk.END, f"❌ ISO not found: {iso}\n", 'error')
            return
        sz = os.path.getsize(iso)/(1024**2)
        if not messagebox.askyesno("⚠ DESTRUCTIVE OPERATION",
            f"Target  : {device}\nISO     : {os.path.basename(iso)} ({sz:.0f} MB)\n\n"
            f"ALL data on {device} will be WIPED.\n\nContinue?"):
            return

        self._boot_out.delete(1.0, tk.END)
        self._boot_out.insert(tk.END, "📀 Writing ISO — please wait…\n", 'info')

        def _exec():
            try:
                subprocess.run(f"sudo umount {device}* 2>/dev/null", shell=True)
                cmd = f'sudo dd if="{iso}" of={device} bs=4M status=progress conv=fsync'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode == 0:
                    self._boot_out.insert(tk.END, "\n✅ Bootable USB created!\n", 'success')
                else:
                    self._boot_out.insert(tk.END, f"\n❌ {res.stderr}\n", 'error')
            except Exception as e:
                self._boot_out.insert(tk.END, f"\n❌ {e}\n", 'error')

        threading.Thread(target=_exec, daemon=True).start()

    # ─── STORAGE FORMAT TAB ──────────────────────────────────────────────────

    def _tab_storage_format(self):
        tab = tk.Frame(self.nb, bg=PALETTE['bg2'])
        self.nb.add(tab, text="  💾 FORMAT  ")

        warn = tk.Frame(tab, bg=PALETTE['danger'], height=28)
        warn.pack(fill='x', padx=6, pady=(6, 0))
        warn.pack_propagate(False)
        tk.Label(warn,
                 text="⚠  WARNING: Formatting will PERMANENTLY ERASE all data on the selected device!  ⚠",
                 font=FONTS['label'],
                 bg=PALETTE['danger'], fg='#ffffff').pack(pady=4)

        card = tk.Frame(tab, bg=PALETTE['card'],
                        highlightbackground=PALETTE['border'],
                        highlightthickness=1)
        card.pack(fill='both', expand=True, padx=6, pady=6)

        section_label(card, "OPERATION LOG")
        _, self._fmt_out = scrolled_output(card, height=8)
        self._fmt_out.master.pack(fill='x', padx=12, pady=4)

        # Controls
        ctrl = tk.Frame(card, bg=PALETTE['card'])
        ctrl.pack(fill='x', padx=12, pady=4)

        # Left: device
        left = tk.Frame(ctrl, bg=PALETTE['card'])
        left.pack(side='left', fill='both', expand=True, padx=(0,10))

        tk.Label(left, text="DEVICE", font=FONTS['label'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w')
        self._fmt_menu = ttk.Combobox(left, textvariable=self.format_device,
                                      style='Cyber.TCombobox', width=38)
        self._fmt_menu.pack(fill='x', pady=2)
        self._fmt_menu.bind('<<ComboboxSelected>>', self._fmt_dev_selected)
        tk.Label(left, textvariable=self.format_dev_info,
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w')

        # Right: filesystem + label
        right = tk.Frame(ctrl, bg=PALETTE['card'])
        right.pack(side='right', fill='both', expand=True)

        tk.Label(right, text="FILESYSTEM", font=FONTS['label'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w')
        ttk.Combobox(right, textvariable=self.fs_type,
                     values=['ext4','ntfs','fat32','exfat'],
                     style='Cyber.TCombobox', width=18).pack(anchor='w', pady=2)

        tk.Label(right, text="LABEL  (optional)", font=FONTS['label'],
                 bg=PALETTE['card'], fg=PALETTE['text_dim']).pack(anchor='w', pady=(6,0))
        tk.Entry(right, textvariable=self.volume_label,
                 bg=PALETTE['grid'], fg=PALETTE['text'],
                 insertbackground=PALETTE['primary'],
                 font=FONTS['mono_tiny'], relief='flat', bd=0,
                 highlightbackground=PALETTE['border'],
                 highlightthickness=1, width=22).pack(anchor='w', ipady=4, pady=2)

        # Actions
        act = tk.Frame(card, bg=PALETTE['card'])
        act.pack(fill='x', padx=12, pady=8)

        cyber_btn(act, "↺  REFRESH DEVICES", self._fmt_refresh,
                  color=PALETTE['panel'], text_color=PALETTE['primary'],
                  font=FONTS['label']).pack(side='left', padx=4)
        cyber_btn(act, "💾  FORMAT DEVICE",
                  self._fmt_do,
                  color=PALETTE['danger'],
                  text_color='#ffffff',
                  font=FONTS['mono_med'],
                  padx=20, pady=8).pack(side='right', padx=4)

        self._fmt_refresh()

    def _fmt_refresh(self):
        self._fmt_out.delete(1.0, tk.END)
        self._fmt_out.insert(tk.END, "🔍 Scanning storage devices…\n", 'info')

        def _exec():
            res = subprocess.run(['lsblk','-o','NAME,SIZE,TYPE,MOUNTPOINT','-n'],
                                 capture_output=True, text=True)
            devs = []
            self.storage_devices = []
            for line in res.stdout.split('\n'):
                if not line.strip(): continue
                parts = line.split()
                if len(parts) < 2: continue
                name = parts[0]; size = parts[1]
                dtype = parts[2] if len(parts) > 2 else 'disk'
                mnt   = parts[3] if len(parts) > 3 else ''
                if name in ('sda','nvme0n1'): continue
                if dtype in ('disk','part'):
                    lbl = f"/dev/{name}  [{size}]  {dtype}" + (" (mounted)" if mnt else "")
                    devs.append(lbl)
                    self.storage_devices.append({'device': f"/dev/{name}",
                                                 'size': size, 'type': dtype, 'mount': mnt})
                    self._fmt_out.insert(tk.END, f"  💾 {lbl}\n", 'info')
            self._fmt_menu['values'] = devs
            if not devs:
                self._fmt_out.insert(tk.END, "⚠  No devices found\n", 'warning')
            else:
                self._fmt_out.insert(tk.END, f"\n✅  {len(devs)} device(s) found\n", 'success')

        threading.Thread(target=_exec, daemon=True).start()

    def _fmt_dev_selected(self, _):
        sel = self.format_device.get()
        for d in self.storage_devices:
            if sel.startswith(d['device']):
                mnt = f" — MOUNTED at {d['mount']}" if d['mount'] else ""
                self.format_dev_info.set(
                    f"{d['device']}  [{d['size']}]  {d['type']}{mnt}")
                break

    def _fmt_do(self):
        device = self.format_device.get().split()[0]
        fs     = self.fs_type.get()
        label  = self.volume_label.get()
        if not device:
            self._fmt_out.insert(tk.END, "❌ Select a device first.\n", 'error'); return
        if not os.path.exists(device):
            self._fmt_out.insert(tk.END, f"❌ Device not found: {device}\n", 'error'); return
        res = subprocess.run(f"mount | grep {device}", shell=True,
                             capture_output=True, text=True)
        if res.stdout:
            self._fmt_out.insert(tk.END, f"⚠  {device} is mounted — unmount first.\n", 'warning')
            return
        if not messagebox.askyesno("⚠ DESTRUCTIVE OPERATION",
            f"Device : {device}\nFormat : {fs}\n\nAll data will be ERASED.\n\nContinue?"):
            return

        self._fmt_out.delete(1.0, tk.END)
        self._fmt_out.insert(tk.END, f"💾 Formatting {device} as {fs}…\n", 'info')

        def _exec():
            cmds = {'ext4':  f'sudo mkfs.ext4 -F {f"-L {label}" if label else ""} {device}',
                    'ntfs':  f'sudo mkfs.ntfs -F {f"-L {label}" if label else ""} {device}',
                    'fat32': f'sudo mkfs.fat -F 32 {f"-n {label}" if label else ""} {device}',
                    'exfat': f'sudo mkfs.exfat {f"-n {label}" if label else ""} {device}'}
            cmd = cmds.get(fs)
            if not cmd:
                self._fmt_out.insert(tk.END, f"❌ Unsupported: {fs}\n", 'error'); return
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if r.returncode == 0:
                    self._fmt_out.insert(tk.END,
                        f"\n✅ Formatted as {fs}!" + (f"\n🏷  Label: {label}" if label else "") + "\n",
                        'success')
                else:
                    self._fmt_out.insert(tk.END, f"\n❌ {r.stderr}\n", 'error')
            except Exception as e:
                self._fmt_out.insert(tk.END, f"\n❌ {e}\n", 'error')

        threading.Thread(target=_exec, daemon=True).start()

    # ─── STATUS BAR ──────────────────────────────────────────────────────────

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=PALETTE['panel'],
                       highlightbackground=PALETTE['border'],
                       highlightthickness=1,
                       height=28)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)

        self._led = tk.Label(bar, text="●",
                             font=('Courier New', 11),
                             bg=PALETTE['panel'],
                             fg=PALETTE['success'])
        self._led.pack(side='left', padx=10)

        self._status_lbl = tk.Label(bar, text="SYSTEM READY",
                                    font=FONTS['mono_tiny'],
                                    bg=PALETTE['panel'],
                                    fg=PALETTE['text_dim'])
        self._status_lbl.pack(side='left')

        # Right: hostname + IP
        try:
            hostname = socket.gethostname()
            ip       = socket.gethostbyname(hostname)
        except Exception:
            hostname = "unknown"; ip = "0.0.0.0"

        tk.Label(bar, text=f"{hostname}  |  {ip}  |  {platform.system()} {platform.release()}",
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['panel'],
                 fg=PALETTE['text_dim']).pack(side='right', padx=12)

        # Runtime counter
        tk.Frame(bar, bg=PALETTE['border'], width=1).pack(
            side='right', fill='y', pady=5, padx=4)

        tk.Label(bar, text="UPTIME ▸",
                 font=FONTS['mono_xsmall'],
                 bg=PALETTE['panel'],
                 fg=PALETTE['text_dim']).pack(side='right', padx=(0, 2))

        self._runtime_lbl = tk.Label(bar, text="00:00:00",
                                     font=('Courier New', 9, 'bold'),
                                     bg=PALETTE['panel'],
                                     fg=PALETTE['primary'])
        self._runtime_lbl.pack(side='right', padx=(0, 4))

        tk.Frame(bar, bg=PALETTE['border'], width=1).pack(
            side='right', fill='y', pady=5, padx=4)

    def _status(self, msg):
        self._status_lbl.config(text=msg)

    # ══════════════════════════════════════════════════════════════════════════
    #  MONITORING
    # ══════════════════════════════════════════════════════════════════════════

    def _start_monitors(self):
        self._upd_cpu()
        self._upd_mem()
        self._upd_dsk()
        self._upd_quick()
        self._pulse_led()
        self._upd_runtime()

    def _upd_runtime(self):
        try:
            elapsed = datetime.now() - self._start_time
            total_s = int(elapsed.total_seconds())
            h  = total_s // 3600
            m  = (total_s % 3600) // 60
            s  = total_s % 60
            self._runtime_lbl.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            # Colour shifts: green → amber → red as hours increase
            if h >= 8:
                self._runtime_lbl.config(fg=PALETTE['danger'])
            elif h >= 4:
                self._runtime_lbl.config(fg=PALETTE['accent2'])
            else:
                self._runtime_lbl.config(fg=PALETTE['primary'])
        except Exception:
            pass
        self.root.after(1000, self._upd_runtime)

    def _upd_cpu(self):
        try:
            v = psutil.cpu_percent()
            self._gauge_cpu.set_value(v)
        except Exception:
            pass
        self.root.after(1000, self._upd_cpu)

    def _upd_mem(self):
        try:
            v = psutil.virtual_memory().percent
            self._gauge_mem.set_value(v)
        except Exception:
            pass
        self.root.after(1000, self._upd_mem)

    def _upd_dsk(self):
        try:
            v = psutil.disk_usage('/').percent
            self._gauge_dsk.set_value(v)
        except Exception:
            pass
        self.root.after(3000, self._upd_dsk)

    def _upd_quick(self):
        try:
            cpu  = psutil.cpu_percent()
            mem  = psutil.virtual_memory().percent
            dsk  = psutil.disk_usage('/').percent
            self._q_cpu.config(text=f"{cpu:.0f}%",
                               fg=PALETTE['danger'] if cpu > 85 else PALETTE['primary'])
            self._q_mem.config(text=f"{mem:.0f}%",
                               fg=PALETTE['danger'] if mem > 90 else PALETTE['secondary'])
            self._q_disk.config(text=f"{dsk:.0f}%",
                                fg=PALETTE['danger'] if dsk > 85 else PALETTE['accent2'])
        except Exception:
            pass
        self.root.after(2000, self._upd_quick)

    def _pulse_led(self):
        colours = [PALETTE['success'], PALETTE['primary_dim']]
        current = self._led.cget('fg')
        self._led.config(fg=colours[0] if current == colours[1] else colours[1])
        self.root.after(900, self._pulse_led)

    def _tick_time(self):
        self._time_lbl.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_time)

    # ══════════════════════════════════════════════════════════════════════════
    #  POWERSHELL RUNNER
    # ══════════════════════════════════════════════════════════════════════════

    def _run_ps(self, feat, output_widget, clear=False, extra=None, is_text=False):
        def _execute():
            if clear and output_widget:
                output_widget.delete(1.0, tk.END)

            cmd = ['pwsh', '-File', self.ps_script, '-Feature', str(feat)]
            if extra:
                for k, v in extra.items():
                    if v: cmd.extend([f'-{k}', str(v)])

            if not is_text and output_widget:
                ts = datetime.now().strftime('%H:%M:%S')
                output_widget.insert(tk.END,
                    f"┌{'─'*58}┐\n"
                    f"│  Feature {feat:>2}  │  {ts}  "
                    f"{'─' * (58 - 24 - len(str(feat)))}│\n"
                    f"└{'─'*58}┘\n\n", 'header')

            if hasattr(self, '_led'):
                self._led.config(fg=PALETTE['accent2'])
            if hasattr(self, '_status_lbl'):
                self._status_lbl.config(text=f"Running feature {feat}…")

            try:
                self.current_proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True, bufsize=1)
                if output_widget:
                    for line in self.current_proc.stdout:
                        output_widget.insert(tk.END, line, 'info')
                        output_widget.see(tk.END)
                self.current_proc.wait()
                if output_widget:
                    stderr = self.current_proc.stderr.read()
                    if stderr:
                        output_widget.insert(tk.END, f"\n{stderr}\n", 'error')
                    if not is_text:
                        output_widget.insert(tk.END,
                            f"\n✅  COMPLETED\n", 'success')
            except Exception as e:
                if output_widget:
                    output_widget.insert(tk.END, f"\n❌  ERROR: {e}\n", 'error')
            finally:
                self.current_proc = None
                if hasattr(self, '_led'):
                    self._led.config(fg=PALETTE['success'])
                if hasattr(self, '_status_lbl'):
                    self._status_lbl.config(text="SYSTEM READY")

        threading.Thread(target=_execute, daemon=True).start()

    def _stop_process(self):
        if self.current_proc and self.current_proc.poll() is None:
            self.current_proc.terminate()
            self._status("Process stopped by user")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.withdraw()              # hide while building

    app = CompleteOSUtility(root)

    # Centre on screen
    root.update_idletasks()
    w, h = 1440, 900
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
