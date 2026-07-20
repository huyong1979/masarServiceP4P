/* dslPY.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <string>
#include <stdexcept>
#include <memory>
#include <vector>
#include <sstream>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/dsl.h>
#include <pv/nt.h>

#include <pv/gatherV3Data.h>

namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::nt;
using std::tr1::static_pointer_cast;
using std::tr1::dynamic_pointer_cast;
typedef std::string String;

static const char* pyStringAsUTF8(PyObject* obj)
{
    return PyUnicode_AsUTF8(obj);
}

static String normalizeFieldName(const String& in)
{
    if(in.empty()) return String("col");
    String out;
    out.reserve(in.size());
    for(size_t i=0; i<in.size(); ++i) {
        char c = in[i];
        if((c>='a' && c<='z') || (c>='A' && c<='Z') || (c>='0' && c<='9') || c=='_') {
            out.push_back(c);
        } else {
            out.push_back('_');
        }
    }
    if(out[0]>='0' && out[0]<='9') out.insert(out.begin(), '_');
    return out;
}

static NTTablePtr createNTTable(
    bool hasFunction,
    bool hasTimeStamp,
    bool hasAlarm,
    StringArray const &names,
    FieldConstPtrArray const &fields)
{
    (void)hasFunction;
    NTTableBuilderPtr builder = NTTable::createBuilder();
    if(hasTimeStamp) builder->addTimeStamp();
    if(hasAlarm) builder->addAlarm();
    for(size_t i = 0; i < names.size(); ++i) {
        if(fields[i]->getType()==scalarArray) {
            ScalarArrayConstPtr arr = static_pointer_cast<const ScalarArray>(fields[i]);
            builder->addColumn(names[i], arr->getElementType());
            continue;
        }
        builder->add(names[i], fields[i]);
    }
    return builder->create();
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

class DSL_RDB;
typedef std::tr1::shared_ptr<DSL_RDB> DSL_RDBPtr;

class DSL_RDB :
    public DSL,
    public std::tr1::enable_shared_from_this<DSL_RDB>
{
public:
    POINTER_DEFINITIONS(DSL_RDB);
    DSL_RDB();
    virtual ~DSL_RDB();
    virtual void destroy();
    virtual PVStructurePtr request(
        const std::string& functionName,int num,StringArray const &names,StringArray const &values);
    bool init();
private:
    DSL_RDBPtr getPtrSelf()
    {
        return shared_from_this();
    }

    PyObject * prequest;
    PyObject * pgetchannames;
};

DSL_RDB::DSL_RDB()
    : prequest(0), pgetchannames(0)
{
   PyThreadState *py_tstate = NULL;
   Py_Initialize();
   PyEval_InitThreads();
   py_tstate = PyGILState_GetThisThreadState();
   PyEval_ReleaseThread(py_tstate);
}

DSL_RDB::~DSL_RDB()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    if(prequest!=0) Py_XDECREF(prequest);
    if(pgetchannames!=0) Py_XDECREF(pgetchannames);
    PyGILState_Release(gstate);
    PyGILState_Ensure();
    Py_Finalize();
}

bool DSL_RDB::init()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject * module = PyImport_ImportModule("masarserver.dslPY");
    if(module==0) {
        String message("dslPY");
        message += " does not exist or is not a python module";
        printf("DSL_RDB::init %s\n",message.c_str());
        return false;
    }
    PyObject *pclass = PyObject_GetAttrString(module, "DSL");
    if(pclass==0) {
        String message("class DSL");
        message += " does not exist";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(module);
        return false;
    }
    PyObject *pargs = Py_BuildValue("()");
    if (pargs == NULL) {
        Py_DECREF(pclass);
        printf("Can't build arguments list\n");
        return false;
    }
    PyObject *pinstance = PyObject_CallObject(pclass,pargs);
    Py_DECREF(pargs);
    if(pinstance==0) {
        String message("class DSL");
        message += " constructor failed";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    prequest = PyObject_GetAttrString(pinstance, "request");
    if(prequest==0) {
        String message("DSL::request");
        message += " could not attach to method";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    pgetchannames = PyObject_GetAttrString(pinstance, "retrieveChannelNames");
    if(pgetchannames==0) {
        String message("DSL::request");
        message += " could not attach to method";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    Py_XDECREF(pinstance);
    Py_XDECREF(pclass);
    Py_XDECREF(module);
    PyGILState_Release(gstate);
    return true;
}

void DSL_RDB::destroy() {}

static NTTablePtr noDataEnetry(std::string message) {
    FieldCreatePtr fieldCreate = getFieldCreate();
    size_t  n = 1;
    StringArray names;
    FieldConstPtrArray fields;
    names.reserve(n);
    fields.reserve(n);
    names.push_back("status");
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    NTTablePtr ntTable(createNTTable(false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();

    PVBooleanArrayPtr pvBoolVal = ntTable->getPVStructure()->getSubField<PVBooleanArray>("value.status");
    if(!pvBoolVal) return ntTable;
    std::vector<boolean> temp(1);
    temp[0]=false;
    replaceFromVector(pvBoolVal, temp);

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntTable->attachAlarm(pvAlarm);

    alarm.setMessage(message);
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr retrieveSnapshot(PyObject * list)
{
    Py_ssize_t top_len = PyList_Size(list);
    if (top_len != 2) {
        return noDataEnetry("Wrong format for returned data from dslPY when retrieving masar data.");
    }
    PyObject * head_array = PyList_GetItem(list, 0); // get head array
    PyObject * head = PyList_GetItem(head_array, 1); // get label array
    Py_ssize_t tuple_size = PyTuple_Size(head);

    PyObject * data_array = PyList_GetItem(list, 1); // get data array
    // data length in each field
    // (the first row is a description instead of real data)
    Py_ssize_t numberChannels = PyList_Size(data_array) - 1;
    if (numberChannels < 0)
        return noDataEnetry("no channel found in this snapshot.");

    size_t strFieldLen = 3; // pv name, s_value, and alarm message are stored as string.

    FieldCreatePtr fieldCreate = getFieldCreate();

    StringArray names;
    names.reserve(tuple_size);

    // create fields
    // set label for each field
    // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
    //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
    //  'is_array', 'array_value')
    FieldConstPtrArray fields;
    fields.reserve(tuple_size);
    for (ssize_t i = 0; i < tuple_size; i ++){
        if (i == 0 || i == 1 || i == 11) { // pv_name: 0, string value: 1, alarm message: 11
            fields.push_back(fieldCreate->createScalarArray(pvString));
        } else if (i == 2) { // double value: 2
            fields.push_back(fieldCreate->createScalarArray(pvDouble));
        } else if(i!=13) {
            // long value: 3, dbr type: 4, secondsPastEpoch: 6, nanoSeconds: 7, timeStampTag: 8,
            // alarmSeverity: 9, alarmStatus: 10, is_array: 12
            fields.push_back(fieldCreate->createScalarArray(pvLong));
        } else {
            // for array value operation
            int naf = 3;
            FieldConstPtrArray arrfields;
            arrfields.reserve(naf);
            arrfields.push_back(fieldCreate->createScalarArray(pvString));
            arrfields.push_back(fieldCreate->createScalarArray(pvDouble));
            arrfields.push_back(fieldCreate->createScalarArray(pvInt));
            StringArray arrayVal;
            arrayVal.reserve(naf);
            arrayVal.push_back("stringVal");
            arrayVal.push_back("doubleVal");
            arrayVal.push_back("intVal");
            StructureConstPtr arrStructure = fieldCreate->createStructure(arrayVal,arrfields);
            fields.push_back(fieldCreate->createStructureArray(arrStructure));
        }
        const char* label = pyStringAsUTF8(PyTuple_GetItem(head, i));
        names.push_back(normalizeFieldName(label ? label : ""));
    }

    // create NTTable
    NTTablePtr ntTable(createNTTable(false,true,true,names,fields));

    // initilize PVStructureArray for waveform/array record
    PVStructureArrayPtr pvarrayValue = ntTable->getPVStructure()->getSubField<PVStructureArray>(names[13]);
    if(!pvarrayValue) {
        return noDataEnetry("Failed to create waveform column.");
    }

    pvarrayValue->setCapacity(numberChannels);
    pvarrayValue->setCapacityMutable(false);
    pvarrayValue->setLength(numberChannels);

    PVStructureArray::svector structVec(numberChannels);
    StructureConstPtr pstructure
        = pvarrayValue->getStructureArray()->getStructure();
    PVDataCreatePtr pvDataCreate = getPVDataCreate();
    for (int i=0; i<numberChannels; i++) {
        structVec[i] = pvDataCreate->createPVStructure(pstructure);
    }
    pvarrayValue->replace(freeze(structVec));
    PVStructureArray::const_svector structdata = pvarrayValue->view();

    if (numberChannels > 0) {
        std::vector<std::vector<String> > pvNames(strFieldLen);
        for (size_t i = 0; i < pvNames.size(); i++){
            pvNames[i].resize(numberChannels);
        }
        std::vector<double> dVals(numberChannels);
        std::vector<std::vector<int64> > lVals(tuple_size-strFieldLen-1); //[dataLen];
        for(size_t i=0; i<lVals.size(); i++) {
            lVals[i].resize(numberChannels);
        }

        // Get values for each fields from list
        PyObject * sublist;

        for (int index = 0; index < numberChannels; index++ ){
            sublist = PyList_GetItem(data_array, index+1);
            for (int i = 0; i < tuple_size-1; i ++) { // tuple_size -1: do not parse waveform tuple directly.
                PyObject * temp = PyTuple_GetItem(sublist, i);
                // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
                //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
                //  'is_array', 'array_value')
                if (i == 0 ) { // pv_name: 0
                    // PyString_Check for type check?
                    const char* sval = pyStringAsUTF8(temp);
                    if (sval == NULL) {
                        pvNames[0][index] = "";
                    } else {
                        pvNames[0][index] = sval;
                    }
                } else if (i == 1 ) { // string value: 1
                    // PyString_Check for type check?
                    const char* sval = pyStringAsUTF8(temp);
                    if (sval == NULL) {
                        pvNames[1][index] = "";
                    } else {
                        pvNames[1][index] = sval;
                    }
                } else if (i == 11 ) { // alarm message: 11
                    // PyString_Check for type check?
                    const char* sval = pyStringAsUTF8(temp);
                    if (sval == NULL) {
                        pvNames[2][index] = "";
                    } else {
                        pvNames[2][index] = sval;
                    }
                } else if (i == 2) { // double value: 2
                    // PyDouble_Check for type check?
                    dVals[index] = PyFloat_AsDouble (temp);
                } else if (i!=13){
                    // long value: 3, dbr type: 4, isConnected: 5, secondsPastEpoch: 6, nanoSeconds: 7,
                    // timeStampTag: 8, alarmSeverity: 9, alarmStatus: 10, is_array: 12
                    // PyLong_Check for type check?
                    if (i == 12) {
                        lVals[i-4][index] = PyLong_AsLongLong (temp);
                    } else {
                        lVals[i-3][index] = PyLong_AsLongLong (temp);
                    }
                }
            }

            PVStructurePtr pvStructure = structdata[index];
            // retrieve array value
            if (lVals[8][index] == 1) {
                // lVals[8] stores whether value is array
                // EPICS DBR type
                //#define    DBF_STRING  0
                //#define    DBF_INT     1
                //#define    DBF_SHORT   1
                //#define    DBF_FLOAT   2
                //#define    DBF_ENUM    3
                //#define    DBF_CHAR    4
                //#define    DBF_LONG    5
                //#define    DBF_DOUBLE  6
                // check EPICS dbr type
                PyObject * arrayValueList = PyTuple_GetItem(sublist, 13);
                PVFieldPtrArray pvfields = pvStructure->getPVFields();

                if (lVals[1][index] == 1 || lVals[1][index] == 4 || lVals[1][index] == 5){
                    // integer type
                    PVIntArrayPtr pvintarray = static_pointer_cast<PVIntArray>(pvfields[2]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t)PyList_Size(arrayValueList);
                        std::vector<int32> pvalue(array_len);
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyLong_AsLong(PyList_GetItem(arrayValueList, array_index));
                        }
                        replaceFromVector(pvintarray, pvalue);
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t)PyTuple_Size(arrayValueList);
                        std::vector<int32> pvalue(array_len);
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyLong_AsLong(PyTuple_GetItem(arrayValueList, array_index));
                        }
                        replaceFromVector(pvintarray, pvalue);
                    }
                } else if (lVals[1][index] == 0) {
                    // string
                    PVStringArrayPtr pvstringarray = static_pointer_cast<PVStringArray>(pvfields[0]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyList_Size(arrayValueList);
                        std::vector<String> pvalue(array_len);
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            const char* s = pyStringAsUTF8(PyList_GetItem(arrayValueList, array_index));
                            pvalue[array_index] = s ? s : "";
                        }
                        replaceFromVector(pvstringarray, pvalue);
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyTuple_Size(arrayValueList);
                        std::vector<String> pvalue(array_len);
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            const char* s = pyStringAsUTF8(PyTuple_GetItem(arrayValueList, array_index));
                            pvalue[array_index] = s ? s : "";
                        }
                        replaceFromVector(pvstringarray, pvalue);
                    }
                } else if (lVals[1][index] == 2 || lVals[1][index] == 6) {
                    // float or double
                    PVDoubleArrayPtr pvdoublearray = static_pointer_cast<PVDoubleArray>(pvfields[1]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyList_Size(arrayValueList);
                        std::vector<double> pvalue (array_len);
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyFloat_AsDouble(PyList_GetItem(arrayValueList, array_index));
                        }
                        replaceFromVector(pvdoublearray, pvalue);
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyTuple_Size(arrayValueList);
                        std::vector<double> pvalue (array_len);
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyFloat_AsDouble(PyTuple_GetItem(arrayValueList, array_index));
                        }
                        replaceFromVector(pvdoublearray, pvalue);
                    }
                }
            }
        }

        // set value to each field
        PVStringArrayPtr pvStr;
        PVDoubleArrayPtr pvDVal;
        PVLongArrayPtr pvLVal;
        for (int i = 0; i < tuple_size; i ++) {
            if (i == 0 ) { // pv_name: 0
                pvStr = static_pointer_cast<PVStringArray>(ntTable->getColumn(names[i]));
                replaceFromVector(pvStr, pvNames[0]);
            } else if (i == 1) { // string value: 1
                pvStr = static_pointer_cast<PVStringArray>(ntTable->getColumn(names[i]));
                replaceFromVector(pvStr, pvNames[1]);
            } else if (i == 11 ) { // alarm message: 11
                pvStr = static_pointer_cast<PVStringArray>(ntTable->getColumn(names[11]));
                replaceFromVector(pvStr, pvNames[2]);
            }else if (i == 2) { // double value: 2
                pvDVal = static_pointer_cast<PVDoubleArray>(ntTable->getColumn(names[i]));
                replaceFromVector(pvDVal, dVals);
            } else if (i!=13){
                // long value: 3, dbr type: 4, isConnected: 5, secondsPastEpoch: 6, nanoSeconds: 7,
                // timeStampTag: 8, alarmSeverity: 9, alarmStatus: 10, is_array: 12
                pvLVal = static_pointer_cast<PVLongArray>(ntTable->getColumn(names[i]));
                if (i == 12)
                    replaceFromVector(pvLVal, lVals[i-4]);
                else
                    replaceFromVector(pvLVal, lVals[i-3]);
            } else {
            }
        }
    }

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr retrieveServiceConfigEvents(PyObject * list, long numeric)
{
    Py_ssize_t list_len = PyList_Size(list);
    // data order in the tuple
    // for example result of service config
    // (service_config_id, service_config_name, service_config_desc, service_config_create_date,
    //  service_config_version, and service_name)
    PyObject * labelList = PyList_GetItem(list, 0);
    Py_ssize_t tuple_size = PyTuple_Size(labelList);
    if (tuple_size < numeric) {
        numeric = tuple_size; // all array are numbers
    }
    int fieldLen = list_len - 1; // length - label header

    FieldCreatePtr fieldCreate = getFieldCreate();

    // create fields
    // set label for each field
    FieldConstPtrArray fields(tuple_size);
    StringArray names(tuple_size);
    for (int i = 0; i < numeric; i ++){
        fields[i] = fieldCreate->createScalarArray(pvLong);
        const char* name = pyStringAsUTF8(PyTuple_GetItem(labelList, i));
        names[i] = normalizeFieldName(name ? name : "");
    }
    for (int i = numeric; i < tuple_size; i ++){
        fields[i] = fieldCreate->createScalarArray(pvString);
        const char* name = pyStringAsUTF8(PyTuple_GetItem(labelList, i));
        names[i] = normalizeFieldName(name ? name : "");
    }

    // create NTTable
    NTTablePtr ntTable(createNTTable(false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();

    std::vector<std::vector<int64> > scIdVals(numeric);
    for(size_t i=0; i<scIdVals.size(); i++) {
        scIdVals[i].resize(list_len-1);
    }

    std::vector<std::vector<String> > vals (tuple_size-numeric);
    for (size_t i = 0; i < vals.size(); i++){
        vals[i].resize(fieldLen);
    }

    // Get values for each fields from list
    PyObject * sublist;
    for (int index = 1; index < list_len; index++ ){
        sublist = PyList_GetItem(list, index);
        for (int i = 0; i < tuple_size; i ++) {
            PyObject * temp = PyTuple_GetItem(sublist, i);
            if (i < numeric){
                // PyLong_Check for type check?
                scIdVals[i][index-1] = PyLong_AsLongLong(temp);
            } else {
                // PyString_Check for type check?
                const char* s = pyStringAsUTF8(temp);
                if (s == NULL) {
                    vals[i-numeric][index-1] = "";
                } else {
                    vals[i-numeric][index-1] = s;
                }
            }
        }
    }

    // set value to each numeric field
    PVLongArrayPtr pvSCIds;
    for (int i = 0; i < numeric; i ++) {
        pvSCIds = dynamic_pointer_cast<PVLongArray>(ntTable->getColumn(names[i]));
        if(!pvSCIds) {
            return noDataEnetry("Missing numeric column while building result table.");
        }
        pvSCIds->setCapacity(fieldLen);
        pvSCIds->setCapacityMutable(false);
        replaceFromVector(pvSCIds, scIdVals[i]);
    }
    // set value to each string field
    PVStringArrayPtr pvStrVal;
    for (int i = numeric; i < tuple_size; i ++) {
        pvStrVal = dynamic_pointer_cast<PVStringArray>(ntTable->getColumn(names[i]));
        if(!pvStrVal) {
            return noDataEnetry("Missing string column while building result table.");
        }
        pvStrVal->setCapacity(fieldLen);
        pvStrVal->setCapacityMutable(false);
        replaceFromVector(pvStrVal, vals[i-numeric]);
    }

    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr saveSnapshot(PyObject * list, NTTablePtr data, String message)
{
    // Get save masar event id
    // -1 means saveSnapshot failure
    int64 eid = -2;
    if (PyTuple_Check(list)){
        PyObject * plist = PyTuple_GetItem(list, 0);
        PyObject * pstatus = PyList_GetItem(plist,0);
        eid = PyLong_AsLongLong(pstatus);
    } else if(PyList_Check(list)) {
        PyObject * pstatus = PyList_GetItem(list,0);
        eid = PyLong_AsLongLong(pstatus);
    } else {
        // updateSnapshotEvent return: not a tuple, nor list.
        return noDataEnetry("Wrong format for returned data from dslPY.");
    }

    if (eid == -1) {
        return noDataEnetry("Machine preview failed. "+ message);
    } else {
        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        data->attachAlarm(pvAlarm);

        alarm.setMessage("Machine preview Successed. " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        data->attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(eid);
        pvTimeStamp.set(timeStamp);

        return data;
    }
}

static NTTablePtr updateSnapshotEvent(PyObject * list)
{
    // Get save masar event id
    // -1 means updateSnapshotEvent failure
    int64 eid = -2;
    if (PyTuple_Check(list)){
        PyObject * plist = PyTuple_GetItem(list, 0);
        PyObject * pstatus = PyList_GetItem(plist,0);
        eid = PyLong_AsLongLong(pstatus);
    } else if(PyList_Check(list)) {
        PyObject * pstatus = PyList_GetItem(list,0);
        eid = PyLong_AsLongLong(pstatus);
    } else {
        // updateSnapshotEvent return: not a tuple, nor list.
        return noDataEnetry("Wrong format for returned data from dslPY.");
    }

    FieldCreatePtr fieldCreate = getFieldCreate();
    size_t  n = 1;
    StringArray names;
    FieldConstPtrArray fields;
    names.reserve(n);
    fields.reserve(n);
    names.push_back("status");
    fields.push_back(fieldCreate->createScalarArray(pvBoolean));
    NTTablePtr ntTable(createNTTable(false,true,true,names,fields));
    PVStructurePtr pvStructure = ntTable->getPVStructure();

    PVBooleanArrayPtr pvBoolVal = ntTable->getPVStructure()->getSubField<PVBooleanArray>("value.status");
    if(!pvBoolVal) return noDataEnetry("Failed to create status column.");
    std::vector<boolean> dataflag;
    dataflag.reserve(n);

    if (eid >= 0) {
        dataflag.push_back(true);
        replaceFromVector(pvBoolVal, dataflag);
    } else {
        dataflag.push_back(false);
        replaceFromVector(pvBoolVal, dataflag);
    }

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntTable->attachAlarm(pvAlarm);

    if (eid >= 0) {
        alarm.setMessage("Success to save snapshot preview.");
    } else {
        alarm.setMessage("Falied to save snapshot preview.");
    }
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr createResult(
    PyObject *result, String functionName)
{
    NTTablePtr pvStructure;
    {
        PyObject *list = 0;
        if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
        {
            //THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY.");
            //return pvStructure;
            return noDataEnetry("Wrong format for returned data from dslPY.");
        }

        if (functionName.compare("retrieveSnapshot")==0) {
            pvStructure = retrieveSnapshot(list);
        } else if (functionName.compare("retrieveServiceEvents")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 2);
        } else if (functionName.compare("retrieveServiceConfigs")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 1);
        } else if (functionName.compare("retrieveServiceConfigProps")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 2);
        } else if (functionName.compare("updateSnapshotEvent")==0) {
            pvStructure = updateSnapshotEvent(list);
        } else {
            pvStructure = noDataEnetry("Did not find data");
        }
    }
    return pvStructure;
}

static NTTablePtr getLiveMachine(StringArray const & channelName,
                                 int numberChannels, String * message)
{
    GatherV3DataPtr gather = GatherV3DataPtr(
        new GatherV3Data(channelName,numberChannels));
	
	// wait for at least 1.0 seconds before timeout.
	// or wait for channel numbers/1000 seconds 
    double timeout = numberChannels * 1.0e-3;
    if (timeout < 1.0) timeout = 1.0;
    // maximun waiting time: 10.0 seconds.
    // it does not solve the fundamental problem. 
    if (timeout > 10.0) timeout = 10.0;
    
    bool result = gather->connect(timeout);
    
    * message = gather->getMessage();
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        if (gather->getConnectedChannels() == 0)
            return noDataEnetry("connect failed "+gather->getMessage());
    }
    if((*message).length() == 0) {
        *message = "All channels are connected.";
    }
    result = gather->get();

    NTTablePtr livedata = gather->getNTTable();

    return livedata;
}

PVStructurePtr DSL_RDB::request(
    const std::string& functionName,int num,StringArray const & names,StringArray const &values)
{
    if (functionName.compare("getLiveMachine")==0) {
        String message;
        NTTablePtr ntTable = getLiveMachine(values, num, &message);

        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        ntTable->attachAlarm(pvAlarm);
        alarm.setMessage("Live machine: " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        ntTable->attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(0);
        pvTimeStamp.set(timeStamp);
        return ntTable->getPVStructure();
    }

    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *pyDict = PyDict_New();
    for (int i = 0; i < num; i ++) {
        PyObject *pyValue = Py_BuildValue("s",values[i].c_str());
        PyDict_SetItemString(pyDict,names[i].c_str(),pyValue);
    }
    PyObject *pyValue = Py_BuildValue("s",functionName.c_str());
    PyDict_SetItemString(pyDict,"function",pyValue);
    NTTablePtr pvReturn;
    if (functionName.compare("saveSnapshot")==0) {
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *pchannelnames = PyObject_CallObject(pgetchannames,pyTuple);
        if(pchannelnames == NULL) {
            pvReturn = noDataEnetry("Failed to retrieve channel names.");
        } else {
            Py_ssize_t list_len = PyList_Size(pchannelnames);

            StringArray channames(list_len);
            PyObject * name;
            for (ssize_t i = 0; i < list_len; i ++) {
                name = PyList_GetItem(pchannelnames, i);
                const char* s = pyStringAsUTF8(name);
                channames[i] = s ? s : "";
            }
            Py_DECREF(pchannelnames);
            String message;
            NTTablePtr data = getLiveMachine(channames, list_len, &message);

            // create a tuple is needed to pass to Python as parameter.
            PyObject * pdata = PyCapsule_New(&data,"pvStructure",0);
            PyObject * pyTuple2 = PyTuple_New(2);

            // first value is the data from live machine
            PyTuple_SetItem(pyTuple2, 0, pdata);
            // second value is the dictionary
            Py_INCREF(pyDict);
            PyTuple_SetItem(pyTuple2, 1, pyDict);
            PyObject *result = PyObject_CallObject(prequest,pyTuple2);
            if(result == NULL) {
                pvReturn = noDataEnetry("Failed to save snapshot.");
            } else {
                pvReturn = saveSnapshot(result, data, message);
                Py_DECREF(result);
            }
            Py_DECREF(pyTuple2);
        }
        Py_DECREF(pyTuple);
    } else {
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);

        PyObject *result = PyObject_CallObject(prequest,pyTuple);
        Py_DECREF(pyTuple);
        if(result == NULL) {
            PyErr_Print();
            pvReturn = noDataEnetry("No data entry found in database.");
        } else {
            pvReturn = createResult(result,functionName);
            Py_DECREF(result);
        }
    }
    PyGILState_Release(gstate);
    return pvReturn->getPVStructure();
}

DSLPtr createDSL_RDB()
{
   DSL_RDBPtr dsl = DSL_RDBPtr(new DSL_RDB());
   if(!dsl->init()) return DSL_RDBPtr();
   return DSL_RDBPtr(dsl);
}

}}
