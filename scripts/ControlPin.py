#! /usr/bin/python
#
# Turn a pin on or off, for example
#	sudo python ControlPin.py -g 0 off
#
# default is GPIO pin 0 off

from WiringPin import WiringPin
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-g", "--gpio", type = "int", default = 0)

(options, args) = parser.parse_args()
state = True if len(args) != 0 and args[0] == "on" else False
wp = WiringPin(options.gpio).export()

wp.set_value(state)
