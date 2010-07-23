#
# Generic Makefile for C modules, wrapped in Python by SWIG.
#
# Chanege the variable INTERFACE to your interface files and if you're
# not using a sensible UNIX style platform then change the executables
# and so on too.
#


INTERFACE=Channel.i

PREFIX=/usr
RM=rm
SWIG=swig
SWIGOPT=
CC=gcc
CFLAGS=-O3 -Wall -c
LDSHARED=ld
LDFLAGS=-shared
INCLUDES=
LIBS=
SO=.so

SRCS=$(wildcard *.c) 
ISRCS=$(INTERFACE:.i=_wrap.c)
OBJS=${SRCS:.c=.o} 
IOBJS=$(ISRCS:.c=.o)

TARGET=$(addprefix _, $(INTERFACE:.i=$(SO)))

# Make sure these locate your Python installation
PYTHON_INCLUDE=-I$(PREFIX)/include/python2.6

# Clear out old suffices.
.SUFFIXES:

# List suffices that we are using.
.SUFFIXES:	.i .o .c

.PHONY:	clean

all: $(SRCS)
	$(SWIG) -python $(SWIGOPT) $(INTERFACE)
	$(CC) -c $(CCSHARED) $(CFLAGS) $(ISRCS) $(SRCS) $(INCLUDE) $(PYTHON_INCLUDE)
	$(LDSHARED) $(LDFLAGS) $(OBJS) $(IOBJS) $(LIBS) -o $(TARGET)
	@echo Built all files and created $(TARGET)

clean :
	-$(RM) -f  *.pyc *.so *.o *_wrap.c *~ 

depend :	$(SRCS)
	makedepend $(INCLUDES) $^

# DO NOT DELETE THIS LINE
