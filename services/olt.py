import os

from dotenv import load_dotenv

from parser.olt_parser import clean_output

from services.ssh_client import SSHClient


load_dotenv()


OLT_HOST = os.getenv("OLT_HOST")
OLT_USER = os.getenv("OLT_USER")
OLT_PASS = os.getenv("OLT_PASS")


ssh = SSHClient(
    host=OLT_HOST,
    username=OLT_USER,
    password=OLT_PASS
)


def check_olt():

    command = "show card"

    result = ssh.execute(command)

    parsed = clean_output(result)

    return parsed
