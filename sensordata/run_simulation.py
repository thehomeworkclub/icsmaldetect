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

class ICSSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ICS Facility Control")
        self.root.geometry("400x300")
        
        # Style
        style = ttk.Style()
        style.configure('Warning.TButton', background='red', foreground='red')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Facility Status: Offline", font=('Helvetica', 12))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Start button
        self.start_btn = ttk.Button(main_frame, text="Start Uranium Enrichment Facility", 
                                  command=self.start_facility)
        self.start_btn.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
        
        # Attack button (initially disabled)
        self.attack_btn = ttk.Button(main_frame, text="Simulate Cyber Attack", 
                                   command=self.start_attack,
                                   style='Warning.TButton',
                                   state='disabled')
        self.attack_btn.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
        
        # Stop button (initially disabled)
        self.stop_btn = ttk.Button(main_frame, text="Emergency Stop", 
                                 command=self.stop_facility,
                                 state='disabled')
        self.stop_btn.grid(row=3, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
        
        # Process tracking
        self.normal_sim = None
        self.attack_sim = None
        self.is_running = False
        self.under_attack = False
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        
        # Set up output display
        self.output_text = tk.Text(main_frame, height=8, width=40)
        self.output_text.grid(row=4, column=0, columnspan=2, pady=10, padx=20)
        self.output_text.config(state='disabled')
        
        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_output(self, message):
        """Add message to output text widget"""
        self.output_text.config(state='normal')
        self.output_text.insert('end', f"{message}\n")
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
            self.status_label.config(text="Facility Status: Online")
            self.start_btn.config(state='disabled')
            self.attack_btn.config(state='normal')
            self.stop_btn.config(state='normal')
            
            # Start output monitoring thread
            threading.Thread(target=self.monitor_output, daemon=True).start()
            
            self.log_output("Facility started - Monitoring metrics...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start facility: {str(e)}")

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
            self.log_output("WARNING: Cyber attack detected!")
            
            # Start attack output monitoring thread
            threading.Thread(target=self.monitor_attack_output, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start attack simulation: {str(e)}")

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
        self.status_label.config(text="Facility Status: Offline")
        self.start_btn.config(state='normal')
        self.attack_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')
        
        self.log_output("Facility stopped.")

    def monitor_output(self):
        """Monitor and display normal simulation output"""
        while self.is_running and self.normal_sim and self.normal_sim.poll() is None:
            output = self.normal_sim.stdout.readline()
            if output:
                if "ANOMALY DETECTED" in output:
                    self.log_output(output.strip())

    def monitor_attack_output(self):
        """Monitor and display attack simulation output"""
        while self.under_attack and self.attack_sim and self.attack_sim.poll() is None:
            output = self.attack_sim.stdout.readline()
            if output:
                if "Attack detected" in output:
                    self.log_output(output.strip())

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
