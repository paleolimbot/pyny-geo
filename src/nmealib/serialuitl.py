import serial
import glob

def scanPortsLinux():
    """scan for available ports. return a list of device names."""
    return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/tty.usb*')

print scanPortsLinux()
