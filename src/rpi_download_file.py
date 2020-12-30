import os
import re
import subprocess
from typing import Optional

import paramiko


class DownloadFileFromPi(object):
    """
    Using the paramiko module, this function ssh into the rpi and downloads the
    the csv file and saves it locally.
    """

    def __init__(
        self,
        pi_username: str,
        pi_password: str,
        local_fname: str,
        remote_path: str,
        mac_addr: str,
        rpi_ip: str,
        comp_password: Optional[str] = None,
    ):
        """
        :param pi_username: str
            pi username
        :param pi_password: str
            pi password
        :param local_fname: str
            path where the file should be saved
        :param remote_path: str
            path to file on the pi
        :param mac_addr: str
            the mac address of the RPI
        :param rpi_ip: the last known ip address of the device
        """

        if comp_password is None:
            raise ValueError(
                "Must input the computer login password for `comp_password` argument."
            )

        self.username = pi_username
        self.password = pi_password
        self.comp_password = comp_password
        self.local_fname = local_fname
        self.remote_path = remote_path
        self.mac_addr = mac_addr
        self.rpi_ip = rpi_ip

    def check_ip_address(self):
        """
        It takes awhile to scan the network for the IP address, so this checks if the
        IP address supplied matches the known MAC address for the device.
        """
        cmd1 = subprocess.Popen(["echo", self.comp_password], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(
            ["sudo", "-S", "nmap", "-sP", "-n", self.rpi_ip],
            stdin=cmd1.stdout,
            stdout=subprocess.PIPE,
        )
        output = cmd2.stdout.read().decode()
        try:
            new_mac_addr = re.search(
                "([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", output
            ).group(0)
            if new_mac_addr.lower() == self.mac_addr:
                return True
            else:
                return False
        except AttributeError:
            return False

    def get_ip_from_mac(self):
        """
        Get an ipaddress of a connected device with known MAC address.
        """
        # ping all connected devices so arp will work for the listed mac address
        _ = subprocess.check_output(("nmap", "-sP", "192.168.1.0/050"))
        arp_res = subprocess.check_output(("arp", "-a")).decode("ascii")
        arp_list = arp_res.split("?")
        try:
            match_idx = [
                i for i, x in enumerate(arp_list) if re.search(self.mac_addr, str(x))
            ][0]
        except IndexError:
            raise ValueError(
                "IP Address not found for MAC address {}".format(self.mac_addr)
            )
        ip_address = re.search(
            "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", arp_list[match_idx]
        ).group(0)

        return ip_address

    def download_file(self):
        """
        Using the paramiko module, this function ssh into the rpi and downloads the
        the csv file and saves it locally.
        """
        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if not self.check_ip_address():
                self.rpi_ip = self.get_ip_from_mac()
                print(f"New IP Address: {self.rpi_ip}")
            ssh_client.connect(
                hostname=self.rpi_ip, username=self.username, password=self.password
            )

            # make local path
            cwd = os.getcwd()
            local_path = os.path.join(cwd, self.local_fname)
            with ssh_client.open_sftp() as ftp_client:
                ftp_client.get(self.remote_path, local_path)
