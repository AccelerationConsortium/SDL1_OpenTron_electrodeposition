import os
import sys
import platform
import subprocess
from setuptools import setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    
    def run(self):
        install.run(self)
        
        # Only run on Linux
        if platform.system() == "Linux":
            self._run_linux_setup()
        
        # Install SquidstatPyLibrary wheel based on platform
        self._install_squidstat_wheel()
    
    def _run_linux_setup(self):
        """Run install_dependencies.sh on Linux."""
        script_path = os.path.join(
            os.path.dirname(__file__),
            "src",
            "install_dependencies.sh"
        )
        
        if os.path.exists(script_path):
            print("\n" + "="*60)
            print("Running Linux dependency installation script...")
            print("="*60)
            try:
                # Make script executable
                os.chmod(script_path, 0o755)
                # Run the script
                result = subprocess.run(
                    ["bash", script_path],
                    check=False,
                    capture_output=False
                )
                if result.returncode != 0:
                    print("\nWARNING: install_dependencies.sh returned non-zero exit code.")
                    print("You may need to run it manually with sudo privileges.")
                    print("Script location:", script_path)
            except Exception as e:
                print(f"\nWARNING: Could not run install_dependencies.sh: {e}")
                print("You may need to run it manually with sudo privileges.")
                print("Script location:", script_path)
        else:
            print(f"\nWARNING: install_dependencies.sh not found at {script_path}")
    
    def _install_squidstat_wheel(self):
        """Install the appropriate SquidstatPyLibrary wheel for the platform."""
        system = platform.system()
        
        if system == "Linux":
            wheel_name = "SquidstatPyLibrary-1.10.3.0-py3-none-manylinux2014_x86_64.whl"
        elif system == "Windows":
            wheel_name = "SquidstatPyLibrary-1.8.0.5-py3-none-win_amd64.whl"
        else:
            print(f"\nWARNING: SquidstatPyLibrary wheel not available for {system}")
            return
        
        wheel_path = os.path.join(
            os.path.dirname(__file__),
            "src",
            wheel_name
        )
        
        if os.path.exists(wheel_path):
            print(f"\nInstalling {wheel_name}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", wheel_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                print(f"Successfully installed {wheel_name}")
            except subprocess.CalledProcessError as e:
                print(f"\nWARNING: Could not install {wheel_name}")
                print(f"Error: {e}")
                print(f"You may need to install it manually: pip install {wheel_path}")
        else:
            print(f"\nWARNING: {wheel_name} not found at {wheel_path}")


setup(
    cmdclass={
        'install': PostInstallCommand,
    },
)
