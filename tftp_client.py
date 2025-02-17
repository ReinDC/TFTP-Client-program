import tkinter as tk
from tkinter import messagebox
import socket
import os

class TftpClient:
    def __init__(self, timeout=5, max_retries=5):
        """
        Class constructor for TftpClient
        
        Args:
            timeout (int): The timeout duration for the client in seconds. Default is 5 seconds.
            max_retries (int): The maximum number of retries for the client. Default is 5 retries.
        """
        self.timeout = timeout
        self.max_retries = max_retries

    @staticmethod
    def get_unique_filename(filename):
        """
        Generates a unique filename by appending a counter in parentheses if the file already exists.

        Args:
            filename (str): The original filename to check/modify

        Returns:
            str: A unique filename that doesn't exist in the current directory. 
        """
        if not os.path.exists(filename):
            return filename
        base, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_name = f"{base}({counter}){ext}"
            if not os.path.exists(new_name):
                return new_name
            counter += 1

    def download(self, server_host, remote_filename, local_filename, blksize=512):
        """
        Download function of the TFTP client
        
        Args:
            server_host (str): The hostname or IP address of the TFTP server
            remote_filename (str): Name of the file to download from the server
            local_filename (str): Path where the downloaded file will be saved locally
            blksize (int, optional): Desired block size for the transfer. Defaults to 512 bytes
        """
        
        local_filename = self.get_unique_filename(local_filename)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        # RRQ with options
        rrq = b'\x00\x01' + remote_filename.encode() + b'\x00octet\x00'
        rrq += f'blksize\x00{blksize}\x00'.encode()
        server_port = 69
        sock.sendto(rrq, (server_host, server_port))

        try:
            file = open(local_filename, 'wb')
        except IOError as e:
            messagebox.showerror("Error", f"Failed to create local file: {e}")
            sock.close()
            return

        expected_block = 1
        retries = self.max_retries
        transfer_addr = None
        success = False

        while True:
            try:
                data, transfer_addr = sock.recvfrom(blksize + 4) 
                opcode = int.from_bytes(data[:2], 'big')
                
                if opcode == 3:  # DATA
                    block_number = int.from_bytes(data[2:4], 'big')
                    file_data = data[4:]
                    
                    if block_number == expected_block:
                        file.write(file_data)
                        ack = b'\x00\x04' + block_number.to_bytes(2, 'big')
                        sock.sendto(ack, transfer_addr)
                        expected_block += 1
                        
                        if len(file_data) < blksize:
                            success = True
                            break
                    elif block_number < expected_block:
                        ack = b'\x00\x04' + block_number.to_bytes(2, 'big')
                        sock.sendto(ack, transfer_addr)
                elif opcode == 5:  # ERROR
                    error_msg = data[4:-1].decode()
                    messagebox.showerror("Server Error", f"Server error: {error_msg}")
                    break
                elif opcode == 6:
                    options = self.parse_oack(data[2:])
                    if 'blksize' in options:
                        blksize = int(options['blksize'])
                    ack = b'\x00\x04\x00\x00'
                    sock.sendto(ack, transfer_addr)
            except socket.timeout:
                retries -= 1
                if retries == 0:
                    messagebox.showerror("Error", "Max retries reached, transfer aborted")
                    break
                
                if expected_block == 1:
                    sock.sendto(rrq, (server_host, server_port))
                else:
                    ack = b'\x00\x04' + (expected_block - 1).to_bytes(2, 'big')
                    sock.sendto(ack, transfer_addr)
                
        file.close()
        sock.close()

        if not success:
            if os.path.exists(local_filename):
                os.remove(local_filename)
        else:
            messagebox.showinfo("Success", f"Download completed as {os.path.basename(local_filename)}")
            
    def upload(self, server_host, remote_filename, local_filename, blksize=512):
        """
        Upload function of the TFTP client.
        
        Args:
            server_host (str): The hostname or IP address of the TFTP server.
            remote_filename (str): The name of the file to be saved on the server.
            local_filename (str): The path to the local file to be uploaded.
            blksize (int, optional): The block size for data transfer. Defaults to 512.
        """
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        success = False
        server_port = 69
        try:
            with open(local_filename, 'rb') as file:
                wrq = b'\x00\x02' + remote_filename.encode() + b'\x00octet\x00'
                sock.sendto(wrq, (server_host, server_port))

                current_block = 0
                retries = self.max_retries
                transfer_addr = None

                while retries > 0:
                    try:
                        data, transfer_addr = sock.recvfrom(4)
                        opcode = int.from_bytes(data[:2], 'big')
                        if opcode == 4:  # ACK packet
                            block_number = int.from_bytes(data[2:4], 'big')
                            if block_number == 0:
                                current_block = 1
                                break
                        elif opcode == 5:  # ERROR packet
                            error_msg = data[4:-1].decode()
                            messagebox.showerror("Server Error", f"Server error: {error_msg}")
                            return
                    except socket.timeout:
                        retries -= 1
                        sock.sendto(wrq, (server_host, server_port))
                
                if retries == 0:
                    messagebox.showerror("Error", "Failed to initiate upload")
                    return

                while True:
                    file_data = file.read(blksize)
                    data_packet = b'\x00\x03' + current_block.to_bytes(2, 'big') + file_data
                    retries_inner = self.max_retries

                    while retries_inner > 0:
                        try:
                            sock.sendto(data_packet, transfer_addr)
                            ack_data, _ = sock.recvfrom(4)
                            opcode = int.from_bytes(ack_data[:2], 'big')
                            if opcode == 4:
                                ack_block = int.from_bytes(ack_data[2:4], 'big')
                                if ack_block == current_block:
                                    current_block += 1
                                    break
                            elif opcode == 5:
                                error_msg = ack_data[4:-1].decode()
                                messagebox.showerror("Server Error", f"Server error: {error_msg}")
                                return
                        except socket.timeout:
                            retries_inner -= 1

                    if retries_inner == 0:
                        messagebox.showerror("Error", "Max retries reached, transfer aborted")
                        break

                    if len(file_data) < blksize:
                        success = True
                        break
        finally:
            sock.close()

        if success:
            messagebox.showinfo("Success", "Upload completed")


    def parse_oack(self, data):
        """
        Parse the options acknowledgment (OACK) packet from the TFTP server.

        Args:
            data (bytes): The OACK packet data received from the server.

        Returns:
            dict: A dictionary containing the parsed options and their values.
        """
        
        options = {}
        parts = data.split(b'\x00')
        for i in range(0, len(parts) - 1, 2):
            key = parts[i].decode()
            value = parts[i + 1].decode()
            options[key] = value
        return options

class TftpClientGUI:
    def __init__(self, root):
        """
        Class constructor for TftpClientGUI
        
        Args:
            root (tk.Tk): The root window of the Tkinter application.
        """
        
        self.root = root
        self.root.title("TFTP Client")
        
        tk.Label(root, text="Server IP:").grid(row=0, column=0, padx=10, pady=10)
        self.server_ip = tk.Entry(root, width=30)
        self.server_ip.insert(0, "127.0.0.1")
        self.server_ip.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(root, text="Remote File:").grid(row=1, column=0, padx=10, pady=10)
        self.remote_file = tk.Entry(root, width=30)
        self.remote_file.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(root, text="Local File:").grid(row=2, column=0, padx=10, pady=10)
        self.local_file = tk.Entry(root, width=30)
        self.local_file.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(root, text="Block Size:").grid(row=3, column=0, padx=10, pady=10)
        self.blksize = tk.Entry(root, width=30)
        self.blksize.insert(0, "512")  # Default block size
        self.blksize.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Button(root, text="Download", command=self.download_file).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(root, text="Upload", command=self.upload_file).grid(row=4, column=1, padx=10, pady=10)
        
        self.client = TftpClient()

    def download_file(self):
        """
        Functionality of the download button
        
        Args:
            None
        Returns:
            None
        """
        
        server_ip = self.server_ip.get()
        remote_file = self.remote_file.get()
        local_file = self.local_file.get()
        blksize = int(self.blksize.get())
        
        if not server_ip or not remote_file or not local_file:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        self.client.download(server_ip, remote_file, local_file, blksize)

    def upload_file(self):
        """
        Functionality of the upalod button
        
        Args:
            None
        Returns:
            None
        """
        
        server_ip = self.server_ip.get()
        remote_file = self.remote_file.get()
        local_file = self.local_file.get()
        blksize = int(self.blksize.get())
        
        if not server_ip or not remote_file or not local_file:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        self.client.upload(server_ip, remote_file, local_file, blksize)

if __name__ == '__main__':
    root = tk.Tk()
    app = TftpClientGUI(root)
    root.mainloop()