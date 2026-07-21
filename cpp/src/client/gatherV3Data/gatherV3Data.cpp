/* gatherV3Data.cpp */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#include <stdexcept>
#include <vector>
#include <sstream>

#include <epicsExit.h>
#include <alarm.h>
#include <alarmString.h>

#include <pv/nttable.h>
#include <pv/gatherV3Data.h>

namespace epics { namespace pvAccess {

using namespace epics::pvData;
using namespace epics::nt;
using std::tr1::static_pointer_cast;
using std::cout;
using std::endl;
typedef std::string String;

template<typename PVArrPtr>
static typename PVArrPtr::element_type::svector reuseArray(const PVArrPtr& arr)
{
    return arr->reuse();
}

template<typename PVArrPtr, typename Vec>
static void replaceFromVector(const PVArrPtr& arr, const Vec& in)
{
    typedef typename PVArrPtr::element_type PVArr;
    typename PVArr::svector tmp(in.size());
    for(size_t i = 0; i < in.size(); ++i) {
        tmp[i] = in[i];
    }
    arr->replace(freeze(tmp));
}

static PVFieldPtr getNTTableFieldByIndex(const NTTablePtr& ntTable, size_t index)
{
    const StringArray& columns = ntTable->getColumnNames();
    if(index>=columns.size()) return PVFieldPtr();
    return ntTable->getColumn(columns[index]);
}

struct GatherV3DataPvt;

enum State {
    idle,
    connecting,
    connected,
    getting,
    putting,
    destroying,
};

enum V3RequestType {
    requestDouble,
    requestLong,
    requestString
};

struct ChannelID
{
    GatherV3DataPvt *pvt;
    chid theChid;
    int offset;
    V3RequestType requestType;
    int elementLength;
    bool getIsConnected;
    dbr_short_t     status;
    dbr_short_t     severity;
    epicsTimeStamp  stamp;         
};

struct GatherV3DataPvt
{
    GatherV3DataPvt(
        bool hasFunction,bool hasTimeStamp, bool hasAlarm,
        StringArray const & valueNames,
        FieldConstPtrArray const &valueFields);
    ~GatherV3DataPvt(){}
    void getOne(int index);
    Mutex mutex;
    Event event;
    PVTimeStamp pvtimeStamp;
    TimeStamp timeStamp;
    PVAlarm pvalarm;
    Alarm alarm;
    String message;
    NTTablePtr nttable;
    PVStructurePtr pvStructure;
    int numberChannels;
    std::vector<ChannelID *> apchannelID; // array of  pointer to ChanneID
    PVDoubleArrayPtr pvdoubleValue;
    PVLongArrayPtr pvlongValue;
    PVStringArrayPtr pvstringValue;
    PVStructureArrayPtr pvarrayValue;
    PVLongArrayPtr pvsecondsPastEpoch;
    PVIntArrayPtr pvnanoSeconds;
    PVIntArrayPtr pvtimeStampTag;
    PVIntArrayPtr pvalarmSeverity;
    PVIntArrayPtr pvalarmStatus;
    PVStringArrayPtr pvalarmMessage;
    PVIntArrayPtr pvDBRType;
    PVBooleanArrayPtr pvisArray;
    PVBooleanArrayPtr pvisConnected;
    PVStringArrayPtr pvchannelName;
    State state;
    int numberConnected;
    int numberCallbacks;
    bool requestOK;
    epicsThreadId threadId;
};

GatherV3DataPvt::GatherV3DataPvt(
    bool hasFunction,bool hasTimeStamp, bool hasAlarm,
    StringArray const & valueNames,
    FieldConstPtrArray const &valueFields)
:
 nttable()
{
   (void)hasFunction;
   NTTableBuilderPtr builder = NTTable::createBuilder();
   if(hasTimeStamp) builder->addTimeStamp();
   if(hasAlarm) builder->addAlarm();
   for(size_t i = 0; i < valueNames.size(); ++i) {
       if(valueFields[i]->getType()==scalarArray) {
           ScalarArrayConstPtr arr = static_pointer_cast<const ScalarArray>(valueFields[i]);
           builder->addColumn(valueNames[i], arr->getElementType());
       } else {
           builder->add(valueNames[i], valueFields[i]);
       }
   }
   nttable = builder->create();
   pvStructure = nttable->getPVStructure();
}

// concatenate a new message onto message
static void messageCat(
    GatherV3DataPvt *pvt,const char *cafunc,int castatus,int channel)
{
    String name = pvt->pvchannelName->view()[channel];
    String buf = String(cafunc);
    buf += " ";
    buf += String(ca_message(castatus));
    buf += " for channel ";
    buf += name;
    pvt->message += buf;
}

static void connectionCallback(struct connection_handler_args args)
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DataPvt * pvt = id->pvt;
    if(pvt->state==destroying) return;
    int offset = id->offset;

    PVBooleanArray::svector data = reuseArray(pvt->pvisConnected);
    bool isConnected = data[offset];
    bool newState = ((ca_state(chid)==cs_conn) ? true : false);
    if(isConnected==newState) {
        printf("gatherV3Data connectionCallback."
               " Why extra connection callback?\n");
        return;
    }
    data[offset] = newState;
    pvt->pvisConnected->replace(freeze(data));
    Lock xx(pvt->mutex);
    if(newState) {
        int dbrType = ca_field_type(chid);
        unsigned long numberElements = ca_element_count(chid);
        switch(dbrType) {
        case DBF_STRING:
        case DBF_ENUM:
            id->requestType = requestString; break;
        case DBF_CHAR:
        case DBF_SHORT:
        case DBF_LONG:
            id->requestType = requestLong; break;
        case DBF_FLOAT:
        case DBF_DOUBLE:
            id->requestType = requestDouble; break;
        default:
            printf("warning %s has unsupported type %d\n",
                ca_name(chid),dbrType);
            id->requestType = requestString; break;
        }
        PVIntArray::svector pvalue = reuseArray(pvt->pvDBRType);
        pvalue[offset] = dbrType;
        pvt->pvDBRType->replace(freeze(pvalue));
        PVBooleanArray::svector isArray = reuseArray(pvt->pvisArray);
        if(numberElements==1) {
            isArray[offset] = false;
        } else {
            isArray[offset] = true;
        }
        pvt->pvisArray->replace(freeze(isArray));
        pvt->numberConnected++;
        if(pvt->state==connecting && pvt->numberConnected==pvt->numberChannels) {
            pvt->event.signal();
        }
        return;
    }
    pvt->numberConnected--;
}

static void getCallback ( struct event_handler_args args )
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DataPvt * pvt = id->pvt;
    if(pvt->state!=getting) return;
    int offset = id->offset;
    Lock xx(pvt->mutex);
    pvt->numberCallbacks++;
    if ( args.status != ECA_NORMAL ) {
          messageCat(pvt,"getCallback",args.status,offset);
          if(pvt->numberCallbacks==pvt->numberChannels) {
              pvt->event.signal();
          }
          return;
    }
    id->getIsConnected = true;
    unsigned long numberElements = args.count;
    // all DBR_TIME_XXX start with status,severity, timeStamp
    const struct dbr_time_double * pTime =
         ( const struct dbr_time_double * ) args.dbr;
    id->severity = pTime->severity;
    id->status = pTime->status;
    id->stamp = pTime->stamp;
    boolean isArray = pvt->pvisArray->view()[offset];
    if(!isArray) {
        if(id->requestType==requestDouble) {
            const struct dbr_time_double * pTD =
                 ( const struct dbr_time_double * ) args.dbr;
            // set double value
            PVDoubleArray::svector pvalue = reuseArray(pvt->pvdoubleValue);
            pvalue[offset] = pTD->value;
            pvt->pvdoubleValue->replace(freeze(pvalue));
    
            // convert double value to string
            PVStringArray::svector pstring = reuseArray(pvt->pvstringValue);
            char buffer[20];
            sprintf(buffer,"%e",pTD->value);
            pstring[offset] = String(buffer);
            pvt->pvstringValue->replace(freeze(pstring));
    
            // put the integer part to keep at least some information.
            PVLongArray::svector plvalue = reuseArray(pvt->pvlongValue);
            plvalue[offset] = pTD->value;
            pvt->pvlongValue->replace(freeze(plvalue));
        } else if(id->requestType==requestLong) {
            const struct dbr_time_long * pTL =
                 ( const struct dbr_time_long * ) args.dbr;
            // set long value as 64-bit
            PVLongArray::svector pvalue = reuseArray(pvt->pvlongValue);
            pvalue[offset] = pTL->value;
            pvt->pvlongValue->replace(freeze(pvalue));
    
            // put 64-bit long to a double array
            PVDoubleArray::svector dvalue = reuseArray(pvt->pvdoubleValue);
            dvalue[offset] = pTL->value;
            pvt->pvdoubleValue->replace(freeze(dvalue));
    
            // convert long value to a string
            char buffer[20];
            sprintf(buffer,"%d",pTL->value);
            PVStringArray::svector svalue = reuseArray(pvt->pvstringValue);
            svalue[offset] = String(buffer);
            pvt->pvstringValue->replace(freeze(svalue));
        } else if(id->requestType==requestString) {
            const struct dbr_time_string * pTS =
                 ( const struct dbr_time_string * ) args.dbr;
            // set to string array only
            PVStringArray::svector svalue = reuseArray(pvt->pvstringValue);
            svalue[offset] = String(pTS->value);
            pvt->pvstringValue->replace(freeze(svalue));
            if(pTS->value[0]==0) {
                pvt->numberCallbacks-- ;
                PVIntArray::svector pvalue = reuseArray(pvt->pvDBRType);
                pvalue[offset] = DBF_LONG;
                pvt->pvDBRType->replace(freeze(pvalue));
                id->requestType = requestLong;
                id->getIsConnected = false;
                pvt->getOne(id->offset);
                ca_flush_io();
            }
        } else {
            throw std::logic_error("unknown DBR_TYPE");
        }
    } else {
        PVStructurePtr pvStructure = pvt->pvarrayValue->view()[offset];
        PVFieldPtrArray pvfields = pvStructure->getPVFields();
        PVStringArrayPtr pvstringarray = static_pointer_cast<PVStringArray>(pvfields[0]);
        PVDoubleArrayPtr pvdoublearray = static_pointer_cast<PVDoubleArray>(pvfields[1]);
        PVIntArrayPtr pvintarray = static_pointer_cast<PVIntArray>(pvfields[2]);
        if(id->requestType==requestDouble) {
            const struct dbr_time_double * pTD =
                 ( const struct dbr_time_double * ) args.dbr;
            // set double value
            PVDoubleArray::svector pvalue(numberElements);
            memcpy(&pvalue[0],&pTD->value,numberElements*sizeof(double));
            pvdoublearray->replace(freeze(pvalue));
        } else if(id->requestType==requestLong) {
            const struct dbr_time_long * pTL =
                 ( const struct dbr_time_long * ) args.dbr;
            // set long value as 32-bit
            PVIntArray::svector pvalue(numberElements);
            memcpy(&pvalue[0],&pTL->value,numberElements*sizeof(int32));
            pvintarray->replace(freeze(pvalue));
        } else if(id->requestType==requestString) {
            const struct dbr_time_string * pTS =
                 ( const struct dbr_time_string * ) args.dbr;
            // set to string array only
            PVStringArray::svector pvalue(numberElements);
            const char *pfrom = pTS->value;
            for(unsigned long i=0; i<numberElements; i++) {
                pvalue[i] = String(pfrom);
                pfrom += MAX_STRING_SIZE;
            }
            pvstringarray->replace(freeze(pvalue));
        } else {
            throw std::logic_error("unknown DBR_TYPE");
        }
    }

    if(pvt->numberCallbacks==pvt->numberConnected) {
        pvt->event.signal();
    }
}

void GatherV3DataPvt::getOne(int i)
{
    ChannelID *channelId = apchannelID[i];
    chid theChid = channelId->theChid;
    V3RequestType requestType = channelId->requestType;
    int req = DBR_TIME_DOUBLE;
    if(requestType==requestLong) req = DBR_TIME_LONG;
    if(requestType==requestString) req = DBR_TIME_STRING;
    int result = ca_array_get_callback(
        req,
        0,
        theChid,
        getCallback,
        channelId);
    if(result==ECA_NORMAL) return;
    if(result==ECA_DISCONN) {
        messageCat(this,"ca_get_callback",ECA_DISCONN,i);
        channelId->getIsConnected = false;
        this->requestOK = false;
        return;
    }
    if(result!=ECA_NORMAL) {
        messageCat(this,"ca_get_callback",result,i);
        this->requestOK = false;
    }
}

static void putCallback ( struct event_handler_args args )
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DataPvt * pvt = id->pvt;
    if(pvt->state!=putting) return;
    int offset = id->offset;
    Lock xx(pvt->mutex);
    pvt->numberCallbacks++;
    if ( args.status != ECA_NORMAL ) {
          messageCat(pvt,"putCallback",args.status,offset);
          if(pvt->numberCallbacks==pvt->numberChannels) {
              pvt->event.signal();
          }
          return;
    }
    if(pvt->numberCallbacks==pvt->numberChannels) {
        pvt->event.signal();
    }
}

GatherV3Data::GatherV3Data(
    StringArray const & channelNames,
    int numberChannels)
: pvt(0)
{
    FieldCreatePtr fieldCreate = getFieldCreate();
    size_t naf = 3;
    StringArray names;
    names.reserve(naf);
    FieldConstPtrArray arrfields;
    arrfields.reserve(naf);
    names.push_back("stringValue");
    names.push_back("doubleValue");
    names.push_back("intValue");
    arrfields.push_back(fieldCreate->createScalarArray(pvString));
    arrfields.push_back(fieldCreate->createScalarArray(pvDouble));
    arrfields.push_back(fieldCreate->createScalarArray(pvInt));
    StructureConstPtr arrStructure = fieldCreate->createStructure(
         names,arrfields);
    int n = 14;
    StringArray fieldNames;
    fieldNames.reserve(n);
    FieldConstPtrArray fields;
    fields.reserve(n);
    // The order is mapped into SQL query sequence to keep data format consistency.
    // Update RDB query each time when fields order is changed.
    // fields order & type
    // 'pv name', 'string value', 'double value', 'long value',
    // string,     string,         double,         long,      ,
    // 'array value',     'isArray', 'dbr type', 'isConnected',
    // structureArray,     boolean,   int,        boolean,
    // 'secondsPastEpoch', 'nanoSeconds', 'timeStampTag',
    // long,                int,           int,          
    // 'alarmSeverity', 'alarmStatus', 'alarmMessage'
    //  int,             int,           string
    fieldNames.push_back("channelName");
    fieldNames.push_back("stringValue");
    fieldNames.push_back("doubleValue");
    fieldNames.push_back("longValue");
    fieldNames.push_back("dbrType");
    fieldNames.push_back("isConnected");
    fieldNames.push_back("secondsPastEpoch");
    fieldNames.push_back("nanoSeconds");
    fieldNames.push_back("timeStampTag");
    fieldNames.push_back("alarmSeverity");
    fieldNames.push_back("alarmStatus");
    fieldNames.push_back("alarmMessage");
    fieldNames.push_back("isArray");
    fieldNames.push_back("arrayValue");
    fields.push_back(fieldCreate->createScalarArray(pvString));
    fields.push_back(fieldCreate->createScalarArray(pvString));
    fields.push_back(fieldCreate->createScalarArray(pvDouble));
    fields.push_back(fieldCreate->createScalarArray(pvLong));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    fields.push_back(fieldCreate->createScalarArray(pvLong));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvInt));
    fields.push_back(fieldCreate->createScalarArray(pvString));
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    fields.push_back(fieldCreate->createStructureArray(arrStructure));
    

    pvt = new GatherV3DataPvt(false,true,true,fieldNames,fields);
    pvt->nttable->attachTimeStamp(pvt->pvtimeStamp);
    pvt->nttable->attachAlarm(pvt->pvalarm);
    pvt->pvtimeStamp.attach(pvt->pvStructure->getSubField("timeStamp"));
    pvt->pvalarm.attach(pvt->pvStructure->getSubField("alarm"));
    pvt->numberChannels = numberChannels;
//    ChannelID **apchannelID = new ChannelID*[numberChannels];
    pvt->apchannelID.resize(numberChannels);
    for(int i=0; i<numberChannels; i++) {
        ChannelID *pChannelID = new ChannelID();
        pChannelID->pvt = pvt;
        pChannelID->theChid = 0;
        pChannelID->offset = i;
        pChannelID->requestType = requestString;
        pChannelID->elementLength = 1;
        pChannelID->getIsConnected = false;
        pChannelID->status = epicsAlarmUDF;
        pChannelID->severity = epicsSevInvalid;
        pChannelID->stamp.secPastEpoch = 0;
        pChannelID->stamp.nsec = 0;
        pvt->apchannelID[i] = pChannelID;
    }

    pvt->pvchannelName = pvt->nttable->getColumn<PVStringArray>("channelName");
    pvt->pvchannelName->setCapacity(numberChannels);
    pvt->pvchannelName->setCapacityMutable(false);
    replaceFromVector(pvt->pvchannelName, channelNames);

    pvt->pvstringValue = pvt->nttable->getColumn<PVStringArray>("stringValue");
    pvt->pvstringValue->setCapacity(numberChannels);
    pvt->pvstringValue->setCapacityMutable(false);
    PVStringArray::svector pstrings(numberChannels);
    for (int i=0; i<numberChannels; i++) {
         pstrings[i] = String("0.0");
    }

    pvt->pvstringValue->replace(freeze(pstrings));

    pvt->pvdoubleValue = pvt->nttable->getColumn<PVDoubleArray>("doubleValue");
    pvt->pvdoubleValue->setCapacity(numberChannels);
    pvt->pvdoubleValue->setCapacityMutable(false);
    PVDoubleArray::svector pdouble(numberChannels);
    for (int i=0; i<numberChannels; i++) pdouble[i] = 0.0;
    pvt->pvdoubleValue->replace(freeze(pdouble));

    pvt->pvlongValue = pvt->nttable->getColumn<PVLongArray>("longValue");
    pvt->pvlongValue->setCapacity(numberChannels);
    pvt->pvlongValue->setCapacityMutable(false);
    PVLongArray::svector plong(numberChannels);
    for (int i=0; i<numberChannels; i++) plong[i] = 0.0;
    pvt->pvlongValue->replace(freeze(plong));

    pvt->pvDBRType = pvt->nttable->getColumn<PVIntArray>("dbrType");
    pvt->pvDBRType->setCapacity(numberChannels);
    pvt->pvDBRType->setCapacityMutable(false);
    PVIntArray::svector pDBRType(numberChannels);
    for (int i=0; i<numberChannels; i++) pDBRType[i] = DBF_NO_ACCESS;
    pvt->pvDBRType->replace(freeze(pDBRType));

    pvt->pvisConnected = pvt->nttable->getColumn<PVBooleanArray>("isConnected");
    pvt->pvisConnected->setCapacity(numberChannels);
    pvt->pvisConnected->setCapacityMutable(false);
    PVBooleanArray::svector pbool(numberChannels);
    for (int i=0; i<numberChannels; i++) pbool[i] = false;
    pvt->pvisConnected->replace(freeze(pbool));

    pvt->pvsecondsPastEpoch = pvt->nttable->getColumn<PVLongArray>("secondsPastEpoch");
    pvt->pvsecondsPastEpoch->setCapacity(numberChannels);
    pvt->pvsecondsPastEpoch->setCapacityMutable(false);
    PVLongArray::svector psecondsPastEpoch(numberChannels);
    for (int i=0; i<numberChannels; i++) psecondsPastEpoch[i] = 0;
    pvt->pvsecondsPastEpoch->replace(freeze(psecondsPastEpoch));

    pvt->pvnanoSeconds = pvt->nttable->getColumn<PVIntArray>("nanoSeconds");
    pvt->pvnanoSeconds->setCapacity(numberChannels);
    pvt->pvnanoSeconds->setCapacityMutable(false);
    PVIntArray::svector pnanoSeconds(numberChannels);
    for (int i=0; i<numberChannels; i++) pnanoSeconds[i] = 0;
    pvt->pvnanoSeconds->replace(freeze(pnanoSeconds));

    pvt->pvtimeStampTag = pvt->nttable->getColumn<PVIntArray>("timeStampTag");
    pvt->pvtimeStampTag->setCapacity(numberChannels);
    pvt->pvtimeStampTag->setCapacityMutable(false);
    PVIntArray::svector ptimeStampTag(numberChannels);
    for (int i=0; i<numberChannels; i++) ptimeStampTag[i] = 0;
    pvt->pvtimeStampTag->replace(freeze(ptimeStampTag));

    pvt->pvalarmSeverity = pvt->nttable->getColumn<PVIntArray>("alarmSeverity");
    pvt->pvalarmSeverity->setCapacity(numberChannels);
    pvt->pvalarmSeverity->setCapacityMutable(false);
    PVIntArray::svector palarmSeverity(numberChannels);
    for (int i=0; i<numberChannels; i++) palarmSeverity[i] = INVALID_ALARM;
    pvt->pvalarmSeverity->replace(freeze(palarmSeverity));

    pvt->pvalarmStatus = pvt->nttable->getColumn<PVIntArray>("alarmStatus");
    pvt->pvalarmStatus->setCapacity(numberChannels);
    pvt->pvalarmStatus->setCapacityMutable(false);
    PVIntArray::svector palarmStatus(numberChannels);
    for (int i=0; i<numberChannels; i++) palarmStatus[i] = epicsAlarmComm;
    pvt->pvalarmStatus->replace(freeze(palarmStatus));

    pvt->pvalarmMessage = pvt->nttable->getColumn<PVStringArray>("alarmMessage");
    pvt->pvalarmMessage->setCapacity(numberChannels);
    pvt->pvalarmMessage->setCapacityMutable(false);
    PVStringArray::svector palarmMessage(numberChannels);
    for (int i=0; i<numberChannels; i++) palarmMessage[i] = String();
    pvt->pvalarmMessage->replace(freeze(palarmMessage));

    pvt->pvisArray = pvt->nttable->getColumn<PVBooleanArray>("isArray");
    pvt->pvisArray->setCapacity(numberChannels);
    pvt->pvisArray->setCapacityMutable(false);
    pbool.resize(numberChannels);
    for (int i=0; i<numberChannels; i++) pbool[i] = false;
    pvt->pvisArray->replace(freeze(pbool));

    pvt->pvarrayValue = pvt->pvStructure->getSubField<PVStructureArray>("arrayValue");
    if(!pvt->pvarrayValue) {
        throw std::runtime_error("Failed to get arrayValue field from NTTable.");
    }
    pvt->pvarrayValue->setCapacity(numberChannels);
    pvt->pvarrayValue->setCapacityMutable(false);
    PVStructureArray::svector ppPVStructure(numberChannels);
    StructureConstPtr pstructure
        = pvt->pvarrayValue->getStructureArray()->getStructure();
    PVDataCreatePtr pvDataCreate = getPVDataCreate();
    for (int i=0; i<numberChannels; i++) {
        ppPVStructure[i] = pvDataCreate->createPVStructure(pstructure);
    }
    pvt->pvarrayValue->replace(freeze(ppPVStructure));

    pvt->state = idle;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = false;
    pvt->threadId = 0;
}

GatherV3Data::~GatherV3Data()
{
    if(pvt->state!=idle) disconnect();
    for(int i=0; i<pvt->numberChannels; i++) {
        ChannelID *pChannelID = pvt->apchannelID[i];
        delete pChannelID;
    }
    delete pvt;
}

bool GatherV3Data::connect(double timeOut)
{
    if(pvt->state!=idle) {
        throw std::logic_error(
            "GatherV3Data::connect only legal when state is idle\n");
    }
    SEVCHK(ca_context_create(ca_enable_preemptive_callback),"ca_context_create");
    pvt->threadId = epicsThreadGetIdSelf();
    pvt->state = connecting;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->event.tryWait();
    int numberChannels = pvt->numberChannels;
    PVBooleanArray::svector isConnected = reuseArray(pvt->pvisConnected);
    PVStringArray::const_svector channelNames = pvt->pvchannelName->view();
    for(int i=0; i< numberChannels; i++) {
        isConnected[i] = false;
        const char * channelName = channelNames[i].c_str();
        ChannelID *pchannelID = pvt->apchannelID[i];
        int result = ca_create_channel(
           channelName,
           connectionCallback,
           pchannelID,
           20,
           &pchannelID->theChid);
        if(result!=ECA_NORMAL) {
            printf("%s ca_create_channel failed %s\n",
               channelName,ca_message(result));
        }
    }
    pvt->pvisConnected->replace(freeze(isConnected));
    ca_flush_io();
    std::stringstream ss;
    while(true) {
        int oldNumber = pvt->numberConnected;
        bool result = pvt->event.wait(timeOut);
        if(result && pvt->requestOK) {
            pvt->state = connected;
            return pvt->requestOK;
        }
        if(pvt->numberConnected!=pvt->numberChannels) {
            ss.str("");
            ss << (pvt->numberChannels - pvt->numberConnected);
            String buf = ss.str();
            buf += " channels of ";
            ss.str("");
            ss << pvt->numberChannels;
            buf += ss.str();
            buf += " are not connected.";
            pvt->message = buf;
            pvt->alarm.setMessage(pvt->message);
            pvt->alarm.setSeverity(invalidAlarm);
            pvt->alarm.setStatus(clientStatus);
        }
        if(oldNumber==pvt->numberConnected) {
            pvt->state = connected;
            return false;
        }
        timeOut = 1.0;
    }
    return false;
}

void GatherV3Data::disconnect()
{
    Lock xx(pvt->mutex);
    if(pvt->state==idle) return;
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3Data::disconnect must be same thread that called connect\n");
    }
    int numberChannels = pvt->numberChannels;
    pvt->state = destroying;
    for(int i=0; i< numberChannels; i++) {
        chid theChid = pvt->apchannelID[i]->theChid;
        ca_clear_channel(theChid);
    }
    ca_context_destroy();
    pvt->state = idle;
}


bool GatherV3Data::get()
{
    if(pvt->state!=connected) {
        throw std::logic_error("GatherV3Data::get illegal state\n");
    }
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3Data::get must be same thread that called connect\n");
    }
    pvt->state = getting;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->message = String();
    pvt->event.tryWait();
    pvt->timeStamp.getCurrent();
    pvt->alarm.setMessage("");
    pvt->alarm.setSeverity(noAlarm);
    pvt->alarm.setStatus(noStatus);
    for(int i=0; i< pvt->numberChannels; i++) {
        pvt->getOne(i);
    }
    ca_flush_io();
    bool result = false;
    while(true) {
        int oldNumber = pvt->numberCallbacks;
        result = pvt->event.wait(1.0);
        if(result) break;
        if(pvt->numberCallbacks==oldNumber) break;
    }
    if(!result) {
        pvt->message += " timeout";
        pvt->requestOK = false;
        pvt->alarm.setMessage(pvt->message);
        pvt->alarm.setSeverity(invalidAlarm);
        pvt->alarm.setStatus(clientStatus);
    }
    int numberChannels = pvt->numberChannels;
    PVBooleanArray::svector isConnected = reuseArray(pvt->pvisConnected);
    PVLongArray::svector secondsPastEpoch = reuseArray(pvt->pvsecondsPastEpoch);
    PVIntArray::svector nanoSeconds = reuseArray(pvt->pvnanoSeconds);
    PVIntArray::svector alarmSeverity = reuseArray(pvt->pvalarmSeverity);
    PVIntArray::svector alarmStatus = reuseArray(pvt->pvalarmStatus);
    PVStringArray::svector alarmMessage = reuseArray(pvt->pvalarmMessage);
    for(int i=0; i<numberChannels; i++) {
        ChannelID *pID = pvt->apchannelID[i];
        isConnected[i] = pID->getIsConnected;
        // pID->stamp.secPastEpoch should be 0 if record is not processed yet.
        // otherwise, use EPOCH time.
        if (pID->stamp.secPastEpoch > posixEpochAtEpicsEpoch)
            secondsPastEpoch[i] =
                pID->stamp.secPastEpoch + posixEpochAtEpicsEpoch;
        nanoSeconds[i] = pID->stamp.nsec;
        alarmSeverity[i] = pID->severity;
        alarmStatus[i] = pID->status;
        alarmMessage[i] = String(epicsAlarmConditionStrings[pID->status]);
        if(pvt->alarm.getSeverity()<pID->severity) {
            pvt->alarm.setSeverity(static_cast<AlarmSeverity>(alarmSeverity[i]));
            pvt->alarm.setStatus(static_cast<AlarmStatus>(alarmStatus[i]));
            pvt->alarm.setMessage(alarmMessage[i]);
        }
    }
    pvt->pvisConnected->replace(freeze(isConnected));
    pvt->pvsecondsPastEpoch->replace(freeze(secondsPastEpoch));
    pvt->pvnanoSeconds->replace(freeze(nanoSeconds));
    pvt->pvalarmSeverity->replace(freeze(alarmSeverity));
    pvt->pvalarmStatus->replace(freeze(alarmStatus));
    pvt->pvalarmMessage->replace(freeze(alarmMessage));
    pvt->state = connected;
    return pvt->requestOK;
}

bool GatherV3Data::put()
{
    if(pvt->state!=connected) {
        throw std::logic_error("GatherV3Data::put illegal state\n");
    }
    if(pvt->threadId!=epicsThreadGetIdSelf()) {
        throw std::logic_error(
            "GatherV3Data::put must be same thread that called connect\n");
    }
    pvt->state = putting;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->message = String();
    pvt->event.tryWait();
    pvt->timeStamp.getCurrent();
    pvt->alarm.setMessage("");
    pvt->alarm.setSeverity(noAlarm);
    pvt->alarm.setStatus(noStatus);
    PVLongArray::const_svector plvalue = pvt->pvlongValue->view();
    PVDoubleArray::const_svector pdvalue = pvt->pvdoubleValue->view();
    PVStringArray::const_svector psvalue = pvt->pvstringValue->view();
    PVStructureArray::const_svector parrayvalue = pvt->pvarrayValue->view();
    PVBooleanArray::const_svector isArray = pvt->pvisArray->view();
    for(int i=0; i< pvt->numberChannels; i++) {
        ChannelID *channelId = pvt->apchannelID[i];
        chid theChid = channelId->theChid;
        V3RequestType requestType = channelId->requestType;
        PVIntArray::const_svector intArrayBuf;
        PVDoubleArray::const_svector doubleArrayBuf;
        unsigned long count = 1;
        unsigned long sizebuf = 0;
        char *buffer = 0;
        const void *pdata = 0;
        int req = 0;
        if(isArray[i]) {
            switch(requestType) {
                case requestLong: {
                     req = DBR_LONG;
                     PVIntArrayPtr pvvalue = parrayvalue[i]->getSubField<PVIntArray>("intValue");
                     count = pvvalue->getLength();
                     intArrayBuf = pvvalue->view();
                     pdata = intArrayBuf.empty() ? 0 : &intArrayBuf[0];
                }
                break;
                case requestDouble: {
                    req = DBR_DOUBLE;
                    PVDoubleArrayPtr pvvalue = parrayvalue[i]->getSubField<PVDoubleArray>("doubleValue");
                    count = pvvalue->getLength();
                    doubleArrayBuf = pvvalue->view();
                    pdata = doubleArrayBuf.empty() ? 0 : &doubleArrayBuf[0];
                }
                break;
                case requestString: {
                    req = DBR_STRING;
                    PVStringArrayPtr pvvalue = parrayvalue[i]->getSubField<PVStringArray>("stringValue");
                    int length = pvvalue->getLength();
                    PVStringArray::const_svector values = pvvalue->view();
                    sizebuf = length*MAX_STRING_SIZE;
                    count = length;
                    buffer = new char[sizebuf];
                    memset(buffer,0,sizebuf);
                    pdata = buffer;
                    char *p = buffer;
                    for(int j=0; j< length; j++) {
                        String value = values[j];
                        const char *pfrom = value.c_str();
                        int num = value.length();
                        if(num>=MAX_STRING_SIZE) num = MAX_STRING_SIZE-1;
                        memcpy(p,pfrom,num);
                        p += MAX_STRING_SIZE;
                    }
                }
                break;
            default:
                 printf(
                     "%s warning gatherV3Data::put has unsupported type %d\n",
                     ca_name(theChid),requestType);
                    
            }
        } else {
            switch(requestType) {
            case requestLong:
                req = DBR_LONG; pdata = &plvalue[i]; break;
            case requestDouble:
                req = DBR_DOUBLE; pdata = &pdvalue[i]; break;
            case requestString:
                req = DBR_STRING; pdata = psvalue[i].c_str();
                break;
            }
        }
        int result = ca_array_put_callback(
            req,
            count,
            theChid,
            pdata,
            putCallback,
            pvt->apchannelID[i]);
        if(result!=ECA_NORMAL) {
            messageCat(pvt,"ca_put_callback",result,i);
            pvt->requestOK = false;
        }
        if(sizebuf>0) delete[] buffer;
    }
    ca_flush_io();
    bool result = false;
    while(true) {
        int oldNumber = pvt->numberCallbacks;
        result = pvt->event.wait(1.0);
        if(result) break;
        if(pvt->numberCallbacks==oldNumber) break;
    }
    if(!result) {
        pvt->message += " timeout";
        pvt->requestOK = false;
        pvt->alarm.setMessage(pvt->message);
        pvt->alarm.setSeverity(invalidAlarm);
        pvt->alarm.setStatus(clientStatus);
    }
    pvt->state = connected;
    return pvt->requestOK;
}

String GatherV3Data::getMessage()
{
    return pvt->message;
}

PVStructurePtr GatherV3Data::getNTTableStructure()
{
    return pvt->pvStructure;
}

NTTablePtr  GatherV3Data::getNTTable(){
    return pvt->nttable;
}

PVDoubleArrayPtr GatherV3Data::getDoubleValue()
{
    return pvt->pvdoubleValue;
}

PVLongArrayPtr GatherV3Data::getLongValue()
{
    return pvt->pvlongValue;
}

PVStringArrayPtr GatherV3Data::getStringValue()
{
    return pvt->pvstringValue;
}

PVStructureArrayPtr GatherV3Data::getArrayValue()
{
    return pvt->pvarrayValue;
}

PVLongArrayPtr GatherV3Data::getSecondsPastEpoch()
{
    return pvt->pvsecondsPastEpoch;
}

PVIntArrayPtr GatherV3Data::getNanoSeconds()
{
    return pvt->pvnanoSeconds;
}

PVIntArrayPtr GatherV3Data::getTimeStampTag()
{
    return pvt->pvtimeStampTag;
}

PVIntArrayPtr GatherV3Data::getAlarmSeverity()
{
    return pvt->pvalarmSeverity;
}

PVIntArrayPtr GatherV3Data::getAlarmStatus()
{
    return pvt->pvalarmStatus;
}

PVStringArrayPtr GatherV3Data::getAlarmMessage()
{
    return pvt->pvalarmMessage;
}

PVIntArrayPtr GatherV3Data::getDBRType()
{
    return pvt->pvDBRType;
}

PVBooleanArrayPtr GatherV3Data::getIsArray()
{
    return pvt->pvisArray;
}

PVBooleanArrayPtr GatherV3Data::getIsConnected()
{
    return pvt->pvisConnected;
}

PVStringArrayPtr GatherV3Data::getChannelName()
{
    return pvt->pvchannelName;
}
int GatherV3Data::getConnectedChannels()
{
    return pvt->numberConnected;
}
}}
