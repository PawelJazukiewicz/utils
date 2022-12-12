# pip install Office365-REST-Python-Client
# Module to seemlessly save, copy & move files to/from sharepoint
# Technically works but code is a mess.
# I don't recommend working with Office365-REST-Python-Client library.

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import utils.credstore as credstore  # requires credstore and sharepoint credentials stored in "SharePointCred"
                  # in the same folder as this script.
import shutil
import os
import tempfile
from urllib.parse import urlparse

def split_url(sharePointURL):
    scheme, netloc, path, params, query, fragment = urlparse(sharePointURL)
    if netloc == "":
        if '.sharepoint.com' in path.lower():
            netloc, path = path.split("/", 1)
        else:
            netloc = "defaultcompany.sharepoint.com"
    else:
        path = path[1:]

    sites, siteName, sitePath = path.split("/", 2)
    filename = path.split("/")[-1:][0]
    if "." in filename:
        sitePath = "/".join(sitePath.split("/")[:-1])
    else:
        filename = ""
    if not scheme: scheme = "https"
    if sites == 'sites' and siteName and sitePath:
        context = f"{scheme}://{netloc}/sites/{siteName}/"
        path = f"/sites/{siteName}/{sitePath}"
    else:
        context = f"{scheme}://{netloc}/"
        path = f"/{path}"
    return context, path, filename

def is_sharepoint_path(path):
    """Simple test if a path is a sharepoint path or a hard drive path."""
    return path.startswith("http://") or path.startswith("https://") \
        or ("sites/" in path.lower()) or ("/" in path and '.sharepoint.com' in path.split("/",1)[0].lower())

def path_join(path, filename):
    """ Joins path for sharepoint or disk"""
    if is_sharepoint_path(path):
        if path[-1:] != "/": path += "/"
        return path + filename
    else:
        return os.path.join(path, filename)


def _get_context_with_credentials(contextUrl):
    cred = credstore.get_credentials("SharePointCred")
    ctx = ClientContext(contextUrl).with_user_credentials(cred.userName, cred.password)
    return ctx 

def _get_folder_and_filename(sharePointURL):
    contextUrl, path, filename = split_url(sharePointURL)
    ctx = _get_context_with_credentials(contextUrl)
    target_folder = ctx.web.get_folder_by_server_relative_url(path)
    return target_folder, filename

def listFilesInFolder(spFolderPath):
    contextUrl, path_s, filename_s = split_url(spFolderPath)
    ctx = _get_context_with_credentials(contextUrl)
    libraryRoot = ctx.web.get_folder_by_server_relative_url(path_s)
    ctx.load(libraryRoot)
    ctx.execute_query()
    files = libraryRoot.files
    ctx.load(files)
    ctx.execute_query()
    return files
    
def copy_anywhere(source, target):
    """
    Copy sourcefile to target. Works with Sharepoint and hard drive / network drive
    files, both ways. SP -> HD, HD -> SP, SP -> SP and HD -> HD.
    Acceptable sharepoint path syntax: 
        'http://company.sharepoint.com/sites/yoursite/../yourfile.doc'
        'company.sharepoint.com/sites/yoursite/../yourfile.doc'
        'sites/yoursite/../yourfile.doc' (will default to defaultcompany.sharepoint.com)
    Source requires full path with file name. Target requires base path only (filename optional,
    will be used if supplied, otherwise will be transfered from source.)
    """
    if is_sharepoint_path(source):
        if is_sharepoint_path(target):
            # SP to SP
            contextUrl, path_s, filename_s = split_url(source)
            ctx = _get_context_with_credentials(contextUrl)
            file = ctx.web.get_file_by_server_relative_url(path_s + "/" + filename_s)
            contextUrl, path, filename = split_url(target)
            if not filename: filename = filename_s
            copiedfile = file.copyto(path + "/" + filename, True).execute_query()
            return copiedfile.serverRelativeUrl
        else:
            # SP to disk 
            contextUrl, path, filename = split_url(source) 
            ctx = _get_context_with_credentials(contextUrl)
            if os.path.isdir(target):    
                target = os.path.join(target, filename)
            with open(target, "wb") as f:
                ret = ctx.web.get_file_by_server_relative_url(path + '/' + filename).download(f).execute_query()
            return target
    else:
        if is_sharepoint_path(target):
            # Disk to SP
            with open(source, "rb") as f:
               fileData = f.read()
            target_folder, filename = _get_folder_and_filename(target)
            if not filename:
                filename = os.path.split(source)[1]
            target_file = target_folder.upload_file(filename, fileData).execute_query()
            return target_file.serverRelativeUrl
        else:
            # Disk to disk
            output_file = shutil.copy2(source, target)
            return output_file

def move_anywhere(source, target):
    """
    Move sourcefile to target. Works with Sharepoint and hard drive / network drive
    files, both ways. SP -> HD, HD -> SP, SP -> SP and HD -> HD.
    Acceptable sharepoint path syntax: 
        'http://company.sharepoint.com/sites/yoursite/../yourfile.doc'
        'company.sharepoint.com/sites/yoursite/../yourfile.doc'
        'sites/yoursite/../yourfile.doc' (will default to defaultcompany.sharepoint.com)
    Source requires full path with file name. Target requires base path only (filename optional,
    will be used if supplied, otherwise will be transfered from source.)
    """
    if is_sharepoint_path(source):
        if is_sharepoint_path(target):
            contextUrl, path_s, filename_s = split_url(source)
            ctx = _get_context_with_credentials(contextUrl)
            file = ctx.web.get_file_by_server_relative_url(path_s + "/" + filename_s)
            contextUrl, path, filename = split_url(target)
            if not filename: filename = filename_s
            copiedfile = file.moveto(path + "/" + filename, True).execute_query()
            return copiedfile.serverRelativeUrl
        else:
            contextUrl, path, filename = split_url(source) 
            ctx = _get_context_with_credentials(contextUrl)
            if os.path.isdir(target):    
                target = os.path.join(target, filename)
            with open(target, "wb") as f:
                ret = ctx.web.get_file_by_server_relative_url(path + '/' + filename).download(f).execute_query()
            ret.recycle().execute_query()
            return target
    else:
        if is_sharepoint_path(target):
            with open(source, "br") as f:
               fileData = f.read()
            target_folder, filename = _get_folder_and_filename(target)
            if not filename:
                filename = os.path.split(source)[1]
            target_file = target_folder.upload_file(filename, fileData).execute_query()
            os.remove(source)
            return target_file
        else:
            output_file = shutil.move(source, target)
            return output_file

def save_anywhere(data, target, encoding="utf-8"):
    """
    Save data to target file. Works with Sharepoint and hard drive / network drive
    files, both ways.
    Acceptable sharepoint path syntax:   
        'http://company.sharepoint.com/sites/yoursite/../yourfile.doc'
        'company.sharepoint.com/sites/yoursite/../yourfile.doc'
        'sites/yoursite/../yourfile.doc' (will default to defaultcompany.sharepoint.com)
    """
    if is_sharepoint_path(target):
        if not encoding == "unicode": 
            data = data.encode(encoding)
        contextUrl, path, filename = split_url(target)
        target_folder, filename = _get_folder_and_filename(target)
        output_file = target_folder.upload_file(filename, data).execute_query()
        return output_file.serverRelativeUrl
    else:
        with open(target, "w", encoding=encoding) as f:
            f.write(data)
        return target

if __name__ == '__main__':
    pass
