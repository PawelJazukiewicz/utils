# STATUS: Complete
# Import to use DownloadMonitor.

import os
import time
import glob

class DownloadTimeoutException(Exception): pass

class DownloadMonitor:
    """Helper class for handling file downloads with Selenium. Waits until download finishes and returns downloaded
    file(s).  \n Instantiate before triggering download: \n myDownload = DownloadMonitor() \n
    After triggering download, wait for it: \n myFile = myDownload.getFirstFinished(60) \n
    When downloading multiple files simultaneously and waiting for all of them, use: \n 
    myFileList = myDownload.getAllFinished(600) """
    
    partialExts = ['.part','.partial','.crdownload','.tmp']
    
    def defaultDownloadsPath(self):
        """Returns the default downloads path for linux or windows"""
        # https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        else:
            return os.path.join(os.path.expanduser('~'), 'downloads')
    
    def __init__(self, downloadsFolder=""):
        if downloadsFolder=="":
            downloadsFolder = self.defaultDownloadsPath()
        self._downloadsFolder = os.path.join(downloadsFolder, "*")
        self._list = [f for f in glob.glob(self._downloadsFolder) if os.path.isfile(f)]
    
    def getFirstFinished(self, timeout):
        """Returns single new file from the downloads folder - the first to finish downloading
        after instantiation. \n Ignores partial files. """
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            newCompleteFileList = [f for f in glob.glob(self._downloadsFolder) 
                                    if os.path.isfile(f) 
                                    and f not in self._list 
                                    and os.path.splitext(f)[1].lower() not in self.partialExts]
            if newCompleteFileList:
                return  min(newCompleteFileList, key=lambda file: os.path.getmtime(file))
            time.sleep(1)
        
        raise DownloadTimeoutException(timeout + " seconds timeout surpassed waiting for new file in " + self._downloadsFolder)

    def getAllFinished(self, timeout, suppressTimeoutReturnIncomplete=False):
        """Returns a list of all new files from the downloads folder created since instantiation. \n
        After first new file appears in the downloads folder, continues waiting until there are
        no more partial files. \n If suppressTimeoutReturnIncomplete set to True, doesn't raise timeout
        exception and on timeout returns list of all new files including partials."""
        timeout_start = time.time()
        downloadsStarted = False
        while time.time() < timeout_start + timeout:
            newFileList = [f for f in glob.glob(self._downloadsFolder) 
                            if os.path.isfile(f) 
                            and f not in self._list]
            if newFileList:
                downloadsStarted = True
                partialList = filter(lambda f: os.path.splitext(f)[1].lower() in self.partialExts, newFileList)
                if not partialList:
                    return newFileList
            time.sleep(1)
        
        if suppressTimeoutReturnIncomplete:
            return newFileList
        else:
            raise DownloadTimeoutException(timeout + " seconds timeout surpassed waiting for new files in "
             + self._downloadsFolder + (("\n" + "Partial downloads: " + partialList) if downloadsStarted else ""))

# Testing
if __name__ == "__main__":
    md = DownloadMonitor()
    print("Testing. You have 3 minutes to put a new file in the default downloads folder.")
    dl = md.getFirstFinished(180)
    print(dl)
