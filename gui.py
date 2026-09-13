# gui.py - Tkinter GUI for Steganography tool (embedding, extraction, and analysis)

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from stego_core import hide_data, extract_data, get_image_capacity
from analysis import analyze_images, plot_histograms


class StegoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UniKL Steganography Tool (IKB 21303)")
        self.geometry("1020x760")
        self.minsize(920, 680)

        # configure styles
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._configure_styles()
        self._create_widgets()

    def _configure_styles(self):
        bg_color = "#f5f7fa"
        self.configure(bg=bg_color)
        self.style.configure("TNotebook", background=bg_color)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[14, 6])
        self.style.map("TNotebook.Tab", background=[("selected", "#2b6cb0")], foreground=[("selected", "white")])
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def _create_widgets(self):
        # top header banner
        header_frame = tk.Frame(self, bg="#1a365d", height=70)
        header_frame.pack(fill="x", side="top")
        
        lbl_title = tk.Label(
            header_frame,
            text="Image Steganography Tool",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1a365d"
        )
        lbl_title.pack(anchor="w", padx=20, pady=(10, 0))

        lbl_sub = tk.Label(
            header_frame,
            text="UniKL MIIT - Cryptography & Steganography (IKB 21303)",
            font=("Segoe UI", 9),
            fg="#cbd5e0",
            bg="#1a365d"
        )
        lbl_sub.pack(anchor="w", padx=20, pady=(0, 10))

        # tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=10)

        # tab 1: embed
        self.tab_embed = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_embed, text=" Hide Data (Embed) ")
        self._init_embed_tab()

        # tab 2: extract
        self.tab_extract = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_extract, text=" Extract Data (Reveal) ")
        self._init_extract_tab()

        # tab 3: analysis
        self.tab_analysis = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_analysis, text=" Quality & Histogram Analysis ")
        self._init_analysis_tab()

        # tab 4: about
        self.tab_about = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_about, text=" About & Instructions ")
        self._init_about_tab()

    # embed tab widgets
    def _init_embed_tab(self):
        container = ttk.Frame(self.tab_embed)
        container.pack(fill="both", expand=True)

        left_col = ttk.Frame(container, width=540)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # cover image selection
        grp_cover = ttk.LabelFrame(left_col, text=" Step 1: Select Cover Image ", padding=10)
        grp_cover.pack(fill="x", pady=6)

        f1 = ttk.Frame(grp_cover)
        f1.pack(fill="x")
        self.txt_embed_cover = ttk.Entry(f1, font=("Segoe UI", 9))
        self.txt_embed_cover.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(f1, text="Browse Cover...", command=self._browse_embed_cover).pack(side="right")

        self.lbl_cover_capacity = ttk.Label(grp_cover, text="Capacity: No cover selected", foreground="#718096")
        self.lbl_cover_capacity.pack(anchor="w", pady=(4, 0))

        # secret file selection
        grp_secret = ttk.LabelFrame(left_col, text=" Step 2: Select Secret File to Hide ", padding=10)
        grp_secret.pack(fill="x", pady=6)

        f2 = ttk.Frame(grp_secret)
        f2.pack(fill="x")
        self.txt_embed_secret = ttk.Entry(f2, font=("Segoe UI", 9))
        self.txt_embed_secret.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(f2, text="Browse Secret...", command=self._browse_embed_secret).pack(side="right")

        self.lbl_secret_info = ttk.Label(
            grp_secret,
            text="Supported: Text (.txt), Documents (.pdf, .doc), Images (.png, .jpg)",
            foreground="#4a5568"
        )
        self.lbl_secret_info.pack(anchor="w", pady=(4, 0))

        # stego output path
        grp_output = ttk.LabelFrame(left_col, text=" Step 3: Output Stego Image ", padding=10)
        grp_output.pack(fill="x", pady=6)

        f3 = ttk.Frame(grp_output)
        f3.pack(fill="x")
        self.txt_embed_output = ttk.Entry(f3, font=("Segoe UI", 9))
        self.txt_embed_output.pack(side="left", fill="x", expand=True, padx=(0, 6))
        default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "stego.png")
        self.txt_embed_output.insert(0, default_out)
        ttk.Button(f3, text="Browse Output...", command=self._browse_embed_output).pack(side="right")

        # hide button
        btn_embed = tk.Button(
            left_col,
            text="Hide Secret & Generate Stego Image (stego.png)",
            font=("Segoe UI", 11, "bold"),
            bg="#2b6cb0",
            fg="white",
            activebackground="#2c5282",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=8,
            command=self._do_embed
        )
        btn_embed.pack(fill="x", pady=12)

        # log output
        grp_log = ttk.LabelFrame(left_col, text=" Log & Results ", padding=6)
        grp_log.pack(fill="both", expand=True)
        self.txt_embed_log = tk.Text(grp_log, height=10, font=("Consolas", 9), wrap="word", bg="#edf2f7")
        self.txt_embed_log.pack(fill="both", expand=True)

        # right column: preview image
        right_col = ttk.LabelFrame(container, text=" Cover Image Preview ", padding=8, width=320)
        right_col.pack(side="right", fill="both", padx=(10, 0))
        right_col.pack_propagate(False)

        self.lbl_embed_preview = ttk.Label(right_col, text="No Preview Available\n(Select an image)", anchor="center")
        self.lbl_embed_preview.pack(fill="both", expand=True)

    def _browse_embed_cover(self):
        init_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        path = filedialog.askopenfilename(
            initialdir=init_dir if os.path.exists(init_dir) else ".",
            filetypes=[("Images (*.png;*.bmp)", "*.png;*.bmp"), ("All Files", "*.*")]
        )
        if path:
            self.txt_embed_cover.delete(0, tk.END)
            self.txt_embed_cover.insert(0, path)
            self._update_cover_info(path)
            self._display_preview(path, self.lbl_embed_preview)

    def _update_cover_info(self, path):
        try:
            info = get_image_capacity(path)
            txt = (f"Resolution: {info['width']}x{info['height']} | "
                   f"Pixels: {info['total_pixels']:,} | "
                   f"Max Payload: {info['max_payload_bytes']:,} bytes ({info['max_payload_kb']:.1f} KB)")
            self.lbl_cover_capacity.config(text=txt, foreground="#2b6cb0")
        except Exception as e:
            self.lbl_cover_capacity.config(text=f"Error reading capacity: {e}", foreground="red")

    def _browse_embed_secret(self):
        init_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        path = filedialog.askopenfilename(
            initialdir=init_dir if os.path.exists(init_dir) else ".",
            filetypes=[
                ("Supported Files (*.txt;*.pdf;*.doc;*.png;*.jpg)", "*.txt;*.pdf;*.doc;*.docx;*.png;*.jpg;*.jpeg"),
                ("All Files (*.*)", "*.*")
            ]
        )
        if path:
            self.txt_embed_secret.delete(0, tk.END)
            self.txt_embed_secret.insert(0, path)
            size = os.path.getsize(path)
            name = os.path.basename(path)
            self.lbl_secret_info.config(
                text=f"Selected: {name} ({size:,} bytes / {size/1024:.2f} KB)",
                foreground="#2b6cb0"
            )

    def _browse_embed_output(self):
        init_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        path = filedialog.asksaveasfilename(
            initialdir=init_dir if os.path.exists(init_dir) else ".",
            defaultextension=".png",
            filetypes=[("PNG Image (*.png)", "*.png")]
        )
        if path:
            self.txt_embed_output.delete(0, tk.END)
            self.txt_embed_output.insert(0, path)

    def _display_preview(self, path, label_widget, max_size=(300, 300)):
        # load thumbnail in preview label
        try:
            with Image.open(path) as img:
                img_copy = img.copy()
                img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_copy)
                label_widget.config(image=photo, text="")
                label_widget.image = photo
        except Exception as e:
            label_widget.config(image="", text=f"Preview error:\n{e}")

    def _do_embed(self):
        # execute hiding process
        cover = self.txt_embed_cover.get().strip()
        secret = self.txt_embed_secret.get().strip()
        output = self.txt_embed_output.get().strip()

        if not cover or not os.path.exists(cover):
            messagebox.showerror("Error", "Please select a valid cover image.")
            return
        if not secret or not os.path.exists(secret):
            messagebox.showerror("Error", "Please select a secret file to hide.")
            return
        if not output:
            messagebox.showerror("Error", "Please choose an output image path.")
            return

        try:
            res = hide_data(cover, secret, output)
            analysis = analyze_images(cover, res["output_path"])

            log_msg = (
                f"=== Secret Data Embedded Successfully ===\n"
                f"Stego Image: {res['output_path']}\n"
                f"Payload Size: {res['payload_bytes']:,} bytes ({res['file_extension']})\n"
                f"Bits Modified: {res['bits_modified']:,} bits\n"
                f"Cover Size: {analysis['cover_file_size']:,} bytes\n"
                f"Stego Size: {analysis['stego_file_size']:,} bytes\n"
                f"Size Change: {analysis['size_delta_bytes']:+,} bytes ({analysis['size_change_pct']:+.2f}%)\n"
                f"PSNR: {analysis['psnr_db']:.2f} dB | SSIM: {analysis['ssim']:.4f}\n"
                f"=========================================\n\n"
            )
            self.txt_embed_log.insert(tk.END, log_msg)
            self.txt_embed_log.see(tk.END)

            # update analysis tab inputs
            self.txt_ana_cover.delete(0, tk.END)
            self.txt_ana_cover.insert(0, cover)
            self.txt_ana_stego.delete(0, tk.END)
            self.txt_ana_stego.insert(0, res["output_path"])

            messagebox.showinfo("Success", f"Secret file embedded successfully!\nSaved to: {res['output_path']}\nPSNR: {analysis['psnr_db']:.2f} dB")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.txt_embed_log.insert(tk.END, f"Error: {e}\n")

    # extract tab widgets
    def _init_extract_tab(self):
        container = ttk.Frame(self.tab_extract)
        container.pack(fill="both", expand=True)

        left_col = ttk.Frame(container, width=540)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # stego image input
        grp_stego = ttk.LabelFrame(left_col, text=" Step 1: Select Stego Image ", padding=10)
        grp_stego.pack(fill="x", pady=6)

        f1 = ttk.Frame(grp_stego)
        f1.pack(fill="x")
        self.txt_extr_stego = ttk.Entry(f1, font=("Segoe UI", 9))
        self.txt_extr_stego.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(f1, text="Browse Stego...", command=self._browse_extr_stego).pack(side="right")

        # destination directory
        grp_dest = ttk.LabelFrame(left_col, text=" Step 2: Output Destination Folder ", padding=10)
        grp_dest.pack(fill="x", pady=6)

        f2 = ttk.Frame(grp_dest)
        f2.pack(fill="x")
        self.txt_extr_dest = ttk.Entry(f2, font=("Segoe UI", 9))
        self.txt_extr_dest.pack(side="left", fill="x", expand=True, padx=(0, 6))
        default_extr = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "extracted")
        self.txt_extr_dest.insert(0, default_extr)
        ttk.Button(f2, text="Browse Folder...", command=self._browse_extr_dest).pack(side="right")

        # extract button
        btn_extract = tk.Button(
            left_col,
            text="Extract Hidden Secret File",
            font=("Segoe UI", 11, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#219653",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=8,
            command=self._do_extract
        )
        btn_extract.pack(fill="x", pady=12)

        # log
        grp_log = ttk.LabelFrame(left_col, text=" Extraction Results ", padding=6)
        grp_log.pack(fill="both", expand=True)
        self.txt_extr_log = tk.Text(grp_log, height=12, font=("Consolas", 9), wrap="word", bg="#edf2f7")
        self.txt_extr_log.pack(fill="both", expand=True)

        # preview
        right_col = ttk.LabelFrame(container, text=" Stego Image Preview ", padding=8, width=320)
        right_col.pack(side="right", fill="both", padx=(10, 0))
        right_col.pack_propagate(False)

        self.lbl_extr_preview = ttk.Label(right_col, text="No Preview Available\n(Select a stego image)", anchor="center")
        self.lbl_extr_preview.pack(fill="both", expand=True)

    def _browse_extr_stego(self):
        init_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        path = filedialog.askopenfilename(
            initialdir=init_dir if os.path.exists(init_dir) else ".",
            filetypes=[("Images (*.png)", "*.png"), ("All Files", "*.*")]
        )
        if path:
            self.txt_extr_stego.delete(0, tk.END)
            self.txt_extr_stego.insert(0, path)
            self._display_preview(path, self.lbl_extr_preview)

    def _browse_extr_dest(self):
        folder = filedialog.askdirectory(initialdir=os.path.dirname(os.path.abspath(__file__)))
        if folder:
            self.txt_extr_dest.delete(0, tk.END)
            self.txt_extr_dest.insert(0, folder)

    def _do_extract(self):
        # execute extraction
        stego = self.txt_extr_stego.get().strip()
        dest = self.txt_extr_dest.get().strip()

        if not stego or not os.path.exists(stego):
            messagebox.showerror("Error", "Please select a valid stego image.")
            return

        try:
            res = extract_data(stego, output_dir_or_file=dest)
            saved_path = res["saved_path"]
            log_msg = (
                f"=== Secret Data Extracted ===\n"
                f"Stego Image: {stego}\n"
                f"Detected File Type: {res['file_extension']}\n"
                f"Extracted Size: {res['payload_size']:,} bytes\n"
                f"CRC32: {res['crc32']} (Verified)\n"
                f"Saved to: {saved_path}\n"
                f"=============================\n\n"
            )
            self.txt_extr_log.insert(tk.END, log_msg)
            self.txt_extr_log.see(tk.END)

            if messagebox.askyesno(
                "Extracted",
                f"Secret file extracted!\nType: {res['file_extension']}\nSaved to: {saved_path}\n\nOpen output folder?"
            ):
                folder = os.path.dirname(os.path.abspath(saved_path))
                if sys.platform == "win32":
                    os.startfile(folder)
                else:
                    subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.txt_extr_log.insert(tk.END, f"Error: {e}\n")

    # analysis tab widgets
    def _init_analysis_tab(self):
        container = ttk.Frame(self.tab_analysis)
        container.pack(fill="both", expand=True)

        ctl_frame = ttk.Frame(container, padding=6)
        ctl_frame.pack(fill="x")

        ttk.Label(ctl_frame, text="Cover:").grid(row=0, column=0, sticky="w", padx=4)
        self.txt_ana_cover = ttk.Entry(ctl_frame, width=32)
        self.txt_ana_cover.grid(row=0, column=1, padx=4)
        def_cover = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples", "cover.png")
        self.txt_ana_cover.insert(0, def_cover)
        ttk.Button(ctl_frame, text="...", width=3, command=self._browse_ana_cover).grid(row=0, column=2, padx=2)

        ttk.Label(ctl_frame, text="Stego:").grid(row=0, column=3, sticky="w", padx=(10, 4))
        self.txt_ana_stego = ttk.Entry(ctl_frame, width=32)
        self.txt_ana_stego.grid(row=0, column=4, padx=4)
        def_stego = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "stego.png")
        self.txt_ana_stego.insert(0, def_stego)
        ttk.Button(ctl_frame, text="...", width=3, command=self._browse_ana_stego).grid(row=0, column=5, padx=2)

        ttk.Button(
            ctl_frame,
            text="Run Analysis",
            style="Action.TButton",
            command=self._do_analysis
        ).grid(row=0, column=6, padx=(16, 4))

        # KPI cards for metrics
        cards_frame = ttk.Frame(container, padding=4)
        cards_frame.pack(fill="x")

        self.kpi_psnr = self._create_kpi_card(cards_frame, "PSNR (dB)", "-- dB", 0)
        self.kpi_mse = self._create_kpi_card(cards_frame, "MSE", "--", 1)
        self.kpi_ssim = self._create_kpi_card(cards_frame, "SSIM", "--", 2)
        self.kpi_size = self._create_kpi_card(cards_frame, "File Size Change", "-- B (--%)", 3)

        # container for matplotlib plot
        self.plot_container = ttk.Frame(container)
        self.plot_container.pack(fill="both", expand=True, pady=6)
        self.canvas = None

    def _create_kpi_card(self, parent, title, val, col_idx):
        card = tk.Frame(parent, bg="#edf2f7", highlightbackground="#cbd5e0", highlightthickness=1, padx=10, pady=6)
        card.grid(row=0, column=col_idx, sticky="ew", padx=6, pady=2)
        parent.columnconfigure(col_idx, weight=1)

        t_lbl = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#4a5568", bg="#edf2f7")
        t_lbl.pack(anchor="w")

        v_lbl = tk.Label(card, text=val, font=("Segoe UI", 12, "bold"), fg="#1a365d", bg="#edf2f7")
        v_lbl.pack(anchor="w", pady=(2, 0))
        return v_lbl

    def _browse_ana_cover(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp"), ("All", "*.*")])
        if p:
            self.txt_ana_cover.delete(0, tk.END)
            self.txt_ana_cover.insert(0, p)

    def _browse_ana_stego(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png"), ("All", "*.*")])
        if p:
            self.txt_ana_stego.delete(0, tk.END)
            self.txt_ana_stego.insert(0, p)

    def _do_analysis(self):
        # run quality calculation and plot histograms
        cov = self.txt_ana_cover.get().strip()
        stg = self.txt_ana_stego.get().strip()
        if not os.path.exists(cov) or not os.path.exists(stg):
            messagebox.showerror("Error", "Please make sure Cover and Stego image paths are valid.")
            return

        try:
            metrics = analyze_images(cov, stg)

            self.kpi_psnr.config(text=f"{metrics['psnr_db']:.2f} dB", fg="#27ae60" if metrics['psnr_db'] > 50 else "#d69e2e")
            self.kpi_mse.config(text=f"{metrics['mse']:.6f}")
            self.kpi_ssim.config(text=f"{metrics['ssim']:.4f}")
            self.kpi_size.config(
                text=f"{metrics['cover_file_size']:,}B -> {metrics['stego_file_size']:,}B ({metrics['size_delta_bytes']:+,}B)"
            )

            if self.canvas:
                self.canvas.get_tk_widget().destroy()

            fig = plot_histograms(cov, stg)
            fig.set_size_inches(9.0, 4.6)
            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # about tab widgets
    def _init_about_tab(self):
        container = ttk.Frame(self.tab_about, padding=14)
        container.pack(fill="both", expand=True)

        txt_info = tk.Text(container, font=("Segoe UI", 10), wrap="word", bg="#f5f7fa", relief="flat")
        txt_info.pack(fill="both", expand=True)

        about_text = """
UniKL MIIT - Cryptography and Steganography (IKB 21303)
Assignment 2: Image Steganography Tool

Group Members:
1. AHMAD DANIAL HAZIQ BIN IBRAHIM - 52215125773
2. ADAM HAZIQ BIN DANIANTO - 52212125275
3. ALIA MARDHIAH BINTI OSMERA - 52215251640
4. AHMAD AZFAR BIN MOHMMAD - 52215125999

Overview:
This application implements Least Significant Bit (LSB) image steganography.
It allows users to hide secret files inside a cover image and extract them later.

Supported Secret File Formats:
- Text files (.txt)
- Document files (.pdf, .doc)
- Image files (.png, .jpg)

Features:
1. Embedding: Hides secret files into 24-bit PNG images using 1-bit LSB substitution.
2. Extraction: Automatically detects file extensions and verifies data integrity with CRC32.
3. Analysis: Computes MSE, PSNR, SSIM, and plots comparative RGB channel histograms.
4. File Size Comparison: Evaluates disk size differences before and after embedding.
"""
        txt_info.insert(tk.END, about_text.strip())
        txt_info.config(state="disabled")


def launch_gui():
    app = StegoApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
