TOP = ../..
include $(TOP)/configure/CONFIG
USR_INCLUDES += -I${PYTHON_BASE}/include/python3.14


PROD_HOST += masarServiceRun
masarServiceRun_SRCS += masarServiceRun.cpp
masarServiceRun_LIBS += masarServer gather nt pvAccess pvData Com
USR_LDFLAGS += -L${PYTHON_BASE}/lib
masarServiceRun_SYS_LIBS += python3.14

# Needed on RHEL/CentOS
USR_SYS_LIBS += util

include $(TOP)/configure/RULES
