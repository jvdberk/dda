import re

import datetime

class TimestampComponents(object):
    # Hierarchical time stamp parsing
    def __init__(self, tformats=(
        "%Y-%m-%d:%H:%M:%S"
      , "%Y-%m-%d:%H:%M"
      , "%Y-%m-%d:%H"
      , "%Y-%m-%d"
      , "%Y-%m"
      , "%Y"
        )):
        self._tformats = tformats
        self._ncomps = [tformat.count("%") for tformat in self._tformats]
    # end def

    def __call__(self, tstamp):
        comps = None
        for (tdx, tformat) in enumerate(self._tformats):
            try:
                comps = datetime.datetime.strptime(tstamp, tformat)
            except:
                pass
            else:
                if comps is not None:
                    # matches an allowed timestamp format
                    ncomps = self._ncomps[tdx]
                    comps = comps.timetuple()[:ncomps]
                    break
                # end if
            # end try

        return comps


class DDA(object):
    def __init__(self, start='/dda'):
        self._start = start

        # /name1/name2/../namen(V.v.YYYY-mm-dd:hh:MM:SS)[b:e:s, ..., b:e:s]
        #self._extract = re.compile(
        #        '^((?:/[^/]+?)+)(\(\d+?\.?\d*?\.?[\d+-:]*?\))?(\[.+\])?$'
        #                          )
        #/name1/name2/../namen(VERSION)[SLICE]
        self._extract = re.compile(
                '^((?:/[^/]+?)+)(\([^\)]+?\))?(\[[^\]]+\])?\.(\w+)$'
                                  )

        self._names = lambda n: n.split('/')
        self._version = re.compile('\((\d+?)\.?(\d*?)\.?([\d+-:][^\.]*?)?\)')
        self._slice = re.compile('\[((?:[^,]+?,*?)+)\]')
        self._slicecomps = re.compile(
        '(?:((?:\w+))?\|?)?((?:[-+]?\d+))?\:?((?:[-+]?\d+))?\:?((?:[-+]?\d+))?'
                                    )
        def tryint(i):
            try:
                i = int(i)
            except:
                pass
            return i
        self._slicecomp = lambda s: tuple([tryint(i) if len(i) else None
                                       for i in self._slicecomps.findall(s)[0]])

        self._timestamp_parser = TimestampComponents()
    # end def

    def __call__(self, path):
        if path[:len(self._start)] == self._start:
            names, version, cslice, ext = self._extract.findall(
                                                        path[len(self._start):]
                                                          )[0]
            names = self._names(names)[1:]
           
            if version:
                #print(version)
                version = list(self._version.findall(version)[0])
                try:
                    version[0] = int(version[0])
                except:
                    print('failed int conv version[0]')
                    version[0] = None
                try:
                    version[1] = int(version[1])
                except:
                    print('failed int conv version[1]')
                    version[1] = None
                try:
                    version[2] = self._timestamp_parser(version[2])
                except:
                    print('failed datetime conv version[2]')
                    version[2] = None

                version = tuple(version)
            else:
                version = None

            if cslice:
                #print(cslice)
                #print(self._slice.findall(cslice))
                slicecomps = self._slice.findall(cslice)[0]
                #print(slicecomps)
                #print(slicecomps.split(','))
                cslice  = tuple([self._slicecomp(sl)
                        for sl in re.split(',\s*', slicecomps)])
            else:
                cslice = None

            return (names, version, cslice, ext)
        else:
            return None
    # end def
