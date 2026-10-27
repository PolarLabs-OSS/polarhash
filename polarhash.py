"""PolarHash — PolarLabs-OSS. Offline checksum utility."""
import csv
import hashlib
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

BG="#091623"
PANEL="#122537"
ACCENT="#27D6D0"
FG="#EAF6FA"
MUTED="#9BB5C2"
ALGOS=("SHA256","SHA512","SHA1","MD5","BLAKE2B")
CHUNK=1024*1024

def checksum(path, algo="SHA256", cancel=None):
    h=hashlib.new(algo.lower())
    with open(path,"rb") as f:
        while True:
            if cancel is not None and cancel.is_set():
                raise InterruptedError("Operazione annullata")
            block=f.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def verify_manifest(path, cancel=None):
    base=Path(path).resolve().parent
    results=[]
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        value,sep,filename=line.partition("  ")
        if not sep:
            continue
        if filename.startswith("*"):
            filename=filename[1:]
        target=(base/filename).resolve()
        if not target.is_relative_to(base):
            results.append((filename,"PATH NON SICURO"))
        elif not target.is_file():
            results.append((filename,"MANCANTE"))
        else:
            try:
                results.append((filename,"OK" if checksum(target,"SHA256",cancel).lower()==value.strip().lower() else "DIFFERENTE"))
            except OSError:
                results.append((filename,"ERRORE LETTURA"))
    return results

class App:
    def __init__(self, root):
        self.root=root
        root.title("PolarHash | PolarLabs-OSS")
        root.geometry("1030x680")
        root.configure(bg=BG)
        self.paths=[]
        self.hashes={}
        self.cancel=threading.Event()
        self.busy=False
        style=ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",background=PANEL,foreground=FG,fieldbackground=PANEL,rowheight=28,borderwidth=0)
        style.configure("Treeview.Heading",background="#1B3850",foreground=FG,font=("Segoe UI",10,"bold"))
        style.map("Treeview",background=[("selected","#23616E")])
        outer=tk.Frame(root,bg=BG,padx=25,pady=21)
        outer.pack(fill="both",expand=True)
        tk.Label(outer,text="POLAR / HASH",font=("Segoe UI",25,"bold"),fg=ACCENT,bg=BG).pack(anchor="w")
        tk.Label(outer,text="Verifica integrità file  •  Nessun upload  •  Elaborazione locale",font=("Segoe UI",10),fg=MUTED,bg=BG).pack(anchor="w",pady=(0,17))
        bar=tk.Frame(outer,bg=BG)
        bar.pack(fill="x",pady=6)
        self.button(bar,"+ Aggiungi file",self.add).pack(side="left",padx=(0,8))
        self.button(bar,"Cartella",self.folder).pack(side="left",padx=(0,8))
        self.button(bar,"Calcola",self.run_hash).pack(side="left",padx=(0,8))
        self.button(bar,"Annulla",self.stop).pack(side="left",padx=(0,8))
        self.button(bar,"Svuota",self.clear).pack(side="left")
        options=tk.Frame(outer,bg=BG)
        options.pack(fill="x",pady=(9,13))
        tk.Label(options,text="Algoritmo:",fg=FG,bg=BG).pack(side="left")
        self.algorithm=tk.StringVar(value="SHA256")
        ttk.Combobox(options,values=ALGOS,textvariable=self.algorithm,state="readonly",width=12).pack(side="left",padx=9)
        tk.Label(options,text="Hash atteso:",fg=FG,bg=BG).pack(side="left",padx=(22,6))
        self.expected=tk.StringVar()
        tk.Entry(options,textvariable=self.expected,bg=PANEL,fg=FG,insertbackground=FG,relief="flat",font=("Consolas",10)).pack(side="left",fill="x",expand=True,ipady=6)
        self.tree=ttk.Treeview(outer,columns=("name","hash","status"),show="headings")
        for col,label,width in (("name","File",280),("hash","Checksum",490),("status","Stato",110)):
            self.tree.heading(col,text=label)
            self.tree.column(col,width=width,stretch=(col=="hash"))
        self.tree.pack(fill="both",expand=True)
        self.tree.bind("<Double-1>",self.copy_selected)
        bottom=tk.Frame(outer,bg=BG)
        bottom.pack(fill="x",pady=(12,0))
        self.button(bottom,"Esporta CSV",self.csv_export).pack(side="left",padx=(0,8))
        self.button(bottom,"Esporta SHA256SUMS",self.manifest_export).pack(side="left",padx=(0,8))
        self.button(bottom,"Verifica SHA256SUMS",self.manifest_check).pack(side="left")
        self.progress=ttk.Progressbar(outer,mode="determinate")
        self.progress.pack(fill="x",pady=(14,5))
        self.status=tk.StringVar(value="Pronto. Doppio clic su una riga per copiare l'hash.")
        tk.Label(outer,textvariable=self.status,bg=BG,fg=MUTED,anchor="w").pack(fill="x")
        tk.Label(outer,text="PolarLabs-OSS  •  Open source  •  MD5 e SHA1 solo per compatibilità, non per sicurezza",bg=BG,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",pady=(10,0))

    def button(self,parent,label,action):
        return tk.Button(parent,text=label,command=action,bg=PANEL,fg=FG,activebackground="#1C5765",activeforeground=FG,relief="flat",padx=13,pady=8,cursor="hand2")

    def add_paths(self,paths):
        for path in paths:
            if os.path.isfile(path) and path not in self.paths:
                self.paths.append(path)
                self.tree.insert("","end",iid=str(len(self.paths)-1),values=(path,"","In attesa"))
        self.status.set(f"{len(self.paths)} file selezionati")

    def add(self):
        self.add_paths(filedialog.askopenfilenames(title="Seleziona file"))

    def folder(self):
        p=filedialog.askdirectory(title="Seleziona cartella")
        if p:
            self.add_paths(str(x) for x in Path(p).rglob("*") if x.is_file())

    def clear(self):
        if self.busy: return
        self.paths=[];self.hashes={}
        for item in self.tree.get_children(): self.tree.delete(item)
        self.progress["value"]=0
        self.status.set("Elenco svuotato")

    def stop(self):
        self.cancel.set()

    def run_hash(self):
        if self.busy or not self.paths: return
        algo=self.algorithm.get()
        exp=self.expected.get().strip().lower()
        self.busy=True;self.cancel.clear()
        self.progress["maximum"]=len(self.paths)
        self.progress["value"]=0
        def worker():
            try:
                for index,path in enumerate(list(self.paths)):
                    if self.cancel.is_set():break
                    try:
                        value=checksum(path,algo,self.cancel)
                        status=("CORRISPONDE" if value.lower()==exp else "DIVERSO") if exp else "OK"
                        self.hashes[path]=(algo,value)
                    except InterruptedError:break
                    except (OSError,ValueError) as e:
                        value="";status=f"ERRORE: {str(e)[:45]}"
                    self.root.after(0,lambda i=index,p=path,v=value,s=status: self.tree.item(str(i),values=(p,v,s)))
                    self.root.after(0,lambda n=index+1:self.progress.configure(value=n))
            finally:
                self.root.after(0,self.finish)
        threading.Thread(target=worker,daemon=True).start()

    def finish(self):
        self.busy=False
        self.status.set("Interrotto" if self.cancel.is_set() else "Calcolo completato")

    def copy_selected(self,event=None):
        chosen=self.tree.selection()
        if chosen:
            val=self.tree.item(chosen[0],"values")[1]
            if val:self.root.clipboard_clear();self.root.clipboard_append(val);self.status.set("Hash copiato")

    def csv_export(self):
        if not self.hashes:return messagebox.showinfo("PolarHash","Calcola prima gli hash")
        name=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if name:
            with open(name,"w",newline="",encoding="utf-8-sig") as f:
                w=csv.writer(f);w.writerow(["File","Algoritmo","Hash"])
                for p,(a,v) in self.hashes.items():w.writerow([p,a,v])
            self.status.set(f"Esportato: {name}")

    def manifest_export(self):
        entries=[(p,v) for p,(a,v) in self.hashes.items() if a=="SHA256"]
        if not entries:return messagebox.showwarning("PolarHash","Calcola prima gli hash SHA256")
        name=filedialog.asksaveasfilename(initialfile="SHA256SUMS",filetypes=[("Manifest","*")])
        if name:
            base=Path(name).resolve().parent
            lines=[]
            for p,v in entries:
                rel=os.path.relpath(p,base)
                if "\n" in rel or "\r" in rel:
                    return messagebox.showerror("PolarHash","Percorso con caratteri non supportati")
                lines.append(f"{v}  {rel}")
            Path(name).write_text("\n".join(lines)+"\n",encoding="utf-8")
            self.status.set("SHA256SUMS esportato")

    def manifest_check(self):
        if self.busy:return
        path=filedialog.askopenfilename(title="Apri SHA256SUMS")
        if not path:return
        self.busy=True;self.cancel.clear()
        self.status.set("Verifica manifest in corso…")
        def worker():
            try:
                results=verify_manifest(path,self.cancel)
                def show():
                    self.clear_after_verify(results)
                self.root.after(0,show)
            except Exception as e:
                self.root.after(0,lambda err=str(e): messagebox.showerror("PolarHash",err))
            finally:
                self.root.after(0,self.finish)
        threading.Thread(target=worker,daemon=True).start()

    def clear_after_verify(self,results):
        self.paths=[];self.hashes={}
        for item in self.tree.get_children():self.tree.delete(item)
        for i,(name,status) in enumerate(results):
            self.tree.insert("","end",iid=str(i),values=(name,"SHA256SUMS",status))
        self.status.set(f"Verificati {len(results)} file")

from ui_theme import apply_theme

if __name__=="__main__":
    root=tk.Tk()
    App(root)
    apply_theme(root)
    root.mainloop()
