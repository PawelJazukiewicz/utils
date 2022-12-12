# utils
Useful utilities for corportate Python scripting.

## credstore.py
Save your credentials locally for use in Python scripts using Windows API and encryption, leveraging Powershell secure strings. 
Credentials saved this way can only be retrieved on the machine, from which they were stored, by the user who stored them.
Saves credentials in an xml file interoperable with Powershell, in the creds folder inside utils.
File naming convention allows for multiple users to use same script on multiple machines, if they store their credentials in the same place.

## download_monitor.py
Monitor downloads folder and wait for one / all downloads to complete when using Selenium.

## sharepoint_files.py
Copy. move and save files to / from UNC paths and sharepoint seemlessly/agnostically - Copy, Move and Save that accepts sharepoint paths.
Requires Sharepoint-REST-API.

## start_logger.py
Wrapper for teams-logger.
