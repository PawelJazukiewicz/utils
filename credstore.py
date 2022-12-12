# STATUS: Complete
# Import to use get_credentials
# Run from command line to store credentials.

import subprocess
import getpass
import sys
import os

class Credential(object):
    def __init__(self, user_name, password):
        """
        :type password: str
        :type user_name str
        """
        self.userName = user_name
        self.password = password

def _get_cred_path(credName, path):
    return os.path.join(path or os.path.join(os.path.split(os.path.realpath(__file__))[0], 'Creds'),
                                "_".join([credName, os.environ['username'][0:5], os.environ['computername'] + '.xml']))

def get_credentials(credName, path=""):
    """Retrieves credentials stored in credName_user_computername.xml.
    Returns an object with .Username and .Password properties (plaintext strings).
    credName refers only to the credential storage file name prefix. Suffix and extension are appended automatically.
    Suffix consists of first 5 characters of %username% + _ + %computername% + .xml
    Ex. Use 'C:\\Users\\JSmith\\Creds\\cred' to refer to a file 'C:\\Users\\JSmith\\Creds\\cred_JSmit_JohnsLaptop.xml'
    To store credentials, use credStore.StoreCredentials or run credStore.py from command line (credName in argument).
    By default, ie if path is not supplied, will look for credentials in a subfolder named Creds in the same folder
    as this file (credStore.py).
    Passwords can only be retrieved on the machine that was used to store them, by the user who stored them. Store credentials for 
    multiple users or machines in the same folder, with the same prefix. That way the same code can be used to retrieve the proper 
    credential for when ran by different users or on different machines.
    """
    credFullPath = _get_cred_path(credName, path)
    cmd = '$cred = Import-Clixml -Path "' + credFullPath + '"; \
            $cred.Username; \
            $cred.GetNetworkCredential().Password'
    runcommand = subprocess.run(["powershell", "-Command", cmd], 
                                capture_output=True, 
                                text=True)
    if runcommand.returncode != 0:
        print(runcommand.stderr)
    else:
        outputStr = runcommand.stdout.splitlines()
        output = Credential(*outputStr)
        return output

def store_credentials(credName="", path=""):
    if credName == "":
        credName = input("Cred name: ")
    credFullPath = _getCredPath(credName, path)
    credBasePath = os.path.split(credFullPath)[0]
    if not os.path.isdir(credBasePath):
        os.mkdir(credBasePath)
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    cmd = '$cred = New-Object System.Management.Automation.PSCredential("' \
           + username + '",(ConvertTo-SecureString "' \
           + password + '" -AsPlainText -Force)); Export-Clixml -Path "' \
           + credFullPath + '" -InputObject $cred'
    runcommand = subprocess.run(["powershell", "-Command", cmd], 
                                capture_output=True, 
                                text=True)
    return runcommand

if __name__ == "__main__":
    if len(sys.argv) > 3:
        print("Too many arguments (path with spaces not in '' ?)")
    else:
        ret = store_credentials(*sys.argv[1:])
        if ret.returncode == 0:
            print("Credential stored successfully.")
        else:
            print(ret.stderr)