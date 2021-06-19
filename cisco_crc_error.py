#Import Scrapli (Network Library)
from scrapli.driver.core import IOSXEDriver
from scrapli.exceptions import ScrapliAuthenticationFailed 
#Import Getpass for Password information
from getpass import getpass
#Import RICH for table creation
from rich.console import Console, ConsoleThreadLocals
from rich.table import Table
from rich import print
#Import Sys
import sys

#Parameters required by user
filename = input("Please enter the filename (IP-Address File): ")
user = input("Enter the username: ")
password = getpass("Enter the Password: ")

#Create a list of IP-Address from filename
try:    
    with open(filename) as ip_file:
        ip_list = ip_file.read().splitlines()
except FileNotFoundError:
    print(f"[bold red] File with name {filename} not found or incorrect file name.[/bold red]")
    sys.exit()

#Table creation
table = Table(title="Device CRC ERROR Details \n")
table.add_column("Hostname", justify="right", style="cyan", no_wrap=True)
table.add_column("Interface", justify="right", style="cyan", no_wrap=True)
table.add_column("CRC-Error", style="bold red")

try:
    for ip in ip_list:
        device = {
            "host": ip,
            "auth_username": user,
            "auth_password": password,
            "auth_strict_key": False,
            }

        conn = IOSXEDriver(**device)
        conn.open()
        
        #Show command to get Hostname
        sh_version = conn.send_command("show version")
        sh_version_structured = sh_version.genie_parse_output()
        hostname = sh_version_structured['version']['hostname']

        #Show command to get interface and their CRC errors
        sh_interfaces = conn.send_command("show interfaces")
        show_intf_structured = sh_interfaces.genie_parse_output()
        
        for interface in show_intf_structured.keys():  
            crc_error = show_intf_structured[interface]['counters']['in_crc_errors']
            if crc_error > 10:
                str_crc_error = str(crc_error)
                #Write Data to RICH table
                table.add_row(hostname, interface, str_crc_error)
except ScrapliAuthenticationFailed:
    print("[bold red]Invalid Username or Password. Please try again.[/bold red]")
    sys.exit()

#Display table with CRC error details
console = Console()
console.print(table)
