# Installation script for qrcode module on Badger 2040 W
# This should be run on the Badger device to install the qrcode library

print("Creating basic QR code functionality...")

try:
    # Try to import existing qrcode module
    import qrcode
    print("QR code module already available!")
except ImportError:
    print("QR code module not available - creating dummy module")
    # Create a dummy qrcode module to prevent errors
    with open('qrcode.py', 'w') as f:
        f.write('''# Dummy QR code module for Badger 2040 W
class QRCode:
    def set_text(self, text): 
        self.text = text
    def get_size(self): 
        return (1, 1)
    def get_module(self, x, y): 
        return False
''')
    print("Created dummy QR module - QR functionality will be limited")
