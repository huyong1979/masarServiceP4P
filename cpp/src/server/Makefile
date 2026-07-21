TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/python3.14

INC += dsl.h

LIBRARY = masarServer

SERVER = $(TOP)/src/server/

SRC_DIRS += $(SERVER)/service
INC += masarService.h
LIBSRCS += masarService.cpp

SRC_DIRS += $(SERVER)/dslPY
INC += dslPY.h
LIBSRCS += dslPY.cpp

masarServer_LIBS += gather nt pvAccess pvData Com
USR_LDFLAGS += -L${PYTHON_BASE}/lib
masarServer_SYS_LIBS += python3.14
masarServer_SYS_LIBS += dl

include $(TOP)/configure/RULES
