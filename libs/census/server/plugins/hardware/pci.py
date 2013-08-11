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
    db.hardware.pci.ensure_index("vendor")
    db.hardware.pci.ensure_index("device")
    db.hardware.pci.ensure_index("subvnd")
    db.hardware.pci.ensure_index("subdev")
    db.hardware.pci.ensure_index("class")
    
def process(db, state, data):
    ids = []
    
    fields = ("vendor", "device", "subvnd", "subdev", "class")
    for dev in data.get("hardware.pci", []):
        # Filter out unwanted fields
        dev = dict(filter(lambda kv: kv[0] in fields, dev.items()))
        
        # Create ID
        dev["_id"] = "pci:v%08Xd%08Xsv%08Xsd%08Xbc%02Xsc%02Xi%02X" % (
                        dev["vendor"], dev["device"],
                        dev["subvnd"], dev["subdev"],
                        dev["class"] & 0xff0000 >> 16,
                        dev["class"] & 0x00ff00 >> 8,
                        dev["class"] & 0x0000ff >> 0)
        
        # Insert
        db.hardware.pci.save(dev)
        ids.append(dev["_id"])
    
    state["hardware.pci.ids"] = ids
