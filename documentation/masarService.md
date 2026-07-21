EPICS masarService

# EPICS masarService

## EPICS v4 Working Group, Working Draft, 2014.04.10

Latest version:[masarService.html](masarService.html)This version:[masarService_20140410.html](masarService_20140410.html)Previous version:NoneEditors:Guobao Shen, BNLMarty Kraimer, BNL

This product is made available subject to acceptance of the [EPICS open source license.](http://epics-pvdata.sourceforge.net/LICENSE.html)

## Abstract

masarService is a service that creates, saves, and retrieves snapshots of data from a set of V3 channels.

It is one of a set of related products in the EPICS V4 control system programming environment:
[relatedDocumentsV4.html](http://epics-pvdata.sourceforge.net/relatedDocumentsV4.html)

## Status of this Document

This is the C++ and python implementation of masarService. It is currently under development.

Known Problem If ClientFactory.stop is called in ezchannelRPC.cpp then python will crash when python terminates.

## Table of Contents

## Preface

This product is available via an [open source license](http://epics-pvdata.sourceforge.net/LICENSE.html)

This is the overview for masarService, which is a service that defines, creates, and retrieves snapshots of data from a set of V3 channels.

An arbitrary number of snapshot definitions can be created and saved in a relational database. I snapshot definition defines a set of V3 channels from which to collect data.

For each shapshot definition an arbitrary set of snapshots can be obtained and saved in the relational database.

A client can retrive any saved snapshot.

This service uses pvData/pvAccess for all communication between a client and the masarSevice.

## Introduction

This document provides details about how to build masarService and some details about the implementation. This distribution includes three additional documents:

userManual[userManual.html](userManual.html)masar[masar.html](masar.html)RELEASE_NOTES.md[RELEASE_NOTES.md](RELEASE_NOTES.md)

## Building

This section provides the steps required to download masarService, build it, and create links for python.

### Downloading Masar

For now the only way to obtain the masarService is from the sourceforge mercurial repository. For example:

```
hg clone http://epics-pvdata.hg.sourceforge.net/hgroot/epics-pvdata/masarService
```

or

```
hg clone ssh://<your-sourceforge-userid>@epics-pvdata.hg.sourceforge.net/hgroot/epics-pvdata/masarSevice
```

### Creating Release.local

After cloning the masarService a RELEASE.local file for C++ must be created and the masarService must be built.

 In directory cpp/configure there is a file named ExampleRELEASE.local To create your version:

```
cd cpp/configure
cp ExampleRELEASE.local RELEASE.local
```

Edit RELEASE.local

Note that python, pvDataCPP, pvAccessCPP, and normative types must all be installed and built in order to build the masarService.

### Build

There are two top level areas that must be built: Masar itself and test.

```
cd masarService/cpp
make
cd ../test/cpp
make
```

### Python Links

Once the masarService is build the tests described in the next section can be run to check that everything has built properly.

The python code requires that that the extension modules have links to a shared library. To create these links do the following:

```
cd masarService/cpp/src/python
python generateSOLinks.py
```

Also PYTHONPATH must have definitions similar to the following:

```
export PYTHONPATH=/home/install/python2.7/lib/python2.7/site-packages/
export PYTHONPATH=$PYTHONPATH:/home/mrk/hg/masarService/cpp/src/python
export PYTHONPATH=$PYTHONPATH:/home/mrk/hg/masarService/python/src/server
export PYTHONPATH=$PYTHONPATH:/home/mrk/hg/masarService/python/src/client
export PYTHONPATH=$PYTHONPATH:/home/mrk/hg/masarService/python
```

## Testing

masarService/python/test has some python tests. This section describes C++ tests.

The gatherV3Data test require the V3 IOC provided with this project is running. It is stated via:

```
cd masarService/test/v3IOC
softIoc st.cmd
```

 An assumption here is the $EPICS_BASE/bin/$EPICS_HOST_ARCH is in the $PATH already. Otherwise, a full path should be given for softIoc, which is included in recent EPICS Base release.

The test database has 1000 records named masarExample0000, ..., masarExample0999. The first four records have types longout, stringout, bo, and mbbo. The other records are all ao records.

There are two addtional recordsi: masarExampleBoUninit and masarExampleMbboUninit. masarExampleBoUninit is a bi record that does not configure ZNAM or ONAM. masarExampleMbboUninit is an mbbo record that does not configure ZRST,...,FFVL.

There are also a number of waveform records:

```
masarExampleBigArray01
masarExampleBigArray02
masarExampleBigArray03
masarExampleBigArray04
masarExampleBigArray05
masarExampleBigArray06
masarExampleBigArray07
masarExampleBigArray08
masarExampleBigArray09
masarExampleBigArray10
masarExampleCharArray
masarExampleDoubleArray
masarExampleFloatArray
masarExampleLongArray
masarExampleShortArray
masarExampleStringArray
masarExampleUCharArray
masarExampleULongArray
masarExampleUShortArray
```

Each of the C++ example and test programs can be executed from the installed bin directory. For example on my linux machine:

```
cd masarService/test/cpp/bin/linux-x86
 ./gatherV3DataPut
```

### gatherV3DataPut

This writes values into the first ten records of the test V3 IOC. A sample run is:

```
mrk > ./gatherV3DataExample
nttable
structure
    time_t timeStamp
        long secondsPastEpoch 0
        int nanoSeconds 0
        int userTag 0
    alarm_t alarm
        int severity 0
        int status 0
        string message
    string[] label []
    string[] channelName [masarExample0000,masarExample0001,masarExample0002,masarExample0003,masarExample0004,masarExampleCharArray,masarExampleStringArray,masarExampleLongArray,masarExampleDoubleArray,masarExampleBoUninit,masarExampleMbboUninit]
    string[] stringValue [0,this is set by gatherV3DataPut,one,one,4.000000e+00,0.0,0.0,0.0,0.0,9,10]
    double[] doubleValue [0,0,0,0,4,0,0,0,0,9,10]
    long[] longValue [0,0,0,0,4,0,0,0,0,9,10]
    int[] dbrType [5,0,3,3,6,4,0,5,6,5,5]
    boolean[] isConnected [1,1,1,1,1,1,1,1,1,1,1]
    long[] secondsPastEpoch [1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781]
    int[] nanoSeconds [113560544,113579355,113584353,113590658,113593069,113597026,113601064,113602526,113603908,113605760,113606764]
    int[] timeStampTag [0,0,0,0,0,0,0,0,0,0,0]
    int[] alarmSeverity [0,0,0,0,1,0,0,0,0,0,0]
    int[] alarmStatus [0,0,0,0,4,0,0,0,0,0,0]
    string[] alarmMessage [NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM,HIGH,NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM]
    boolean[] isArray [0,0,0,0,0,1,1,1,1,0,0]
    structure[] arrayValue
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue [1,2,3,4]
        structure
            string[] stringValue [aaa,bbb,ccc,ddd]
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue [1,2,3,4]
        structure
            string[] stringValue []
            double[] doubleValue [10,100,1000,10000]
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
0x605228
```

### gatherV3DataExample

This tests gets a set of V3 channels. It produces:

```
mrk> ./gatherV3DataExample

structure
    time_t timeStamp
        long secondsPastEpoch 0
        int nanoSeconds 0
        int userTag 0
    alarm_t alarm
        int severity 0
        int status 0
        string message
    string[] label []
    string[] channelName [masarExample0000,masarExample0001,masarExample0002,masarExample0003,masarExample0004,masarExampleCharArray,masarExampleStringArray,masarExampleLongArray,masarExampleDoubleArray,masarExampleBoUninit,masarExampleMbboUninit]
    string[] stringValue [0,this is set by gatherV3DataPut,one,one,4.000000e+00,0.0,0.0,0.0,0.0,Illegal_Value,10]
    double[] doubleValue [0,0,0,0,4,0,0,0,0,0,10]
    long[] longValue [0,0,0,0,4,0,0,0,0,0,10]
    int[] dbrType [5,0,3,3,6,4,0,5,6,3,5]
    boolean[] isConnected [true,true,true,true,true,true,true,true,true,true,true]
    long[] secondsPastEpoch [1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781,1397136781]
    int[] nanoSeconds [113560544,113579355,113584353,113590658,113593069,113597026,113601064,113602526,113603908,113605760,113606764]
    int[] timeStampTag [0,0,0,0,0,0,0,0,0,0,0]
    int[] alarmSeverity [0,0,0,0,1,0,0,0,0,0,0]
    int[] alarmStatus [0,0,0,0,4,0,0,0,0,0,0]
    string[] alarmMessage [NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM,HIGH,NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM,NO_ALARM]
    boolean[] isArray [false,false,false,false,false,true,true,true,true,false,false]
    structure[] arrayValue
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue [1,2,3,4]
        structure
            string[] stringValue [aaa,bbb,ccc,ddd]
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue [1,2,3,4]
        structure
            string[] stringValue []
            double[] doubleValue [10,100,1000,10000]
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
        structure
            string[] stringValue []
            double[] doubleValue []
            int[] intValue []
boolean[] isConnected [true,true,true,true,true,true,true,true,true,true,true]
boolean[] isConnected [true,true,true,true,true,true,true,true,true,true,true]
```

### gatherV3DataTest

This tests gets a large set of V3 channels. This test also requires the test V3 database of the gather service. It must be started before running this test.

This test prints nothing if it is successfull. To run just execute:

```
mrk> pwd
/home/mrk/hg/masarService/cpp
mrk> bin/linux-x86/gatherV3DataExample
```

Thus test can also be run with a debug option. In this case it only gets data from the first 6 channels but displays lots of output.

### masarServiceRun

This is a dummy server. it just accepts a channelRPC request and always returns a PVStructure that is an NTTable.

To start the server:

```
cd masarService/cpp/bin/<arch>
 ./masarServiceRun
```

To stop the server type "exit".

The server must be run in order to run the next two tests.

### testclientRPC

This is a C++ client that makes a channelRPC request to the dummy server.

To run this test:

```
cd masarService/cpp/bin/<arch>
 ./testclientRPC
```

### testchannelRPC.py

This is a python client program that makes a channelRPC request to the dummy server.

To run this test:

```
cd masarService/python/test
python testchannelRPC.py
```

## gatherN3Data

Gather an array of V3 scalar double values. The complete set of data is presented as an NTTable. The NTTable has the optional fields alarm and timeStamp. The class definition is:

```
class GatherV3Data {
public:
    GatherV3Data(String channelNames[],int numberChannels);
    bool connect(double timeOut);
    void disconnect();
    bool get();
    bool put();
    String getMessage();
    PVStructure::shared_pointer getNTTable();
    PVIntArray *getIntArrray();
    PVDoubleArray *getDoubleValue();
    PVStringArray *getStringValue();
    PVLongArray *getSecondsPastEpoch();
    PVIntArray *getNanoSeconds();
    PVIntArray *getTimeStampTag();
    PVIntArray *getAlarmSeverity();
    PVIntArray *getAlarmStatus();
    PVStringArray *getAlarmMessage();
    PVIntArray *getDBRType();
    PVBooleanArray *getIsConnected();
    PVStringArray  *getChannelName();
};
```

where

GatherV3DataThe constructor. channelNames is the array of channelNames to gather. numberChannels is the number of channels to gather. connectConnect to V3 channels. This call blocks until all channels are connected or until timeout. timeout is the number of seconds to wait for connections. The return value is true if all channels are connected and false otherwise. If false then all channels are cleared and connect must be reissued. disconnectDisconnect from the V3 channels.getGet the current values of the V3 channels.NOTE: get MUST be called by the same thread that calls connect.The return value is true if all gets were successful. If the return value is false then getMessage can be called to get the reason. If any channel is disconnected false is returned. getMessageGet the reason why a connect or get failed.getNTTableThe data is saved as an NTTable with alarm and timeStamp. Get it.getIntValueGet the array of values for each V3 channel as int values. If the V3 datatype for the channel is not an integer type the value will always be 0.getDoubleValueGet the array of values for each V3 channel as double values. If the V3 datatype for the channel is not a numeric type the double value will always be 0.getStringValueGet the arrray of values for each V3 channel as string values.getSecondsPastEpochGet the array of secondsPastEpoch for each V3 channel. The epoch is midnight 1970 UTC time. getNanoSecondsGet the array of nanoSeconds since the seconds.getTimeStampTagGet the array of timeStamp tag for each V3 channel.getAlarmSeverityGet the array of alarmseverity value for each V3 channel. getAlarmStatusGet the array of alarm status value for each V3 channel.getAlarmMessageGet the array of alarm messages for each V3 channel. This is just the string value of the V3 status.getDBRTypeThis gets the array of native field types for each V3 channel. DBF_STRINGGet and put will use DBR_STRING as the request type.DBF_ENUMBy default, get and put will use DBR_STRING as the request type. But if a V3 record is not configured properbly, and string value is empty, use the numeric value then.DBF_CHARDBF_INTDBF_LONGFor all of these get and put will use DBR_LONG as the request type.DBF_FLOATDBF_DOUBLEFor both of these get and put will use DBR_DOUBLE as the request type.getIsConnectedGet the array of connection state for each V3 channel. getChannelNameGet the array of channel names for each V3 channel.

masarService/cpp/test/testGatherV3Data/gatherV3DataExample.cpp provides an example of how to use this class.

## Python Client

masarService/python/src/client has a set of python modules. Each implements a python class.

### channelRPC

ChannelRPC is a python class that makes a channelRPC request. If is implemented via a C extension module channelRPCPy which uses the rpcClient facliity that is provided by pvAccessCPP. Look at masarService/python/test/testchannelRPC.py for an example of how to use this class.

To see the methods:

```
mrk> python
Python 2.7 (r27:82500, Sep 16 2010, 18:03:06)
[GCC 4.5.1 20100907 (Red Hat 4.5.1-3)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from masarclient.channelRPC import ChannelRPC as ChannelRPC
>>> help(ChannelRPC)
```

### ntnameValue

NTNameValue is a python class that wraps a C++ implementation of NTNameValue. Once created it can be passed to other python methods that wrap C++ code that expects to receive an PVStructure argument. For example ChannelRPC.request expects to receive an argument that is a python object wraps a pVStructure. For example testChannelRPC has the statements:

```
from masarclient.ntnameValue import NTNameValue as NTNameValue
function = "saveMasar"
args = { "data" : "pv_name,value,status,severity,timeStamp",
         "servicename" : "servicexxx",
         "configname" : "configxxx",
         "comment" : "This is a comment"
       }

ntnv = NTNameValue(function,args)
 ...
result =  channelRPC.request(ntnv.getNTNameValue(),False)
```

To see the methods:

```
mrk> python
Python 2.7 (r27:82500, Sep 16 2010, 18:03:06)
[GCC 4.5.1 20100907 (Red Hat 4.5.1-3)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from masarclient.ntnameValue import NTNameValue as NTNameValue
>>> help(NTNameValue)
```

### nttable

NTTable is a python class that wraps a C++ implementation of NTTable. It is created by passing a python object that a wrapper for a C++ PVStructure that is an NTTable. For example ChannelRPC.request returns such and object. Look at testchannelRPC.py for an example of how this is used.

To see the methods:

```
mrk> python
Python 2.7 (r27:82500, Sep 16 2010, 18:03:06)
[GCC 4.5.1 20100907 (Red Hat 4.5.1-3)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from masarclient.nttable import NTTable as NTTable
>>> help(NTTable)
```

### alarm

Alarm is a python class is the python equivalent of PVStructure that represents an alarm, i.e. is has a severity and a message.

To see the methods:

```
mrk> python
Python 2.7 (r27:82500, Sep 16 2010, 18:03:06)
[GCC 4.5.1 20100907 (Red Hat 4.5.1-3)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from masarclient.alarm import Alarm as Alarm
>>> help(Alarm)
```

### timeStamp

TimeStamp is a python class is the python equivalent of PVStructure that represents a timeStamp, i.e. is has secondsPastEpoch and nanoSeconds within the second. It has many methods for manipulating the timeStamp.

To see the methods:

```
mrk> python
Python 2.7 (r27:82500, Sep 16 2010, 18:03:06)
[GCC 4.5.1 20100907 (Red Hat 4.5.1-3)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from masarclient.timeStamp import TimeStamp as TimeStamp
>>> help(TimeStamp)
```

Look at masarService/python/test/testTimeStamp.py for examples of how to use timeStamp.

## C++ Server

x

### service

For now this is only handles requests that are implemented by dslPY. Later it will ???. For now it :

- accepts the argument from request and checks to see if it is a NTNameValue. If it is not it returns NTTable with a alarm that reports failue.
- Checks to see that the NTNameValue has a function that is implemented by dslRDB. If it is not it returns NTTable with a alarm that reports failue.
- It calls dslRdb and returns the NTTable returned by dslRdb

### dsl.h - Data Source Layer

This is the interface the Data Source Layer must implement. It will be called by service. The class definition is:

```
class DSL {
public:
    PVStructure::shared_pointer request(PVStructure pvArgument);
};
```

Thus it takes a single argument which is a NTNameValue, performs whatever database action is required, and returns a PVStructure that must be an NTTable.

### dslPy

This is the C++ code that calls the python code that access the relational database.

## Python Server

x

## Python support for Standard Structures

Examples of Standard Structure are timeStamp and alarm. For each supported structure:

1. The actual data is kept in a C++ object for the type.
2. A python extension module wraps the C++ object.
3. A python class is provided that calls the extension module.
4. So that the C++ object can be passed to other C++ objects via python a python class method is provided that returns a python object that "wraps" a "void *" that is the address of the C++ object.

Alarm is an example. The python class is masarService/python/src/client/alarm.py. The extension modile is masarService/cpp/src/python/alarmPy.cpp.

alarm.py has methods equivalent to what alarm.h provides. In particular it has methods:

__init__This is the constructor__del__This is the destructor__str__This returns a string showing the current alarm values.getAlarmPyThis method returns a python object thet can be passed to another python object which calls a C++ wrapper that extracts the C++ object pointer so that it can pass it to other C++ code.getMessageGet the current alarm message.setMessageSet the current alarm message.getSeverityGet the current alarm severity as a string.setSeveritySet the current alarm severity via a string.getStatusGet the current alarm status as a string.setStatusSet the current alarm status via a string.getSeverityChoicesGet a tuple of the severity choices.getStatusChoicesGet a tuple of the status choices.

Each of these has a corresponding function in alarmPy.cpp.

## Python support for Normative Types

This is similar to the support for standard structures with the following differences:

- The C++ extension module has a shared pointer to the PVStructure associated with the NT type.
- The PyObject that "wraps" a "void *" pointer wraps a "PVStructure::shared_pointer *".

## Python support for pvAccess

At present there is only python suppport for making a channelRPC request. Again there is a python class masarService/python/src/client/channelRPC.py which makes calls to masarService/cpp/src/python/channelRPCPy.cpp. The C++ extension "wraps" rpcClient from pvAccessCPP.
