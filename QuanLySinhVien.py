import re
import os
import pyodbc
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

DB_CONFIG = {
    "driver": "{SQL Server}",
    "server": "DESKTOP-C87DFH5\\SQLEXPRESS",
    "database": "QuanLy_SinhVien",
    "trusted": True
}

def kiem_tra_email(email):
    if not email:
        return True
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def kiem_tra_sdt(phone):
    if not phone:
        return True
    return re.match(r"^[0-9]{7,15}$", phone) is not None

def lay_ket_noi():
    try:
        if DB_CONFIG.get("trusted", True):
            conn_str = (
                f"DRIVER={DB_CONFIG['driver']};"
                f"SERVER={DB_CONFIG['server']};"
                f"DATABASE={DB_CONFIG['database']};"
                "Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={DB_CONFIG['driver']};"
                f"SERVER={DB_CONFIG['server']};"
                f"DATABASE={DB_CONFIG['database']};"
                f"UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']}"
            )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print("Lỗi kết nối SQL Server:", e)
        messagebox.showerror("Lỗi kết nối DB", f"Không thể kết nối SQL Server.\n{e}")
        return None


def lay_all_khoa():
    conn = lay_ket_noi()
    if not conn:
        return []
    try:
        df = pd.read_sql("SELECT makhoa, tenkhoa FROM KHOA", conn)
        conn.close()
        return [(str(r['makhoa']).strip(), r['tenkhoa']) for _, r in df.iterrows()]
    except Exception as e:
        print("Lỗi khi lấy dữ liệu KHOA:", e)
        messagebox.showerror("Lỗi DB", f"Không thể lấy danh sách Khoa.\n{e}")
        conn.close()
        return []


def lay_lop_theo_khoa(makhoa):
    conn = lay_ket_noi()
    if not conn:
        return []

    try:
        if makhoa:
            sql = """
                SELECT DISTINCT L.malop, L.tenlop
                FROM LOP L
                JOIN SINHVIEN S ON L.malop = S.malop
                WHERE S.makhoa = ?
            """
            df = pd.read_sql(sql, conn, params=(makhoa,))
        else:
            df = pd.read_sql("SELECT malop, tenlop FROM LOP", conn)

        if df.empty:
            df = pd.read_sql("SELECT malop, tenlop FROM LOP", conn)

        conn.close()
        return [(str(r['malop']).strip(), r['tenlop']) for _, r in df.iterrows()]
    except Exception as e:
        print("Lỗi khi lấy lớp:", e)
        messagebox.showerror("Lỗi DB", f"Không thể lấy danh sách lớp.\n{e}")
        conn.close()
        return []

def lay_cac_trangthai():
    """Lấy danh sách các trạng thái hiện có trong SINHVIEN (distinct)."""
    conn = lay_ket_noi()
    if not conn:
        return []
    try:
        df = pd.read_sql("SELECT DISTINCT trangthai FROM SINHVIEN WHERE trangthai IS NOT NULL", conn)
        conn.close()
        return [str(r['trangthai']) for _, r in df.iterrows() if r['trangthai'] is not None]
    except Exception as e:
        print("Lỗi khi lấy trạng thái:", e)
        conn.close()
        return []

class FormSinhVien(simpledialog.Dialog):
    def __init__(self, parent, title=None, initial=None):
        self.initial = initial
        super().__init__(parent, title=title)
    
    def body(self, master):
        master.configure(bg="#F4E9CD")
        labels = [
            ("Mã SV", "maSV"), ("Họ tên", "hotenSV"), ("Ngày sinh (YYYY-MM-DD)", "ngaysinh"),
            ("Địa chỉ", "diachi"), ("CCCD", "cccd"),
            ("SĐT cá nhân", "sdt_canhan"), ("SĐT người thân", "sdt_ngthan"), ("Email", "email"),
            ("Trạng thái", "trangthai")
        ]
        self.entries = {}
        r = 0
        for text, key in labels:
            tk.Label(master, text=text, bg="#F4E9CD", anchor="w").grid(row=r, column=0, sticky="w", padx=6, pady=4)
            entry = tk.Entry(master, width=40)
            entry.grid(row=r, column=1, padx=6, pady=4)
            self.entries[key] = entry
            r += 1
        tk.Label(master, text="Giới tính", bg="#F4E9CD", anchor="w").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.gender_var = tk.StringVar(value="")
        fr = tk.Frame(master, bg="#F4E9CD")
        fr.grid(row=r, column=1, sticky="w")
        tk.Radiobutton(fr, text="Nam", variable=self.gender_var, value="Nam", bg="#F4E9CD").pack(side="left", padx=6)
        tk.Radiobutton(fr, text="Nữ", variable=self.gender_var, value="Nữ", bg="#F4E9CD").pack(side="left", padx=6)
        r += 1
        tk.Label(master, text="Mã khoa", bg="#F4E9CD", anchor="w").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.khoa_cb = ttk.Combobox(master, width=37, state="readonly")
        self.khoa_cb.grid(row=r, column=1, padx=6, pady=4)
        r += 1
        tk.Label(master, text="Mã lớp", bg="#F4E9CD", anchor="w").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.lop_cb = ttk.Combobox(master, width=37, state="readonly")
        self.lop_cb.grid(row=r, column=1, padx=6, pady=4)
        r += 1
        khoa_list = lay_all_khoa()
        self.khoa_map = {f"{m} - {t}": m for m, t in khoa_list}
        self.khoa_cb['values'] = list(self.khoa_map.keys())

        def xu_ly_chon_khoa(event=None):
            sel = self.khoa_cb.get()
            makhoa = self.khoa_map.get(sel)
            if makhoa:
                classes = lay_lop_theo_khoa(makhoa)
                if classes:
                    self.lop_map = {f"{m} - {t}": m for m, t in classes}
                    self.lop_cb['values'] = list(self.lop_map.keys())
                else:
                    self.lop_map = {}
                    self.lop_cb['values'] = []
            else:
                self.lop_map = {}
                self.lop_cb['values'] = []

        self.khoa_cb.bind("<<ComboboxSelected>>", xu_ly_chon_khoa)

        if self.initial:
            for k, v in self.initial.items():
                if k in self.entries and v is not None:
                    self.entries[k].insert(0, str(v))
            if self.initial.get("gioitinh"):
                self.gender_var.set(self.initial.get("gioitinh"))
            if self.initial.get("makhoa"):
                mak = self.initial.get("makhoa")
                for display, code in self.khoa_map.items():
                    if code == mak:
                        self.khoa_cb.set(display)
                        xu_ly_chon_khoa()
                        break
                if self.initial.get("malop") and hasattr(self, "lop_map"):
                    for ldisp, lcode in getattr(self, "lop_map").items():
                        if lcode == self.initial.get("malop"):
                            self.lop_cb.set(ldisp)
                            break
            else:
                if self.initial.get("malop"):
                    classes_all = lay_lop_theo_khoa("")
                    amap = {f"{m} - {t}": m for m, t in classes_all}
                    for kkey, v in amap.items():
                        if v == self.initial.get("malop"):
                            self.lop_cb['values'] = list(amap.keys())
                            self.lop_cb.set(kkey)
                            break

        return self.entries.get("maSV")

    def validate(self):
        data = {k: e.get().strip() for k,e in self.entries.items()}
        data['gioitinh'] = self.gender_var.get()
        makhoa_sel = self.khoa_cb.get()
        malop_sel = self.lop_cb.get()
        data['makhoa'] = self.khoa_map.get(makhoa_sel) if makhoa_sel else None
        data['malop'] = getattr(self, "lop_map", {}).get(malop_sel) if malop_sel else None

        if not data["maSV"]:
            messagebox.showwarning("Thiếu thông tin", "Mã SV không được để trống.")
            return False
        if not data["hotenSV"]:
            messagebox.showwarning("Thiếu thông tin", "Họ tên không được để trống.")
            return False
        if data["email"] and not kiem_tra_email(data["email"]):
            messagebox.showwarning("Sai định dạng", "Email không hợp lệ.")
            return False
        if data["sdt_canhan"] and not kiem_tra_sdt(data["sdt_canhan"]):
            messagebox.showwarning("Sai định dạng", "SĐT cá nhân chỉ gồm 7-15 chữ số.")
            return False
        if data["ngaysinh"]:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", data["ngaysinh"]):
                messagebox.showwarning("Sai định dạng", "Ngày sinh phải dạng YYYY-MM-DD hoặc để trống.")
                return False
        self.result = data
        return True
    
class UngDung:
    def __init__(self, root):
        self.root = root
        root.title("Quản lý sinh viên - Đăng nhập")
        root.geometry("380x260")
        root.configure(bg="#F4E9CD")
        # Login UI
        tk.Label(root, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 16, "bold"), bg="#F4E9CD", fg="#8C5E3C").pack(pady=10)
        frm = tk.Frame(root, bg="#F4E9CD")
        frm.pack(pady=10)
        tk.Label(frm, text="Username:", bg="#F4E9CD").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.ent_user = tk.Entry(frm)
        self.ent_user.grid(row=0, column=1, padx=6, pady=6)
        tk.Label(frm, text="Password:", bg="#F4E9CD").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.ent_pass = tk.Entry(frm, show="*")
        self.ent_pass.grid(row=1, column=1, padx=6, pady=6)
        btn = tk.Button(root, text="Login", bg="#C68B59", fg="white", width=12, command=self.dang_nhap)
        btn.pack(pady=12)
        tk.Label(root, text="(Demo account: admin / 123)", bg="#F4E9CD", font=("Arial", 8)).pack(pady=2)

    def dang_nhap(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if u == "admin" and p == "123":
            self.mo_cua_so_chinh()
        else:
            messagebox.showerror("Đăng nhập thất bại", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def mo_cua_so_chinh(self):
        self.root.withdraw()
        self.main = tk.Toplevel()
        self.main.title("Quản lý sinh viên")
        self.main.geometry("1100x650")

        self.main.configure(bg="#FFF7EB")
        self.xay_dung_giao_dien_chinh(self.main)

        self.main.update_idletasks()
        w = root.winfo_width()
        h = root.winfo_height()

        sw = root.winfo_screenmmwidth()
        sh = root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    def xay_dung_giao_dien_chinh(self, win):
        hdr = tk.Frame(win, bg="#FFF7EB")
        hdr.pack(fill="x")
        tk.Label(hdr, text="QUẢN LÝ SINH VIÊN", font=("Arial", 20, "bold"), bg="#FFF7EB", fg="#8C5E3C").pack(pady=12)

        sf = tk.Frame(win, bg="#FFF7EB")
        sf.pack(pady=6)
        tk.Label(sf, text="Tìm kiếm:", bg="#FFF7EB").pack(side="left", padx=6)
        self.search_var = tk.StringVar()
        ent_search = tk.Entry(sf, textvariable=self.search_var)
        ent_search.pack(side="left", padx=6)
        tk.Button(sf, text="Tìm", bg="#C68B59", fg="white", command=self.tim_kiem).pack(side="left", padx=6)
        tk.Button(sf, text="Làm mới", bg="#C68B59", fg="white", command=lambda: self.tai_du_lieu()).pack(side="left", padx=6)

        tk.Label(sf, text="   Sắp xếp theo:", bg="#FFF7EB").pack(side="left", padx=6)
        self.sort_cb = ttk.Combobox(sf, values=["Mặc định", "Khoa", "Lớp", "Tên (chữ cái đầu của tên)"], state="readonly", width=28)
        self.sort_cb.current(0)
        self.sort_cb.pack(side="left", padx=6)
        tk.Button(sf, text="Áp dụng", bg="#C68B59", fg="white", command=self.ap_dung_sap_xep).pack(side="left", padx=6)

        filter_frame = tk.Frame(win, bg="#FFF7EB")
        filter_frame.pack(fill="x", padx=12, pady=6)

        tk.Label(filter_frame, text="Lọc theo Khoa:", bg="#FFF7EB").grid(row=0, column=0, sticky="w", padx=6)
        self.filter_khoa_cb = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.filter_khoa_cb.grid(row=0, column=1, padx=6)

        tk.Label(filter_frame, text="Lọc theo Lớp:", bg="#FFF7EB").grid(row=0, column=2, sticky="w", padx=6)
        self.filter_lop_cb = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.filter_lop_cb.grid(row=0, column=3, padx=6)

        tk.Label(filter_frame, text="Lọc theo Trạng thái:", bg="#FFF7EB").grid(row=0, column=4, sticky="w", padx=6)
        self.filter_trangthai_cb = ttk.Combobox(filter_frame, state="readonly", width=25)
        self.filter_trangthai_cb.grid(row=0, column=5, padx=6)

        tk.Button(filter_frame, text="Lọc", bg="#C68B59", fg="white", command=self.ap_dung_loc).grid(row=0, column=6, padx=6)
        tk.Button(filter_frame, text="Xóa lọc", bg="#E05D5D", fg="white", command=self.xoa_loc).grid(row=0, column=7, padx=6)

        khoa_list = lay_all_khoa()
        self.filter_khoa_map = {f"{m} - {t}": m for m, t in khoa_list}
        self.filter_khoa_cb['values'] = [""] + list(self.filter_khoa_map.keys())  # allow empty selection
        self.filter_khoa_cb.set("")

        classes_all = lay_lop_theo_khoa("")
        self.filter_lop_map = {f"{m} - {t}": m for m, t in classes_all}
        self.filter_lop_cb['values'] = [""] + list(self.filter_lop_map.keys())
        self.filter_lop_cb.set("")

        statuses = lay_cac_trangthai()
        self.filter_trangthai_cb['values'] = [""] + statuses
        self.filter_trangthai_cb.set("")

        def xu_ly_chon_khoa_filter(event=None):
            sel = self.filter_khoa_cb.get()
            makhoa = self.filter_khoa_map.get(sel)
            if makhoa:
                classes = lay_lop_theo_khoa(makhoa)
                self.filter_lop_map = {f"{m} - {t}": m for m, t in classes}
                self.filter_lop_cb['values'] = [""] + list(self.filter_lop_map.keys())
                self.filter_lop_cb.set("")
            else:
                classes_all2 = lay_lop_theo_khoa("")
                self.filter_lop_map = {f"{m} - {t}": m for m, t in classes_all2}
                self.filter_lop_cb['values'] = [""] + list(self.filter_lop_map.keys())
                self.filter_lop_cb.set("")

        self.filter_khoa_cb.bind("<<ComboboxSelected>>", xu_ly_chon_khoa_filter)

        tbl_frame = tk.Frame(win, bg="#FFF7EB")
        tbl_frame.pack(fill="both", expand=True, padx=12, pady=8)
        self.cols = ("maSV","hotenSV","ngaysinh","gioitinh","diachi","cccd","sdt_canhan","sdt_ngthan","email","trangthai","malop","makhoa")
        self.tree = ttk.Treeview(tbl_frame, columns=self.cols, show="headings")
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        headings = {
            "maSV":"Mã SV","hotenSV":"Họ tên","ngaysinh":"Ngày sinh","gioitinh":"Giới tính","diachi":"Địa chỉ",
            "cccd":"CCCD","sdt_canhan":"SĐT cá nhân","sdt_ngthan":"SĐT người thân","email":"Email","trangthai":"Trạng thái",
            "malop":"Mã lớp","makhoa":"Mã khoa"
        }
        for k in self.cols:
            self.tree.heading(k, text=headings[k])
            if k in ("diachi","email"):
                self.tree.column(k, width=200)
            elif k == "hotenSV":
                self.tree.column(k, width=180)
            else:
                self.tree.column(k, width=110)

        btn_frame = tk.Frame(win, bg="#FFF7EB")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Thêm", width=12, bg="#C68B59", fg="white", command=self.them_sv).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Sửa", width=12, bg="#C68B59", fg="white", command=self.sua_sv).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="Xóa", width=12, bg="#C68B59", fg="white", command=self.xoa_sv).grid(row=0, column=2, padx=8)
        tk.Button(btn_frame, text="Xuất Excel", width=12, bg="#C68B59", fg="white", command=self.xuat_excel_sv).grid(row=0, column=3, padx=8)
        tk.Button(btn_frame, text="Đăng xuất", width=12, bg="#E05D5D", fg="white", command=self.dang_xuat).grid(row=0, column=4, padx=8)
        tk.Button(btn_frame, text="Thoát", width=12, bg="#C68B59", fg="white", command=self.thoat).grid(row=0, column=5, padx=8)

        self.tai_du_lieu()

    def tai_du_lieu(self, order_by=None, filters: dict = None):
        try:
            conn = lay_ket_noi()
            sql = "SELECT * FROM SINHVIEN"
            params = []
            where_clauses = []
            if filters:
                if filters.get("makhoa"):
                    where_clauses.append("makhoa = ?")
                    params.append(filters["makhoa"])
                if filters.get("malop"):
                    where_clauses.append("malop = ?")
                    params.append(filters["malop"])
                if filters.get("trangthai"):
                    where_clauses.append("trangthai = ?")
                    params.append(filters["trangthai"])
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            if order_by == "Khoa":
                sql += " ORDER BY makhoa"
            elif order_by == "Lop":
                sql += " ORDER BY malop"
            elif order_by == "HotenInitial":
                sql += (" ORDER BY CASE WHEN CHARINDEX(' ', REVERSE(hotenSV)) = 0 "
                        "THEN LEFT(hotenSV,1) "
                        "ELSE LEFT(RIGHT(hotenSV, CHARINDEX(' ', REVERSE(hotenSV)) - 1),1) END, hotenSV")
            df = pd.read_sql(sql, conn, params=tuple(params) if params else None)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi kết nối DB", f"Không thể truy vấn database.\nLỗi: {e}")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        cols = list(self.cols)
        for _, row in df.iterrows():
            vals = [row.get(c) for c in cols]
            self.tree.insert("", "end", values=vals)

    def tim_kiem(self):
        key = self.search_var.get().strip()
        if not key:
            self.tai_du_lieu()
            return
        try:
            conn = lay_ket_noi()
            sql = "SELECT * FROM SINHVIEN WHERE gioitinh LIKE ?"
            df = pd.read_sql(sql, conn, params=(f"%{key}%",))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tìm: {e}")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=[row.get(c) for c in df.columns])

    def them_sv(self):
        form = FormSinhVien(self.main, title="Thêm sinh viên")
        if not getattr(form, "result", None):
            return
        data = form.result
        try:
            conn = lay_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO SINHVIEN (maSV, hotenSV, ngaysinh, gioitinh, diachi, cccd, sdt_canhan, sdt_ngthan, email, trangthai, malop, makhoa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data["maSV"], data["hotenSV"], data["ngaysinh"] or None, data["gioitinh"] or None, data["diachi"] or None,
                 data["cccd"] or None, data["sdt_canhan"] or None, data["sdt_ngthan"] or None, data["email"] or None,
                 data["trangthai"] or None, data["malop"] or None, data["makhoa"] or None)
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã thêm sinh viên.")
            self.ap_dung_sap_xep()
        except pyodbc.IntegrityError as e:
            messagebox.showerror("Lỗi", f"Trùng khóa hoặc ràng buộc: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm: {e}")

    def sua_sv(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Chọn dòng", "Hãy chọn sinh viên để sửa.")
            return
        vals = self.tree.item(sel)["values"]
        cols = ("maSV","hotenSV","ngaysinh","gioitinh","diachi","cccd","sdt_canhan","sdt_ngthan","email","trangthai","malop","makhoa")
        initial = {k: (vals[i] if i < len(vals) else "") for i,k in enumerate(cols)}
        form = FormSinhVien(self.main, title="Sửa sinh viên", initial=initial)
        if not getattr(form, "result", None):
            return
        data = form.result
        try:
            conn = lay_ket_noi()
            cur = conn.cursor()
            cur.execute("""
                UPDATE SINHVIEN SET
                    hotenSV=?, ngaysinh=?, gioitinh=?, diachi=?, cccd=?, sdt_canhan=?, sdt_ngthan=?, email=?, trangthai=?, malop=?, makhoa=?
                WHERE maSV=?
            """, data["hotenSV"], data["ngaysinh"] or None, data["gioitinh"] or None, data["diachi"] or None,
                 data["cccd"] or None, data["sdt_canhan"] or None, data["sdt_ngthan"] or None, data["email"] or None,
                 data["trangthai"] or None, data["malop"] or None, data["makhoa"] or None, data["maSV"])
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã cập nhật sinh viên.")
            self.ap_dung_sap_xep()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")

    def xoa_sv(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Chọn dòng", "Hãy chọn sinh viên để xóa.")
            return
        vals = self.tree.item(sel)["values"]
        ma = vals[0]
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sinh viên {ma}?"):
            return
        try:
            conn = lay_ket_noi()
            cur = conn.cursor()
            cur.execute("DELETE FROM SINHVIEN WHERE maSV=?", ma)
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã xóa.")
            self.ap_dung_sap_xep()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa: {e}")

    def xuat_excel_sv(self):
        try:
            conn = lay_ket_noi()
            df = pd.read_sql("SELECT * FROM SINHVIEN", conn)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy dữ liệu để xuất: {e}")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel file", "*.xlsx")], initialfile="DanhSachSinhVien.xlsx")
        if not fpath:
            return
        try:
            df.to_excel(fpath, index=False)
            messagebox.showinfo("Xuất thành công", f"Đã lưu file: {fpath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def ap_dung_sap_xep(self):
        sc = self.sort_cb.get()
        if sc == "Khoa":
            self.tai_du_lieu(order_by="Khoa", filters=self._lay_loc_hien_tai())
        elif sc == "Lớp":
            self.tai_du_lieu(order_by="Lop", filters=self._lay_loc_hien_tai())
        elif sc == "Tên (chữ cái đầu của tên)":
            self.tai_du_lieu(order_by="HotenInitial", filters=self._lay_loc_hien_tai())
        else:
            self.tai_du_lieu(filters=self._lay_loc_hien_tai())

    def _lay_loc_hien_tai(self):
        f = {}
        ksel = self.filter_khoa_cb.get()
        lsel = self.filter_lop_cb.get()
        tsel = self.filter_trangthai_cb.get()
        if ksel:
            f['makhoa'] = self.filter_khoa_map.get(ksel)
        if lsel:
            f['malop'] = self.filter_lop_map.get(lsel)
        if tsel:
            f['trangthai'] = tsel
        return f

    def ap_dung_loc(self):
        filters = self._lay_loc_hien_tai()
        self.tai_du_lieu(filters=filters)

    def xoa_loc(self):
        self.filter_khoa_cb.set("")
        classes_all = lay_lop_theo_khoa("")
        self.filter_lop_map = {f"{m} - {t}": m for m, t in classes_all}
        self.filter_lop_cb['values'] = [""] + list(self.filter_lop_map.keys())
        self.filter_lop_cb.set("")
        self.filter_trangthai_cb.set("")
        self.tai_du_lieu()

    def dang_xuat(self):
        try:
            self.main.destroy()
        except Exception:
            pass
        self.root.deiconify()
        self.ent_user.delete(0, tk.END)
        self.ent_pass.delete(0, tk.END)
        self.ent_user.focus_set()

    def thoat(self):
        try:
            self.main.destroy()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UngDung(root)
    root.mainloop()
