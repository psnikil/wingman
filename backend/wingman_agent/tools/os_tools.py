"""Tools for operating system-level interactions such as launching applications, opening web browsers, searching files, and capturing screenshots."""
import os
import subprocess
import shutil
import platform
import webbrowser
import requests
from typing import Optional, List
from langchain.tools import tool
from .data_models import (
    OpenBrowserArgs, OpenAppArgs, TakeScreenshotArgs, 
    SearchOSFilesArgs, DownloadFileArgs
)

class UbuntuOSTools:
    """Tools for interacting with a Ubuntu/Linux operating system."""

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=OpenBrowserArgs,
        description="""Opens a URL in the default web browser on a Ubuntu/Linux system.
        Example: open_browser(url="https://www.google.com")
        
        When to use: Use when the user needs to visually inspect a website or documentation."""
    )
    def open_browser(url: str) -> str:
        """Opens a URL in the default web browser."""
        args = OpenBrowserArgs(url=url)
        try:
            subprocess.Popen(['xdg-open', args.url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Successfully opened {args.url} in the default browser."
        except Exception as e:
            return f"Error opening browser: {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=OpenAppArgs,
        description="""Launches a desktop application by its command name on a Ubuntu system.
        Examples:
        - Text Editor: open_app(app_name="gedit")
        - Calculator: open_app(app_name="gnome-calculator")
        
        When to use: Useful for opening editors or system utilities directly for the user."""
    )
    def open_app(app_name: str) -> str:
        """Launches a desktop application by name."""
        args = OpenAppArgs(app_name=app_name)
        try:
            subprocess.Popen([args.app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Successfully launched {args.app_name}."
        except Exception as e:
            return f"Error launching app '{args.app_name}': {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=TakeScreenshotArgs,
        description="""Captures a screenshot of the main display and saves it to a file.
        Example: take_screenshot(filename="desktop_view.png")
        
        When to use: Use to record the current GUI state for visual confirmation."""
    )
    def take_screenshot(filename: str = "screenshot.png") -> str:
        """Captures a screenshot of the main display."""
        args = TakeScreenshotArgs(filename=filename)
        try:
            # Use 'import' from ImageMagick as fallback if gnome-screenshot/scrot are not found
            # 'import -window root' captures the whole screen
            subprocess.run(['import', '-window', 'root', args.filename], check=True)
            return f"Screenshot saved to {os.path.abspath(args.filename)}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}. Ensure 'imagemagick' is installed."

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=SearchOSFilesArgs,
        description="""Searches for files on the system using the 'find' command.
        Always use absolute paths for search_path.
        Examples:
        - PDFs: os_search_files(pattern="*.pdf", search_path="/home/user/Documents")
        - Configs: os_search_files(pattern="config.yaml", search_path=".")
        
        When to use: Powerful for locating files across large directory structures. ONLY use when searching for files outside the suers workspace."""
    )
    def os_search_files(pattern: str, search_path: str = ".") -> str:
        """Searches for files on the system."""
        args = SearchOSFilesArgs(pattern=pattern, search_path=search_path)
        try:
            cmd = ['find', args.search_path, '-name', args.pattern]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            files = result.stdout.strip().split('\n')
            if not files or files == ['']:
                return f"No files matching '{args.pattern}' found in {args.search_path}."
            return f"Found {len(files)} files:\n" + "\n".join(files[:20]) + ("\n... (truncated)" if len(files) > 20 else "")
        except Exception as e:
            return f"Error searching files: {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=DownloadFileArgs,
        description="""Downloads a resource from a URL to a local destination file.
        Example: download_file(url="https://example.com/data.zip", save_path="./downloads/data.zip")
        
        When to use: Ideal for fetching assets or data files directly into the project."""
    )
    def download_file(url: str, save_path: str) -> str:
        """Downloads a resource from a URL."""
        args = DownloadFileArgs(url=url, save_path=save_path)
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(args.save_path)), exist_ok=True)
            
            response = requests.get(args.url, stream=True)
            response.raise_for_status()
            
            with open(args.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return f"Successfully downloaded resource to {args.save_path}"
        except Exception as e:
            return f"Error downloading file: {str(e)}"


class WindowsOSTools:
    """Tools for interacting with a Windows operating system."""

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=OpenBrowserArgs,
        description="""Opens a URL in the default web browser on Windows.
        Example: open_browser(url="https://microsoft.com")"""
    )
    def open_browser(url: str) -> str:
        """Opens a URL in the default web browser on Windows."""
        args = OpenBrowserArgs(url=url)
        try:
            if platform.system() != "Windows":
                return "This tool requires a Windows system."
            webbrowser.open(args.url)
            return f"Successfully opened {args.url} in Windows browser."
        except Exception as e:
            return f"Error opening browser on Windows: {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=OpenAppArgs,
        description="""Launches an application on Windows.
        Example: open_app(app_name="notepad")"""
    )
    def open_app(app_name: str) -> str:
        """Launches an application on Windows."""
        args = OpenAppArgs(app_name=app_name)
        try:
            if platform.system() != "Windows":
                return "This tool requires a Windows system."
            if hasattr(os, 'startfile'):
                os.startfile(args.app_name) # type: ignore
                return f"Successfully launched {args.app_name} on Windows."
            else:
                subprocess.Popen(['start', args.app_name], shell=True)
                return f"Successfully launched {args.app_name} on Windows using 'start'."
        except Exception as e:
            return f"Error launching app '{args.app_name}' on Windows: {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=TakeScreenshotArgs,
        description="""Captures a screenshot on Windows.
        Example: take_screenshot(filename="win_capture.png")"""
    )
    def take_screenshot(filename: str = "screenshot.png") -> str:
        """Captures a screenshot on Windows."""
        args = TakeScreenshotArgs(filename=filename)
        try:
            if platform.system() != "Windows":
                return "This tool requires a Windows system."
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $$Screen = [System.Windows.Forms.Screen]::PrimaryScreen
            $$Bitmap = New-Object System.Drawing.Bitmap($$Screen.Bounds.Width, $$Screen.Bounds.Height)
            $$Graphics = [System.Drawing.Graphics]::FromImage($$Bitmap)
            $$Graphics.CopyFromScreen($$Screen.Bounds.X, $Screen.Bounds.Y, 0, 0, $$Screen.Bounds.Size)
            $$Bitmap.Save('{os.path.abspath(args.filename)}')
            $$Graphics.Dispose()
            $$Bitmap.Dispose()
            """
            subprocess.run(["powershell", "-Command", ps_script], check=True)
            return f"Screenshot saved to {os.path.abspath(args.filename)}"
        except Exception as e:
            return f"Error taking screenshot on Windows: {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=SearchOSFilesArgs,
        description="""Searches for files on Windows.
        Example: os_search_files(pattern="*.docx", search_path="C:\\\\Users")"""
    )
    def os_search_files(pattern: str, search_path: str = ".") -> str:
        """Searches for files on Windows."""
        args = SearchOSFilesArgs(pattern=pattern, search_path=search_path)
        try:
            if platform.system() != "Windows":
                return "This tool requires a Windows system."
            ps_cmd = f"Get-ChildItem -Path '{args.search_path}' -Filter '{args.pattern}' -Recurse | Select-Object -ExpandProperty FullName"
            result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, check=True)
            files = result.stdout.strip().split('\n')
            if not files or files == ['']:
                return f"No files matching '{args.pattern}' found on Windows."
            return f"Found {len(files)} files:\n" + "\n".join(files[:20])
        except Exception as e:
            return f"Error searching files on Windows: {str(e)}"

    @staticmethod
    @tool(
        parse_docstring=True, 
        args_schema=DownloadFileArgs,
        description="""Downloads a file on Windows.
        Example: download_file(url="https://example.com/install.exe", save_path="install.exe")"""
    )
    def download_file(url: str, save_path: str) -> str:
        """Downloads a file on Windows."""
        args = DownloadFileArgs(url=url, save_path=save_path)
        try:
            if platform.system() != "Windows":
                return "This tool requires a Windows system."
            os.makedirs(os.path.dirname(os.path.abspath(args.save_path)), exist_ok=True)
            ps_cmd = f"Invoke-WebRequest -Uri '{args.url}' -OutFile '{args.save_path}'"
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            return f"Successfully downloaded file to {args.save_path}"
        except Exception as e:
            return f"Error downloading file on Windows: {str(e)}"
