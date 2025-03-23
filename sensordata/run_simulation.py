#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import signal
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ICSSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ICS Facility Control")
        self.root.geometry("600x400")
        
        # Style
        style = ttk.Style()
        style.configure('Attack.TButton', background='red')
        style.configure('Emergency.TButton', background='red', foreground='white')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status label
        self.status_var = tk.StringVar(value="Facility Status: Offline")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                    font=('Helvetica', 12, 'bold'))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Start button
        self.start_btn = ttk.Button(main_frame, text="Start Uranium Enrichment Facility", 
                                  command=self.start_facility,
                                  style='TButton')
        self.start_btn.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
        
        # Attack button (initially disabled)
        self.attack_btn = ttk.Button(main_frame, text="Simulate Cyber Attack", 
                                   command=self.start_attack,
                                   style='Attack.TButton',
                                   state='disabled')
        self.attack_btn.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
        
        # Stop button (initially disabled)
        self.stop_btn = ttk.Button(main_frame, text="EMERGENCY STOP", 
                                 command=self.stop_facility,
                                 style='Emergency.TButton',
                                 state='disabled')
        self.stop_btn.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
        
        # Output display
        self.output_frame = ttk.LabelFrame(main_frame, text="System Alerts", padding="10")
        self.output_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='nsew')
        
        self.output_text = tk.Text(self.output_frame, height=10, width=60)
        self.output_text.pack(expand=True, fill='both')
        
        # Scrollbar for output
        scrollbar = ttk.Scrollbar(self.output_frame, orient='vertical', 
                                command=self.output_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Process tracking
        self.normal_sim = None
        self.attack_sim = None
        self.is_running = False
        self.under_attack = False
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_output(self, message, level="INFO"):
        """Add message to output text widget with timestamp"""
        self.output_text.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        
        if level == "WARNING":
            tag = "warning"
            prefix = "WARNING"
        elif level == "ERROR":
            tag = "error"
            prefix = "ERROR"
        else:
            tag = "info"
            prefix = "INFO"
        
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("info", foreground="green")
        
        self.output_text.insert('end', f"[{timestamp}] {prefix}: {message}\n", tag)
        self.output_text.see('end')
        self.output_text.config(state='disabled')

    def check_port(self, port):
        """Check if a port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def start_facility(self):
        """Start the normal ICS simulation"""
        if self.check_port(8000):
            messagebox.showerror("Error", "Port 8000 is already in use!")
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Start normal metrics simulation
            self.normal_sim = subprocess.Popen(
                [sys.executable, os.path.join(script_dir, 'ics_metrics.py')],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.is_running = True
            self.status_var.set("Facility Status: ONLINE")
            self.start_btn.config(state='disabled')
            self.attack_btn.config(state='normal')
            self.stop_btn.config(state='normal')
            
            # Start output monitoring thread
            threading.Thread(target=self.monitor_output, daemon=True).start()
            
            self.log_output("Facility started - Systems operational", "INFO")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start facility: {str(e)}")
            logger.error(f"Startup error: {str(e)}")

    def start_attack(self):
        """Start the attack simulation"""
        if self.check_port(8001):
            messagebox.showerror("Error", "Port 8001 is already in use!")
            return
        
        if not self.is_running:
            messagebox.showerror("Error", "Facility must be running to simulate attack!")
            return
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Start attack simulation
            self.attack_sim = subprocess.Popen(
                [sys.executable, os.path.join(script_dir, 'ics_attack_simulation.py')],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.under_attack = True
            self.attack_btn.config(state='disabled')
            self.status_var.set("Facility Status: UNDER ATTACK")
            self.log_output("CYBER ATTACK DETECTED!", "WARNING")
            
            # Start attack output monitoring thread
            threading.Thread(target=self.monitor_attack_output, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start attack simulation: {str(e)}")
            logger.error(f"Attack simulation error: {str(e)}")

    def stop_facility(self):
        """Stop all simulations"""
        self.is_running = False
        self.under_attack = False
        
        # Stop processes
        for process in [self.normal_sim, self.attack_sim]:
            if process and process.poll() is None:
                if sys.platform == 'win32':
                    process.send_signal(signal.CTRL_C_EVENT)
                else:
                    process.terminate()
                process.wait()
        
        # Reset GUI
        self.status_var.set("Facility Status: OFFLINE")
        self.start_btn.config(state='normal')
        self.attack_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        
        self.log_output("Emergency stop initiated - All systems offline", "WARNING")

    def monitor_output(self):
        """Monitor and display normal simulation output"""
        while self.is_running and self.normal_sim and self.normal_sim.poll() is None:
            output = self.normal_sim.stdout.readline()
            if output:
                if "ANOMALY DETECTED" in output:
                    self.log_output(output.strip(), "WARNING")
                elif "ERROR" in output.upper():
                    self.log_output(output.strip(), "ERROR")
                elif "WARNING" in output.upper():
                    self.log_output(output.strip(), "WARNING")

    def monitor_attack_output(self):
        """Monitor and display attack simulation output"""
        while self.under_attack and self.attack_sim and self.attack_sim.poll() is None:
            output = self.attack_sim.stdout.readline()
            if output:
                if "CRITICAL" in output or "ATTACK" in output:
                    self.log_output(output.strip(), "WARNING")
                elif "ERROR" in output.upper():
                    self.log_output(output.strip(), "ERROR")
                elif "ANOMALY" in output:
                    self.log_output(output.strip(), "WARNING")

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_facility()
            self.root.destroy()

def main():
    root = tk.Tk()
    gui = ICSSimulationGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
