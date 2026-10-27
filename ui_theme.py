"""PolarLabs utility UI, inspired by PolarLabs QR Studio and PolarWatch."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

BG="#F7FAFC"
PANEL="#FFFFFF"
INK="#09263B"
MUTED="#617D8F"
SURFACE="#EEF5F8"
BORDER="#D8E5EB"
MINT="#D8F6F3"
MINT_HOVER="#8BE7E2"
DEEP_MINT="#138A91"
LILAC="#E5F8FA"
LILAC_INK="#0C7582"
OLD_DARK={"#081522","#091623","#12273a","#122537","#1a4051"}
OLD_TEXT={"#e9f5f8","#eaf6fa","#9cb9c7","#9bb5c2"}
OLD_ACC={"#31d9d2","#27d6d0"}
def apply_theme(root):
    root.configure(bg=BG)
    sty=ttk.Style(root)
    sty.theme_use("clam")
    sty.configure("TNotebook",background=BG,borderwidth=0)
    sty.configure("TNotebook.Tab",background=SURFACE,foreground=MUTED,padding=(20,11),font=("Segoe UI",10,"bold"),borderwidth=0)
    sty.map("TNotebook.Tab",background=[("selected",PANEL)],foreground=[("selected",DEEP_MINT)])
    sty.configure("Treeview",background=PANEL,fieldbackground=PANEL,foreground=INK,rowheight=35,font=("Segoe UI",10),borderwidth=0)
    sty.map("Treeview",background=[("selected",LILAC)],foreground=[("selected",INK)])
    sty.configure("Treeview.Heading",background=SURFACE,foreground=INK,font=("Segoe UI",10,"bold"),padding=(10,10),relief="flat")
    sty.configure("TCombobox",fieldbackground=PANEL,background=SURFACE,foreground=INK,arrowcolor=DEEP_MINT,padding=(8,8))
    sty.map("TCombobox",fieldbackground=[("readonly",PANEL)],foreground=[("readonly",INK)])
    sty.configure("Horizontal.TProgressbar",troughcolor="#E8EBF2",background=DEEP_MINT,borderwidth=0,thickness=12)
    def recolor(widget):
        try:
            if isinstance(widget,tk.Button):
                old=widget.cget("bg").lower()
                primary=old in OLD_ACC
                widget.configure(bg=DEEP_MINT if primary else PANEL,fg="#FFFFFF" if primary else INK,
                     activebackground=MINT_HOVER if primary else SURFACE,activeforeground=INK,
                     relief="flat",bd=0,padx=16,pady=11,
                     font=("Segoe UI",10,"bold"),cursor="hand2",
                     highlightthickness=1,highlightbackground=DEEP_MINT if primary else BORDER)
            elif isinstance(widget,tk.Text):
                widget.configure(bg=PANEL,fg=INK,insertbackground=INK,
                   selectbackground=LILAC,selectforeground=INK,
                   relief="flat",bd=0,highlightthickness=1,
                   highlightbackground=BORDER,highlightcolor=DEEP_MINT)
            elif isinstance(widget,tk.Entry):
                widget.configure(bg=PANEL,fg=INK,insertbackground=INK,
                   selectbackground=LILAC,selectforeground=INK,
                   relief="flat",bd=0,highlightthickness=1,
                   highlightbackground=BORDER,highlightcolor=DEEP_MINT,
                   font=("Segoe UI",11))
            elif isinstance(widget,tk.Scale):
                widget.configure(bg=PANEL,fg=INK,troughcolor=LILAC,
                     activebackground=DEEP_MINT,highlightthickness=0)
            elif isinstance(widget,(tk.Frame,tk.Label,tk.LabelFrame,tk.Checkbutton,tk.Radiobutton,tk.Listbox)):
                try:
                    old=widget.cget("bg").lower()
                    if old in OLD_DARK:widget.configure(bg=BG if old in ("#081522","#091623") else PANEL)
                except tk.TclError:pass
                if isinstance(widget,(tk.Label,tk.Checkbutton,tk.Radiobutton,tk.Listbox,tk.LabelFrame)):
                    try:
                        fg=widget.cget("fg").lower()
                        if fg in OLD_ACC:widget.configure(fg=DEEP_MINT)
                        elif fg in OLD_TEXT:widget.configure(fg=MUTED if fg in ("#9cb9c7","#9bb5c2") else INK)
                    except tk.TclError:pass
                    if isinstance(widget,tk.Listbox):
                        widget.configure(bg=PANEL,fg=INK,selectbackground=LILAC,selectforeground=INK)
            elif isinstance(widget,tk.Canvas):
                if widget.cget("bg").lower() in OLD_DARK:widget.configure(bg=PANEL)
        except tk.TclError:pass
        for child in widget.winfo_children():recolor(child)
    recolor(root)
    set_window_icon(root)

def set_window_icon(window):
    app=window.title().split("|")[0].strip()
    base=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))
    for ext in (".ico",".png"):
        path=base/(app+ext)
        if not path.exists():path=Path(__file__).resolve().parent/(app+ext)
        if not path.exists():continue
        try:
            if ext==".ico":window.iconbitmap(default=str(path))
            else:
                photo=tk.PhotoImage(file=str(path))
                window.iconphoto(True,photo)
                window._polar_icon=photo
        except (OSError,tk.TclError):pass
