import logging
import os
import re
import subprocess
from typing import Optional

import paramiko

logging.basicConfig(level=logging.INFO)


class DownloadFileFromPi:
    """
    Using the paramiko module, this function ssh into the rpi and downloads the
    the csv file and saves it locally to the current working directory. 
    Required are the local and remote paths for saving and downloading, respectively, 
    the file, and the MAC address of the rpi.

    The user can also input the last known IP address of the pi and the code will
    check if that IP address matches up with the MAC address given. This is much faster
    than scanning the computer's local network for all connected devices. This step also
    requires the computer login password to be input as `root_password`.

    Example:
        DownloadFileFromPi(
            rpi_username="pi",
            rpi_password="raspberry",
            rpi_mac_addr="AA:BB:CC:DD:EE:FF",
            rpi_ip="192.168.1.1"
            root_password="local_login_password"
        ).download_file(
            local_fname="some_file.csv",
            remote_path="/home/pi/path/to/file.csv"
        )

    Recommended to take the slow approach and scan the network instead of inputting
    the root password because it is not encrypted. Once the network has been scanned,
    subsequent downloads should be much faster.

    """

    def __init__(
        self,
        rpi_username: str,
        rpi_password: str,
        rpi_mac_addr: str,
        rpi_ip: Optional[str] = None,
        root_password: Optional[str] = None,
    ):
        """
        :param rpi_username: str
        :param rpi_password: str
        :param rpi_mac_addr: str
            the mac address of the RPI
        :param rpi_ip:
            the last known ip address of the device
        :param root_password:
            the root password for the local computer
        """

        if not re.match(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", rpi_mac_addr):
            raise ValueError(f"The MAC address {rpi_mac_addr} is not valid.")

        if rpi_ip and root_password is None:
            raise ValueError(
                "If checking the previously known rpi IP address, the `root_password` "
                "must be entered."
            )

        self.rpi_username = rpi_username
        self.rpi_password = rpi_password
        self.root_password = root_password
        self.rpi_mac_addr = rpi_mac_addr
        self.rpi_ip = rpi_ip

    def check_ip_address(self):
        """
        It takes awhile to scan the network for the IP address, so this checks if the
        IP address supplied as the last known ip matches the known MAC address for the device.
        """
        cmd1 = subprocess.Popen(["echo", self.root_password], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(
            ["sudo", "-S", "nmap", "-sP", "-n", self.rpi_ip],
            stdin=cmd1.stdout,
            stdout=subprocess.PIPE,
        )
        output = cmd2.stdout.read().decode()
        try:
            new_mac_addr = re.search(
                r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", output
            ).group(0)
            if new_mac_addr.lower() == self.rpi_mac_addr:
                return True
            else:
                return False
        except AttributeError:
            return False

    def get_ip_from_mac(self):
        """
        Get an ipaddress of a connected device with known MAC address.
        """
        # ping all ips from 192.168.1.[0-250] so arp will work for the listed mac address
        _ = subprocess.check_output(("nmap", "-sP", "192.168.1.0/24"))
        arp_res = subprocess.check_output(("arp", "-a")).decode("ascii")
        arp_list = arp_res.split("?")
        try:
            match_idx = [
                i
                for i, x in enumerate(arp_list)
                if re.search(self.rpi_mac_addr, str(x))
            ][0]
        except IndexError:
            raise ValueError(
                "IP Address not found for MAC address {}".format(self.rpi_mac_addr)
            )
        ip_address = re.search(
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", arp_list[match_idx]
        ).group(0)

        return ip_address

    def download_file(self, local_fname: str, remote_path: str):
        """
        Using the paramiko module, this function ssh into the rpi and downloads the
        the csv file and saves it locally.

        :param local_fname: str
            file name to be saved locally
        :param remote_path: str
            path to file on the rpi
        """
        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if not self.rpi_ip:
                self.rpi_ip = self.get_ip_from_mac()
                logging.info(
                    f"IP Address at mac address `{self.rpi_mac_addr}`: {self.rpi_ip}"
                )
            elif not self.check_ip_address():
                self.rpi_ip = self.get_ip_from_mac()
            ssh_client.connect(
                hostname=self.rpi_ip,
                username=self.rpi_username,
                password=self.rpi_password,
            )

            cwd = os.getcwd()
            local_path = os.path.join(cwd, local_fname)
            with ssh_client.open_sftp() as ftp_client:
                ftp_client.get(remote_path, local_path)
