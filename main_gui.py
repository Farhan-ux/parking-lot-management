import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import parking_lot
import ai_logic
import vehicle
import parking_slot
import datetime
import os

class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Smart Parking Management System")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text='Parking Operations')
        self.notebook.add(self.tab2, text='AI Analytics')
        self.notebook.add(self.tab3, text='Security')
        self.notebook.add(self.tab4, text='System Logs')

        self.setup_operations_tab()
        self.setup_analytics_tab()
        self.setup_security_tab()
        self.setup_logs_tab()

    def setup_operations_tab(self):
        # Park Vehicle Section
        lbl_frame = ttk.LabelFrame(self.tab1, text="Vehicle Entry (Auto-Billing & OCR)")
        lbl_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(lbl_frame, text="Plate Number:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_plate = ttk.Entry(lbl_frame)
        self.entry_plate.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(lbl_frame, text="Scan Plate (OCR)", command=self.scan_plate).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Vehicle Type:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_type = ttk.Combobox(lbl_frame, values=["Normal", "Disabled", "VIP", "Bike"])
        self.combo_type.set("Normal")
        self.combo_type.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(lbl_frame, text="Recommend Slot", command=self.recommend_slot).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Assigned Slot:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_slot = ttk.Entry(lbl_frame)
        self.entry_slot.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(lbl_frame, text="Park Vehicle", command=self.park_vehicle).grid(row=3, column=0, columnspan=3, pady=10)

        # Exit Section
        exit_frame = ttk.LabelFrame(self.tab1, text="Vehicle Exit")
        exit_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(exit_frame, text="Plate Number:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_exit_plate = ttk.Entry(exit_frame)
        self.entry_exit_plate.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(exit_frame, text="Calculate Fee & Exit", command=self.exit_vehicle).grid(row=1, column=0, columnspan=2, pady=10)

    def scan_plate(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            plate = ai_logic.perform_ocr(file_path)
            self.entry_plate.delete(0, tk.END)
            self.entry_plate.insert(0, plate)

            # Auto-check if suspicious
            reason = ai_logic.is_suspicious(plate)
            if reason:
                messagebox.showwarning("Security Alert", f"Vehicle {plate} is blacklisted!\nReason: {reason}")
        else:
            # Simulation
            plate = "SIM-" + str(datetime.datetime.now().microsecond)[:3]
            self.entry_plate.delete(0, tk.END)
            self.entry_plate.insert(0, plate)
            messagebox.showinfo("Simulation", f"Simulated Plate: {plate}")

    def recommend_slot(self):
        v_type = self.combo_type.get()
        slot = ai_logic.recommend_parking_slot(v_type)
        if slot:
            self.entry_slot.delete(0, tk.END)
            self.entry_slot.insert(0, str(slot))
        else:
            messagebox.showwarning("Full", "No available slots!")

    def park_vehicle(self):
        plate = self.entry_plate.get()
        v_type = self.combo_type.get()
        slot = self.entry_slot.get()

        if not plate or not slot:
            messagebox.showerror("Error", "Plate and Slot required")
            return

        res = parking_lot.park_vehicle(plate, v_type, slot)
        if res:
            messagebox.showinfo("Success", f"Vehicle {plate} parked in slot {slot}")
            self.update_logs(f"Parked: {plate} in slot {slot}")

    def exit_vehicle(self):
        plate = self.entry_exit_plate.get()
        if not plate:
            messagebox.showerror("Error", "Plate number required")
            return

        conn = ai_logic.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, entry_time FROM vehicles WHERE plate_number=?", (plate,))
        res = cursor.fetchone()

        if res:
            v_id = res[0]
            entry_time = datetime.datetime.strptime(res[1], '%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            hours = max(1, (now - entry_time).total_seconds() / 3600)

            parking_lot.remove_parked_vehicle(v_id, hours)
            fee = hours * 50
            messagebox.showinfo("Exit", f"Vehicle {plate} removed.\nDuration: {round(hours, 2)} hrs\nTotal Fee: {round(fee, 2)} PKR")
            self.update_logs(f"Exited: {plate}. Duration: {round(hours, 2)} hrs, Fee paid: {round(fee, 2)}")
        else:
            messagebox.showerror("Error", "Vehicle not found")
        conn.close()

    def setup_analytics_tab(self):
        ttk.Button(self.tab2, text="Predict Peak Hours", command=self.show_peak_hours).pack(pady=10)
        self.lbl_peak = ttk.Label(self.tab2, text="Peak Prediction: Pending...")
        self.lbl_peak.pack(pady=5)

        ttk.Button(self.tab2, text="Run Overstay Detection", command=self.check_overstays).pack(pady=10)
        self.text_overstays = tk.Text(self.tab2, height=10, width=50)
        self.text_overstays.pack(pady=5)

        ttk.Button(self.tab2, text="Simulate Fraud/Wrong Parking", command=self.simulate_fraud).pack(pady=10)

    def show_peak_hours(self):
        prediction = ai_logic.predict_peak_hours()
        self.lbl_peak.config(text=f"Peak Prediction: {prediction}")

    def check_overstays(self):
        overstays = ai_logic.detect_overstays(0.01) # Small number for demo
        self.text_overstays.delete(1.0, tk.END)
        if overstays:
            for o in overstays:
                self.text_overstays.insert(tk.END, f"Plate: {o['plate']}, Time: {o['hours']} hrs\n")
        else:
            self.text_overstays.insert(tk.END, "No overstays detected.")

    def simulate_fraud(self):
        violation = ai_logic.detect_wrong_parking()
        if violation:
            messagebox.showwarning("Fraud Detection", f"AI Alert: {violation}")
        else:
            messagebox.showinfo("Clean", "No parking violations detected.")

    def setup_security_tab(self):
        ttk.Label(self.tab3, text="Blacklist Plate:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_bl_plate = ttk.Entry(self.tab3)
        self.entry_bl_plate.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.tab3, text="Reason:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_bl_reason = ttk.Entry(self.tab3)
        self.entry_bl_reason.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.tab3, text="Add to Blacklist", command=self.add_blacklist).grid(row=2, column=0, columnspan=2, pady=10)

    def add_blacklist(self):
        plate = self.entry_bl_plate.get()
        reason = self.entry_bl_reason.get()
        if plate and reason:
            ai_logic.add_to_blacklist(plate, reason)
            messagebox.showinfo("Security", f"Plate {plate} blacklisted.")
        else:
            messagebox.showerror("Error", "Plate and Reason required")

    def setup_logs_tab(self):
        self.log_text = tk.Text(self.tab4, height=20, width=70)
        self.log_text.pack(padx=10, pady=10)

    def update_logs(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
