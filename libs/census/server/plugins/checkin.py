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
import datetime

def index(db):
    db.checkin.ensure_index("uuid")
    db.checkin.ensure_index("time")
    db.checkin.ensure_index("hardware")
    
def process(db, state, data):
    hwp = state.get("hardware.profile.id", None)
    if hwp is None:
        return True

    uuid = data.get("uuid", None)
    if uuid is None:
        return False

    checkin = {"uuid": uuid["uuid"],
               "time": datetime.datetime.now(),
               "hardware": hwp}
    db.checkin.save(checkin)
