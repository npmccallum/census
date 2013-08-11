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

import json
import hashlib

def index(db):
    db.hardware.profile.ensure_index("pci")
    db.hardware.profile.ensure_index("usb")
    
def process(db, state, data):
    # Get the PCI and USB IDs
    pci = state.get("hardware.pci.ids", None)
    usb = state.get("hardware.usb.ids", None)
    if pci is None or usb is None:
        return True

    # Generate the profile ID
    id = json.dumps((sorted(pci), sorted(usb))).encode('utf-8')
    id = hashlib.sha1(id).hexdigest()
    
    # Save the profile
    profile = {'_id': id, 'usb': usb, 'pci': pci}
    db.hardware.profile.save(profile)
    
    state["hardware.profile.id"] = profile['_id']
