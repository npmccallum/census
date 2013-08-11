#!/usr/bin/env python
#
# Copyright 2012 Nathaniel McCallum
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def index(db):
    db.hardware.usb.ensure_index("vendor")
    db.hardware.usb.ensure_index("product")
    db.hardware.usb.ensure_index("device")
    db.hardware.usb.ensure_index("class")
    db.hardware.usb.ensure_index("subclass")
    db.hardware.usb.ensure_index("protocol")

def process(db, state, data):
    ids = []

    fields = ("vendor", "product", "device", "class", "subclass", "protocol")    
    for dev in data.get("hardware.usb", []):
        # Filter out unwanted fields
        dev = dict(filter(lambda kv: kv[0] in fields, dev.items()))
        
        # Create ID
        dev["_id"] = "usb:v%04Xp%04Xd%04Xdc%02Xdsc%02Xdp%02X" % (
                        dev["vendor"], dev["product"], dev["device"],
                        dev["class"], dev["subclass"], dev["protocol"])
        
        # Insert
        db.hardware.usb.save(dev)
        ids.append(dev["_id"])

    state["hardware.usb.ids"] = ids
