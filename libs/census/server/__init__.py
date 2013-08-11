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

import cgi
import httplib
import os
import sys

import bson.json_util
import pymongo

class HTTPException(Exception):
    def __init__(self, code):
        self.code = code
        
    def __str__(self):
        return "%d %s" % (self.code, httplib.responses[self.code])
        
class Application:
    def _foreach(self, method, *args):
        queue = list(self._plugins)
        while queue:
            mod = queue.pop(0)
            if getattr(mod, method, lambda *x: None)(self._db, *args):
                queue.append(mod)
    
    def __init__(self, db, rwcreds, rocreds=('readonly', 'readonly')):
        self._db = db
        self._rwcreds = rwcreds
        self._rocreds = rocreds
        
        # Authenticate for read/write
        try:
            self._db.logout()
        except:
            pass
        self._db.authenticate(*rwcreds)
        
        # Load all the plugins
        inv = []
        import plugins
        pdir = os.path.dirname(plugins.__file__)
        for root, dirs, files in os.walk(pdir):
            for file in files:
                if not file.endswith(".py"):
                    continue
                if file.startswith("_"):
                    continue
                
                file = os.path.join(root, file)
                mod = file[len(pdir)+1:-3]
                mod = mod.replace(os.path.sep, '.')
                mod = plugins.__name__ + '.' + mod
                __import__(mod)
                inv.append(sys.modules[mod])
        self._plugins = tuple(inv)
        
        # Create indexes
        self._foreach("index")
                
    def __call__(self, environ, start_response):
        try:
            # Get the method
            method = environ.get('REQUEST_METHOD', '').upper()
            if method == 'POST':
                f = self._post
            elif method == 'PUT':
                f = self._put
            else:
                raise HTTPException(httplib.METHOD_NOT_ALLOWED)
    
            # Parse the request data
            try:
                size = int(environ.get('CONTENT_LENGTH', 0))
                body = environ['wsgi.input'].read(size)
            except ValueError:
                raise HTTPException(httplib.BAD_REQUEST)        
        
            # Call the method function
            return f(environ, start_response, body)
            
        except HTTPException as e:
            start_response(str(e), [])
            return []

    def _put(self, environ, start_response, body):
        try:
            data = bson.json_util.loads(body.decode("utf-8"))
        except ValueError:
            raise HTTPException(httplib.BAD_REQUEST)
        
        # Perform the insert
        state = {}
        self._foreach("process", state, data)
        raise HTTPException(httplib.OK)
    
    def _post(self, environ, start_response, body):
        try:
            data = cgi.parse_qs(body.decode("utf-8"))
            args = bson.json_util.loads(data.get('args', ['[]'])[0])
            func = data.get('func', [None])[0]
        except ValueError:
            raise HTTPException(httplib.BAD_REQUEST)      
        
        if not isinstance(args, (list, tuple)) or func is None:
            raise HTTPException(httplib.BAD_REQUEST)
        
        # Add the read-only user if not present
        rouser = self._db.system.users.find_one({'user': self._rocreds[0]})
        if rouser is None:
            self._db.add_user(self._rocreds[0], self._rocreds[1], True)
        
        # Connect to the database and run the function
        self._db.logout()
        try:
            self._db.authenticate(*self._rocreds)
            result = self._db.command("$eval", func, args=args, nolock=True)
        finally:
            try:
                self._db.logout()
            except:
                pass
            self._db.authenticate(*self._rwcreds)
        
        if not result.get("ok", False):
            raise HTTPException(httplib.INTERNAL_SERVER_ERROR)
        
        # Return response
        resp = bson.json_util.dumps(result.get("retval", None))
        start_response('200 OK', [('Content-Type', 'application/json'),
                                  ('Content-Length', str(len(resp)))])
        return [resp]
    
__all__ = [Application.__name__]
