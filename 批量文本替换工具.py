import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
import threading

class BatchReplaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文本替换工具 - 高性能版")
        self.root.geometry("900x700")

        self.rules = []
        self.source_file = None
        self.output_file = None
        self.is_running = False

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        title_label = ttk.Label(main_frame, text="批量文本替换工具", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)

        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(file_frame, text="选择源文件", command=self.select_source).grid(row=0, column=0, padx=5)
        self.source_label = ttk.Label(file_frame, text="未选择文件", foreground="gray")
        self.source_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Button(file_frame, text="选择输出文件", command=self.select_output).grid(row=1, column=0, padx=5, pady=5)
        self.output_label = ttk.Label(file_frame, text="未选择文件", foreground="gray")
        self.output_label.grid(row=1, column=1, sticky=tk.W, pady=5)

        rules_frame = ttk.LabelFrame(main_frame, text="替换规则 (原文本 → 新文本)", padding="10")
        rules_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        rules_frame.columnconfigure(0, weight=1)
        rules_frame.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(rules_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.rules_listbox = tk.Listbox(list_frame, height=15, yscrollcommand=scrollbar.set,
                                        font=("微软雅黑", 10))
        self.rules_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.rules_listbox.yview)

        btn_frame = ttk.Frame(rules_frame)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        ttk.Button(btn_frame, text="添加规则", command=self.add_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空规则", command=self.clear_rules).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="从文件导入规则", command=self.import_rules).pack(side=tk.LEFT, padx=5)

        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        self.use_regex_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="使用正则表达式", variable=self.use_regex_var).pack(side=tk.LEFT, padx=10)

        self.case_sensitive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive_var).pack(side=tk.LEFT, padx=10)

        self.preview_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="替换前预览", variable=self.preview_var).pack(side=tk.LEFT, padx=10)

        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        action_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(action_frame, text="就绪", font=("微软雅黑", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.progress = ttk.Progressbar(action_frame, mode='determinate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        btn_execute = ttk.Button(action_frame, text="开始替换", command=self.execute_replace, style="Accent.TButton")
        btn_execute.grid(row=2, column=0, pady=5)

        style = ttk.Style()
        style.configure("Accent.TButton", font=("微软雅黑", 11, "bold"))

    def select_source(self):
        filename = filedialog.askopenfilename(title="选择源文件",
                                               filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if filename:
            self.source_file = filename
            self.source_label.config(text=os.path.basename(filename), foreground="black")

    def select_output(self):
        filename = filedialog.asksaveasfilename(title="选择输出文件",
                                                defaultextension=".txt",
                                                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if filename:
            self.output_file = filename
            self.output_label.config(text=os.path.basename(filename), foreground="black")

    def add_rule(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加替换规则")
        dialog.geometry("500x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="原文本:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        old_entry = ttk.Entry(dialog, width=50)
        old_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="新文本:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        new_entry = ttk.Entry(dialog, width=50)
        new_entry.grid(row=1, column=1, padx=5, pady=5)

        def confirm():
            old_text = old_entry.get()
            new_text = new_entry.get()
            if old_text:
                self.rules.append((old_text, new_text))
                self.rules_listbox.insert(tk.END, f"{old_text} → {new_text}")
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "原文本不能为空！")

        ttk.Button(dialog, text="确定", command=confirm).grid(row=2, column=0, columnspan=2, pady=10)
        old_entry.focus()

    def delete_rule(self):
        selection = self.rules_listbox.curselection()
        if selection:
            index = selection[0]
            self.rules.pop(index)
            self.rules_listbox.delete(index)

    def clear_rules(self):
        if self.rules:
            if messagebox.askyesno("确认", "确定要清空所有规则吗？"):
                self.rules.clear()
                self.rules_listbox.delete(0, tk.END)

    def import_rules(self):
        filename = filedialog.askopenfilename(title="导入规则文件",
                                             filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                count = 0
                for line in lines:
                    line = line.strip()
                    if '→' in line:
                        parts = line.split('→')
                        if len(parts) == 2:
                            old = parts[0].strip()
                            new = parts[1].strip()
                            self.rules.append((old, new))
                            self.rules_listbox.insert(tk.END, f"{old} → {new}")
                            count += 1
                messagebox.showinfo("成功", f"成功导入 {count} 条规则！")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败：{str(e)}")

    def execute_replace(self):
        if not self.source_file:
            messagebox.showwarning("警告", "请先选择源文件！")
            return
        if not self.output_file:
            messagebox.showwarning("警告", "请先选择输出文件！")
            return
        if not self.rules:
            messagebox.showwarning("警告", "请至少添加一条替换规则！")
            return

        if self.preview_var.get():
            preview_text = "替换预览：\n\n"
            try:
                with open(self.source_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for old, new in self.rules:
                    if self.use_regex_var.get():
                        if self.case_sensitive_var.get():
                            count = len(re.findall(re.escape(old), content))
                        else:
                            count = len(re.findall(re.escape(old), content, re.IGNORECASE))
                    else:
                        if self.case_sensitive_var.get():
                            count = content.count(old)
                        else:
                            count = content.lower().count(old.lower())

                    preview_text += f"「{old}」→「{new}」替换 {count} 处\n"

                preview_text += f"\n共 {len(self.rules)} 条规则，是否继续？"

                if not messagebox.askyesno("确认替换", preview_text):
                    return
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败：{str(e)}")
                return

        threading.Thread(target=self._do_replace, daemon=True).start()

    def _do_replace(self):
        self.is_running = True
        self.root.after(0, lambda: self.status_label.config(text="正在处理..."))
        self.root.after(0, lambda: self.progress.config(value=0))

        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            processed = 0

            if self.use_regex_var.get():
                flags = 0 if self.case_sensitive_var.get() else re.IGNORECASE
                for old, new in self.rules:
                    content = re.sub(re.escape(old), new, content, flags=flags)
                    processed += 1
                    progress = (processed / len(self.rules)) * 100
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))
            else:
                for old, new in self.rules:
                    if self.case_sensitive_var.get():
                        content = content.replace(old, new)
                    else:
                        pattern = re.compile(re.escape(old), re.IGNORECASE)
                        content = pattern.sub(new, content)

                    processed += 1
                    progress = (processed / len(self.rules)) * 100
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))

            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.root.after(0, lambda: self.status_label.config(text="替换完成！"))
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: messagebox.showinfo("成功", "替换完成！"))

        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="处理失败"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败：{str(e)}"))

        finally:
            self.is_running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchReplaceApp(root)
    root.mainloop()
