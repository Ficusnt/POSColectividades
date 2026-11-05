import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POS - Colectividades")
        self.root.geometry("1200x800")
        
        # Paths
        self.PRODUCTS_FILE = "ColectividadesPos/data/products.csv"
        self.SALES_FILE = "ColectividadesPos/data/sales.csv"
        
        # State
        self.products = []
        self.current_ticket = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Fonts
        self.font_main = ("Arial", 14)
        self.font_bold = ("Arial", 16, "bold")
        self.font_header = ("Arial", 20, "bold")
        self.font_total = ("Arial", 28, "bold")

        self.load_products()
        self.configure_ui()
        self.populate_product_list()

    def load_products(self):
        self.products = []
        if not os.path.exists(self.PRODUCTS_FILE):
            os.makedirs(os.path.dirname(self.PRODUCTS_FILE), exist_ok=True)
            with open(self.PRODUCTS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id", "nombre", "precio"])
            return

        try:
            with open(self.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.products.append({
                        "id": row["id"],
                        "nombre": row["nombre"],
                        "precio": float(row["precio"])
                    })
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")

    def save_products(self):
        try:
            with open(self.PRODUCTS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["id", "nombre", "precio"])
                writer.writeheader()
                writer.writerows(self.products)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el catálogo: {e}")

    def configure_ui(self):
        # Global Style
        self.style = ttk.Style()
        self.style.configure("TButton", font=self.font_main, padding=10)
        self.style.configure("TLabel", font=self.font_main)
        self.style.configure("Header.TLabel", font=self.font_header)
        self.style.configure("Accent.TButton", font=self.font_bold, foreground="green")
        self.style.configure("Report.TButton", font=self.font_main, foreground="blue")

        # Main Container
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # --- LEFT PANEL: Product Catalog ---
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        ttk.Label(self.left_panel, text="Productos", style="Header.TLabel").pack(pady=(0, 10))
        
        # Relocated Catalog Buttons
        catalog_btn_frame = ttk.Frame(self.left_panel)
        catalog_btn_frame.pack(pady=(0, 10), fill=tk.X)
        
        ttk.Button(catalog_btn_frame, text="➕ Agregar Item", command=self.show_add_product_dialog).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(catalog_btn_frame, text="🗑️ Eliminar Item", command=self.delete_selected_product).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Increased size of product list
        self.product_list = tk.Listbox(
            self.left_panel, 
            font=self.font_main, 
            width=45, 
            height=30, 
            selectmode=tk.SINGLE
        )
        self.product_list.pack(side=tk.TOP, fill=tk.Y)
        self.product_list.bind('<Double-1>', lambda e: self.add_to_ticket())

        # --- RIGHT PANEL: Current Ticket ---
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        ttk.Label(self.right_panel, text="Ticket Actual", style="Header.TLabel").pack(pady=(0, 10))

        # Ticket Table
        columns = ("nombre", "cantidad", "precio", "subtotal")
        self.ticket_tree = ttk.Treeview(self.right_panel, columns=columns, show="headings")
        self.ticket_tree.heading("nombre", text="Producto")
        self.ticket_tree.heading("cantidad", text="Cant.")
        self.ticket_tree.heading("precio", text="Precio Unit.")
        self.ticket_tree.heading("subtotal", text="Subtotal")
        
        self.ticket_tree.column("nombre", width=300, anchor="w")
        self.ticket_tree.column("cantidad", width=80, anchor="center")
        self.ticket_tree.column("precio", width=120, anchor="e")
        self.ticket_tree.column("subtotal", width=120, anchor="e")
        
        self.style.configure("Treeview", font=self.font_main, rowheight=30)
        self.style.configure("Treeview.Heading", font=self.font_bold)
        
        self.ticket_tree.pack(expand=True, fill=tk.BOTH)
        self.ticket_tree.bind('<Double-1>', lambda e: self.remove_from_ticket())

        # Ticket Controls
        ticket_ctrl_frame = ttk.Frame(self.right_panel)
        ticket_ctrl_frame.pack(pady=15, fill=tk.X)

        ttk.Label(ticket_ctrl_frame, text="Cantidad:").pack(side=tk.LEFT, padx=5)
        self.qty_var = tk.StringVar(value="1")
        self.qty_entry = ttk.Entry(ticket_ctrl_frame, textvariable=self.qty_var, width=8, font=self.font_main)
        self.qty_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(ticket_ctrl_frame, text="➕ Agregar al Ticket", command=self.add_to_ticket).pack(side=tk.LEFT, padx=10)
        ttk.Button(ticket_ctrl_frame, text="❌ Quitar Item", command=self.remove_from_ticket).pack(side=tk.LEFT, padx=5)

        # Total and Checkout
        self.total_var = tk.StringVar(value="Total: $0")
        self.total_label = ttk.Label(self.right_panel, textvariable=self.total_var, font=self.font_total)
        self.total_label.pack(pady=20, anchor="e")

        # Bottom Action Buttons
        action_frame = ttk.Frame(self.right_panel)
        action_frame.pack(pady=10, anchor="e")

        ttk.Button(action_frame, text="📊 Cierre de Caja", command=self.show_sales_report, style="Report.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="💰 FINALIZAR VENTA", command=self.checkout, style="Accent.TButton").pack(side=tk.LEFT, padx=10)

    def populate_product_list(self):
        self.product_list.delete(0, tk.END)
        for p in self.products:
            self.product_list.insert(tk.END, f"{p['nombre']} - ${p['precio']:,.0f}")

    def show_add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Producto")
        dialog.geometry("400x300")
        dialog.grab_set()

        main_d = ttk.Frame(dialog, padding=20)
        main_d.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_d, text="Nombre:", font=self.font_main).pack(pady=(10, 0))
        name_entry = ttk.Entry(main_d, font=self.font_main)
        name_entry.pack(pady=5, fill=tk.X)

        ttk.Label(main_d, text="Precio:", font=self.font_main).pack(pady=(10, 0))
        price_entry = ttk.Entry(main_d, font=self.font_main)
        price_entry.pack(pady=5, fill=tk.X)

        def save():
            name = name_entry.get().strip()
            price_str = price_entry.get().strip()
            try:
                price = float(price_str)
                new_id = str(max([int(p['id']) for p in self.products], default=0) + 1)
                self.products.append({"id": new_id, "nombre": name, "precio": price})
                self.save_products()
                self.populate_product_list()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Precio debe ser un número")

        ttk.Button(main_d, text="Guardar", command=save).pack(pady=30)

    def delete_selected_product(self):
        selection = self.product_list.curselection()
        if not selection:
            return
        
        idx = selection[0]
        prod = self.products[idx]
        if messagebox.askyesno("Confirmar", f"¿Eliminar {prod['nombre']}?"):
            del self.products[idx]
            self.save_products()
            self.populate_product_list()

    def add_to_ticket(self):
        selection = self.product_list.curselection()
        if not selection:
            messagebox.showwarning("Atención", "Seleccioná un producto primero")
            return
        
        try:
            qty = int(self.qty_var.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return

        prod = self.products[selection[0]]
        
        for item in self.current_ticket:
            if item['id'] == prod['id']:
                item['qty'] += qty
                self.update_ticket_ui()
                return

        self.current_ticket.append({
            "id": prod['id'],
            "nombre": prod['nombre'],
            "precio": prod['precio'],
            "qty": qty
        })
        self.update_ticket_ui()

    def remove_from_ticket(self):
        selection = self.ticket_tree.selection()
        if not selection: return
        
        item_values = self.ticket_tree.item(selection[0])['values']
        prod_name = item_values[0]
        
        for i, item in enumerate(self.current_ticket):
            if item['nombre'] == prod_name:
                del self.current_ticket[i]
                break
        self.update_ticket_ui()

    def update_ticket_ui(self):
        for item in self.ticket_tree.get_children():
            self.ticket_tree.delete(item)
        
        total = 0
        for item in self.current_ticket:
            subtotal = item['precio'] * item['qty']
            total += subtotal
            self.ticket_tree.insert("", tk.END, values=(item['nombre'], item['qty'], f"${item['precio']:,.0f}", f"${subtotal:,.0f}"))
        
        self.total_var.set(f"Total: ${total:,.0f}")

    def checkout(self):
        if not self.current_ticket:
            messagebox.showwarning("Atención", "El ticket está vacío")
            return
        
        try:
            with open(self.SALES_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for item in self.current_ticket:
                    subtotal = item['precio'] * item['qty']
                    writer.writerow([now, self.session_id, item['id'], item['qty'], item['precio'], subtotal])
            
            messagebox.showinfo("Éxito", "Venta registrada correctamente")
            self.current_ticket = []
            self.update_ticket_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la venta: {e}")

    def show_sales_report(self):
        if not os.path.exists(self.SALES_FILE):
            messagebox.showinfo("Reporte", "No hay ventas registradas aún.")
            return

        session_total = 0.0
        daily_total = 0.0
        today_str = datetime.now().strftime("%Y-%m-%d")

        try:
            with open(self.SALES_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row: continue
                    # CSV Format: timestamp, session_id, prod_id, qty, price, subtotal
                    # Skip header if exists (heuristic check)
                    if row[0] == "timestamp": continue
                    
                    subtotal = float(row[5])
                    timestamp = row[0]
                    session_id = row[1]

                    if session_id == self.session_id:
                        session_total += subtotal
                    
                    if timestamp.startswith(today_str):
                        daily_total += subtotal

            report_msg = f"Resumen de Ventas:\n\nTotal Sesión: ${session_total:,.0f}\nTotal Hoy: ${daily_total:,.0f}"
            messagebox.showinfo("Cierre de Caja", report_msg)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()
