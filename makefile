# Makefile to create BIGsplines extension module for NumericPython
#
# Jan Kybic, August 2000
# $Id: Makefile,v 1.1 2004/06/11 14:28:25 jko Exp $
#
# Edited by Simo Tuomisto, 2010

PREFIX=/usr
LBITS=$(shell getconf LONG_BIT)

ifeq ($(LBITS),32)
LIBDIR=$(PREFIX)/lib
else
LIBDIR=$(PREFIX)/lib64
endif

INCLUDEDIR=$(PREFIX)/include

PYTHONVERSION=$(shell python -c "import sys; print sys.version[0:3]")

PYTHONINCLUDE=$(INCLUDEDIR)/python$(PYTHONVERSION)
PYTHONLIBRARY=$(LIBDIR)/python$(PYTHONVERSION)

ifeq ($(PYTHONVERSION), 2.4)
  NUMPYINCLUDE=$(PYTHONLIBRARY)/site-packages/numpy/core/include/numpy
else
  NUMPYINCLUDE=$(PYTHONLIBRARY)/dist-packages/numpy/core/include/numpy
endif
ALTNUMPYINCLUDE=/usr/lib/pymodules/python2.7/numpy/core/include/numpy/

INCLUDES=-I$(PYTHONINCLUDE) -I$(NUMPYINCLUDE) -I$(ALTNUMPYINCLUDE)
LDFLAGS=$(shell  python2.7-config --ldflags)
LD=ld -G
CFLAGS=-Wall -fPIC -O2 $(INCLUDES) -DBIGSPLINES
CC=cc

vpath %.c src
vpath %.o src
vpath %.so lib/dic
SOURCES=BIGsplines.c fiir.c splninterp.c bsplneval.c ffir.c bigsdcgr.c
OBJECTS=$(addprefix src/,$(SOURCES:.c=.o))

#############################
# osx compilation
ISDARWIN=$(shell uname)
ifeq ($(ISDARWIN), Darwin)
INCLUDES=-I /usr/local/lib/python2.7/site-packages/numpy/core/include/numpy/
CFLAGS=-Wall -fPIC -O2 $(INCLUDES) -DBIGSPLINES -DDARWIN $(shell python2.7-config --cflags)
LD=ld -arch x86_64
endif
############################


# generic compile rule
.c.o:	$(HEADERS)	
	$(CC) -c $(CFLAGS) $^ -o $@

all: BIGsplines.so

BIGsplines.so: $(OBJECTS)
	$(LD) $^ $(LDFLAGS) -o lib/dic/BIGsplines.so

clean:
	rm $(OBJECTS) lib/dic/BIGsplines.so

info:
	echo $(ISDARWIN) 
