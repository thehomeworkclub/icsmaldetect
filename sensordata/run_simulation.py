#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import signal

def check_port(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_simulations():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if ports are available
    if check_port(8000):
        print("Error: Port 8000 is already in use!")
        return
    if check_port(8001):
        print("Error: Port 8001 is already in use!")
        return
    
    try:
        # Start normal metrics simulation
        print("Starting normal ICS metrics simulation...")
        normal_sim = subprocess.Popen([sys.executable, os.path.join(script_dir, 'ics_metrics.py')],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    bufsize=1)
        
        # Give the first simulation a moment to start
        time.sleep(1)
        
        # Start attack simulation
        print("Starting attack simulation...")
        attack_sim = subprocess.Popen([sys.executable, os.path.join(script_dir, 'ics_attack_simulation.py')],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    bufsize=1)
        
        print("\nSimulations are running!")
        print("Normal metrics available at: http://localhost:8000")
        print("Attack simulation metrics available at: http://localhost:8001")
        print("\nPress Ctrl+C to stop the simulations...")
        
        # Keep the script running and monitor subprocess outputs
        while True:
            # Check normal simulation output
            normal_out = normal_sim.stdout.readline()
            normal_err = normal_sim.stderr.readline()
            if normal_out:
                print("Normal sim:", normal_out.strip())
            if normal_err:
                print("Normal sim error:", normal_err.strip())
            
            # Check attack simulation output
            attack_out = attack_sim.stdout.readline()
            attack_err = attack_sim.stderr.readline()
            if attack_out:
                print("Attack sim:", attack_out.strip())
            if attack_err:
                print("Attack sim error:", attack_err.strip())
            
            # Check if either process has terminated
            if normal_sim.poll() is not None:
                print(f"Normal simulation terminated with exit code: {normal_sim.returncode}")
                # Capture any remaining error output
                remaining_err = normal_sim.stderr.read()
                if remaining_err:
                    print("Normal sim final error:", remaining_err.strip())
                break
            
            if attack_sim.poll() is not None:
                print(f"Attack simulation terminated with exit code: {attack_sim.returncode}")
                # Capture any remaining error output
                remaining_err = attack_sim.stderr.read()
                if remaining_err:
                    print("Attack sim final error:", remaining_err.strip())
                break
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping simulations...")
        
    finally:
        # Ensure both processes are terminated
        for process in [normal_sim, attack_sim]:
            if process.poll() is None:  # If process is still running
                if sys.platform == 'win32':
                    process.send_signal(signal.CTRL_C_EVENT)
                else:
                    process.terminate()
                process.wait()
        
        print("Simulations stopped.")

if __name__ == '__main__':
    run_simulations()
