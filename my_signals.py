import signal
import sys
def signal_handler(sig, frame):
    print('\nCtrl-C received, exiting.')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
