# Example program from Part 01 of the python-csp tutorial

# Copyright (C) Sarah Mount, 2010.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have rceeived a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import time

from csp.csp import *


def response(code, reason, page):
    """Construct and return a single HTTP response.

    FIXME: Should read and return files from disk, not a static page.
    FIXME: Should handle other MIME types.
    """
    html = """
    <html>
    <head><title>%i %s</title></head>
    <body>
    %s
	<hr/>
	<p><strong>Date:</strong> %s</p>
    </body>
    </html>
    """ % (code, reason, page, time.ctime())
    template = """HTTP/1.0 %i %s
    Content-Type: text/html
	Content-Length: %i


    %s
    """ % (code, reason, len(html), html)
    return template


@process
def server(host, port):
    """Simple CSP based web server.
    """
    print('Running tutorial web-server on port {0}...'.format(port))
    print('Interrupt with CTRL-C')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)    
    while True:
        conn_sock, conn_addr = sock.accept()
        request = conn_sock.recv(4096).strip()
        if request.startswith('GET'):
            handler_ok(request, conn_sock).start()
        else:
            handler_not_found(request, conn_sock).start()


@process
def handler_ok(request, conn_sock):
    """Handle a single HTTP 200 OK request.
    """
    page = '<h1>My python-csp web server!</h1>'
    page += '<p><strong>You asked for:</strong><pre>%s</pre></p>' % request
    conn_sock.send(response(200, 'OK', page))
    conn_sock.shutdown(socket.SHUT_RDWR)
    conn_sock.close()
    return


@process
def handler_not_found(request, conn_sock):
    """Handle a single HTTP 404 Not Found request.
    """
    page = '<h1>Cannot find your file</h1>'
    page += '<p><strong>You asked for:</strong><pre>%s</pre></p>' % request
    conn_sock.send(response(404, 'Not Found', page))
    conn_sock.shutdown(socket.SHUT_RDWR)
    conn_sock.close()
    return


if __name__ == '__main__':
    host = ''
    port = 8888
    server(host, port).start()

