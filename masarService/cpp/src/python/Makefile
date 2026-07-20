TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/python3.14

LIBSRCS += alarmPy.cpp
LIBSRCS += timeStampPy.cpp
LIBSRCS += channelRPCPy.cpp
LIBSRCS += ntnameValuePy.cpp
LIBSRCS += nttablePy.cpp
LIBSRCS += gatherV3DataPy.cpp

LIBRARY = masarPy

masarPy_LIBS += gather nt pvAccess pvData Com
masarPy_SYS_LIBS += dl

USR_LDFLAGS += -L${PYTHON_BASE}/lib
masarPy_SYS_LIBS += python3.14

include $(TOP)/configure/RULES
