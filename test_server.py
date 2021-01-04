import http.server
import socketserver

# deal with the query URLs
from urllib import parse

import datetime

import json
import h5py


from dda import DDA, TimestampComponents

from dda_hdf5 import get_memory_file_id


class Pi(object):
    """
    Dummy data: return decimal expansion of pi
    add a single decimal for each delta past a set epoch date
    Each delta increases the version
    pi can be sliced (1-dim) on its decimals
    """
    def __init__(self, epoch=datetime.datetime.now()
                     , delta=datetime.timedelta(seconds=(15*60))
                     , shape = (1,)):
        self._epoch = epoch
        self._delta = delta
        self._shape = shape

        self._timestamp_parser = TimestampComponents()
    # end def

    def _digits(x):
        """Generate x digits of Pi: Spigot algorithm Gibbons, 2005"""
        q,r,t,j = 1, 180, 60, 2
        while x > 0:
            u,y = 3*(3*j+1)*(3*j+2), (q*(27*j-12)+5*r)//(5*t)
            yield y

            x -= 1
            q,r,t,j = (10*q*j*(2*j-1)), (10*u*(q*(5*j-2)+r-y*t)), (t*u), (j+1)
    # end def

    def __call__(self, name='pi', cmajor=None, cminor=None
                                , cdate=None, nslice=None):
        ndec = 1 + int(((datetime.datetime.now() - self._epoch
                       ).total_seconds())/self._delta.total_seconds()
                      )
        digits = [n for n in list(Pi._digits(ndec))]

        # version
        cmajor = 1 if cmajor is None else cmajor
        cminor = len(digits) - 1 if cminor is None else min(len(digits), cminor)
        # get datetime object
        cstamp = self._epoch + self._delta * (cminor - 0) if cdate is None\
                 else datetime.datetime(*(cdate+(0,1,1,0,0,0)[len(cdate):]))

        # iso date time format
        tformat = self._timestamp_parser._tformats[0]

        version_str = '.'.join((str(cmajor)
                              , str(cminor)
                              , cstamp.strftime(tformat)
                               )
                              )

        return (digits[:cminor], cmajor, cminor, cstamp.strftime(tformat)
                               , version_str)
    # end def

    def _versions():
        ndec = 1 + int(((datetime.datetime.now() - self._epoch
                       ).total_seconds())/self._delta.total_seconds()
                      )
        # version
        cmajor = 1
        cminor = list(range(ndec))
        # get datetime object
        cstamp = [self._epoch + self._delta * (cdx - 0) for cdx in cminor]

        return (cmajor, cminor, cstamp)
    # end def


class PiHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pidigit = Pi()

    def _set_json_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
       
    def _set_h5_headers(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'application/x-hdf')
        self.send_header('Content-Disposition'
                       , 'attachment; filename="{}"'.format(filename)
                        )
        self.end_headers()

    # We only need to handle get requests (via url)
    def do_GET(self):
        parsed_path = parse.urlparse(self.path)
        print('path', parsed_path)

        # message to send back
        message_parts = [
            'CLIENT VALUES:',
            'client_address={} ({})'.format(
                self.client_address,
                self.address_string()),
            'command={}'.format(self.command),
            'path={}'.format(self.path),
            'real path={}'.format(parsed_path.path),
            'query={}'.format(parsed_path.query),
            'request_version={}'.format(self.request_version),
            '',
            'SERVER VALUES:',
            'server_version={}'.format(self.server_version),
            'sys_version={}'.format(self.sys_version),
            'protocol_version={}'.format(self.protocol_version),
            '',
            'HEADERS RECEIVED:',
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append(
                '{}={}'.format(name, value.rstrip())
            )
        message_parts.append('')
        message = '\r\n'.join(message_parts)

        print(message)

        #self.send_response(200)
        #self.send_header('Content-Type',
        #                 'text/plain; charset=utf-8')
        #self.end_headers()
        
        #self.wfile.write(message.encode('utf-8'))
        
        # if real path matches a Digital Data Object
        dda = DDA()
        names, version, cslice, ext = dda(parsed_path.path)

        if not ext in ['json','h5']:
            self.send_error(404)
        else:
            # return data set
            if version is None:
                version = (None, None, None)
            parray = pdigit('pi', *version)

            if cslice is not None:
                cslice = slice(*cslice[0][1:])
            else:
                cslice = slice(None, None, None)

            if ext == 'json':
                self._set_json_headers()
                # write encoded json
                self.wfile.write(json.dumps({'dda': {'pi': parray[0][cslice]
                                           , 'version':parray[1:]
                                            }}
                                           ).encode('utf-8')
                                )
            elif ext == 'h5':
                self._set_h5_headers(parsed_path.path)

                file_id = get_memory_file_id()

                # create groups and stash data
                with h5py.File(file_id, mode='w') as root:
                    dda = root.create_group("dda")
                    dset =  dda.create_dataset("pi"
                                          , (len(parray[0][cslice]),), dtype='i8'
                                              )
                    dset[...] = parray[0][cslice]

                    # add version metadata
                    dset.attrs['version.major'] = parray[1] 
                    dset.attrs['version.minor'] = parray[2]
                    dset.attrs['version.times'] = parray[3]
                    dset.attrs['version']       = parray[4]

                    # update in memory file image
                    root.flush()
                    # save changes as image
                    afile_image = file_id.get_file_image()

                # offer afile_image for download
                self.wfile.write(afile_image)

            # end if
        # end def

if __name__ == "__main__":
    PORT = 8117
   
    pdigit = Pi()

    def main():
        with socketserver.TCPServer(("", PORT), PiHandler) as httpd:
            print('Starting server at port', PORT, 'use <Ctrl-C> to stop')
             
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
            httpd.server_close()
    # end def

    main()

    #print(pdigit('pi', 1, 2, (2020,7, 15, 17, 58)))

