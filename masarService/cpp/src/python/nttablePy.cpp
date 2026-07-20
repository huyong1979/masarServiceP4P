/* nttablePy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <pv/convert.h>
#include <pv/nt.h>
#include <stdexcept>
#include <sstream>

using namespace epics::pvData;
using std::tr1::static_pointer_cast;
using namespace epics::nt;

namespace epics { namespace pvAccess {

class NTTablePvt {
public:
    NTTablePvt(
        NTTable::shared_pointer nttable,
        PVStructurePtr const & pvStructure);
    ~NTTablePvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTTable::shared_pointer nttable;
    PVStructurePtr pvStructure;
    PyObject *pyObject;
};

NTTablePvt::NTTablePvt(
    NTTable::shared_pointer arg,
    PVStructurePtr const & pv)
: nttable(arg),
  pvStructure(pv),
  pyObject(0)
{
    pyObject = PyCapsule_New(&pvStructure,"pvStructure",0);
    Py_INCREF(pyObject);
}

NTTablePvt::~NTTablePvt()
{
}

void NTTablePvt::destroy()
{
    Py_DECREF(pyObject);
    nttable.reset();
}


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    PyObject *capsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablepy",
        &capsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvStructure)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(capsule,"pvStructure");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Must be pvStructure PyCapsule");
        return NULL;
    }
    PVStructurePtr *pv =
        static_cast<PVStructurePtr *>(pvoid);
    NTTablePtr nttable(NTTable::wrap(*pv));
    if(!nttable) {
        PyErr_SetString(PyExc_SyntaxError,
           "pvStructure is not a compatible NTTable");
        return NULL;
    }
    NTTablePvt *pvt = new NTTablePvt(nttable, *pv);
    return PyCapsule_New(pvt,"nttablePvt",0);
}

static PyObject * _init1(PyObject *willbenull, PyObject *args)
{
    PyObject *capsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablepy",
        &capsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvStructure)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(capsule,"pvStructure");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Must be pvStructure PyCapsule");
        return NULL;
    }
    NTTablePtr *nttable = static_cast<NTTablePtr *>(pvoid);
    NTTablePvt *pvt = new NTTablePvt(*nttable,(*nttable)->getPVStructure());
    return PyCapsule_New(pvt,"nttablePvt",0);
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    std::ostringstream buffer;
    buffer << *pvt->nttable->getPVStructure();
    std::string out = buffer.str();
    return Py_BuildValue("s",out.c_str());
}

static PyObject * _getNTTablePy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *ptimeStamp = 0;
    if(!PyArg_ParseTuple(args,"OO:nttablePy",
        &pcapsule,
        &ptimeStamp))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,ptimeStamp)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not a timeStamp capsule");
        return NULL;
    }
    TimeStamp *xxx = static_cast<TimeStamp *>(pvoid);
    PVStructurePtr pvStructure = pvt->nttable->getTimeStamp();
    if(pvStructure!=0) {
        PVTimeStamp pvTimeStamp;
        pvTimeStamp.attach(pvStructure);
        pvTimeStamp.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getAlarm(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *palarm = 0;
    if(!PyArg_ParseTuple(args,"OO:nttablePy",
        &pcapsule,
        &palarm))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,palarm)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not an alarm capsule");
        return NULL;
    }
    Alarm *xxx = static_cast<Alarm *>(pvoid);
    PVStructurePtr pvStructure = pvt->nttable->getAlarm();
    if(pvStructure!=0) {
        PVAlarm pvAlarm;
        pvAlarm.attach(pvStructure);
        pvAlarm.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getNumberValues(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVStringArrayPtr pvLabel = pvt->nttable->getLabels();
    int nvalues = 0;
    if(pvLabel) {
        nvalues = pvLabel->view().size();
    }
    return Py_BuildValue("i",nvalues);
}

static PyObject * _getLabel(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:nttablePy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVStringArrayPtr pvLabel = pvt->nttable->getLabels();
    PVStringArray::const_svector data = pvLabel->view();
    int num = data.size();
    PyObject *result = PyTuple_New(num);
    for(int i=0; i<num; i++) {
        PyObject *elem = Py_BuildValue("s",data[i].c_str());
        PyTuple_SetItem(result, i, elem);
    }
    return result;
}

static PyObject *getScalarValue(PVScalarPtr pvScalar)
{
    ConvertPtr convert = getConvert();
    ScalarType scalarType = pvScalar->getScalar()->getScalarType();
    switch(scalarType) {
        case pvBoolean: {
            PVBooleanPtr pv =  static_pointer_cast<PVBoolean>(pvScalar);
            bool value = pv->get();
            int ivalue = (value ? 1 : 0);
            return Py_BuildValue("i",ivalue);
        }
        case pvByte:
        case pvShort:
        case pvInt:
        {
            int32 value = convert->toInt(pvScalar);
            return Py_BuildValue("i",value);
        }
        case pvUByte:
        case pvUShort:
        case pvUInt:
        {
            uint32 value = convert->toUInt(pvScalar);
            return Py_BuildValue("i",value);
        }
        case pvLong: {
            int64 value = convert->toLong(pvScalar);
            return Py_BuildValue("k",value);
        }
        case pvULong: {
            uint64 value = convert->toULong(pvScalar);
            return Py_BuildValue("k",value);
        }
        case pvFloat: {
            float value = convert->toFloat(pvScalar);
            return Py_BuildValue("f",value);
        }
        case pvDouble: {
            double value = convert->toDouble(pvScalar);
            return Py_BuildValue("d",value);
        }
        case pvString: {
            std::string value = convert->toString(pvScalar);
            return Py_BuildValue("s",value.c_str());
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *getScalarArrayValue(PVScalarArrayPtr pvScalarArray)
{
    ScalarType scalarType = pvScalarArray->getScalarArray()->getElementType();
    switch(scalarType) {
        case pvBoolean: {
            PVBooleanArrayPtr pvArray = static_pointer_cast<PVBooleanArray>(pvScalarArray);
            PVBooleanArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = (data[i] ? 1 : 0);
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvByte: {
            PVByteArrayPtr pvArray = static_pointer_cast<PVByteArray>(pvScalarArray);
            PVByteArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvUByte: {
            PVUByteArrayPtr pvArray = static_pointer_cast<PVUByteArray>(pvScalarArray);
            PVUByteArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvShort: {
            PVShortArrayPtr pvArray = static_pointer_cast<PVShortArray>(pvScalarArray);
            PVShortArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvUShort: {
            PVUShortArrayPtr pvArray = static_pointer_cast<PVUShortArray>(pvScalarArray);
            PVUShortArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                int value = data[i];
                PyObject *elem = Py_BuildValue("i",value);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvInt: {
            PVIntArrayPtr pvArray = static_pointer_cast<PVIntArray>(pvScalarArray);
            PVIntArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("i",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvUInt: {
            PVUIntArrayPtr pvArray = static_pointer_cast<PVUIntArray>(pvScalarArray);
            PVUIntArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("i",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvLong: {
            PVLongArrayPtr pvArray = static_pointer_cast<PVLongArray>(pvScalarArray);
            PVLongArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("k",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvULong: {
            PVULongArrayPtr pvArray = static_pointer_cast<PVULongArray>(pvScalarArray);
            PVULongArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("k",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvFloat: {
            PVFloatArrayPtr pvArray = static_pointer_cast<PVFloatArray>(pvScalarArray);
            PVFloatArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("f",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvDouble: {
            PVDoubleArrayPtr pvArray = static_pointer_cast<PVDoubleArray>(pvScalarArray);
            PVDoubleArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("d",data[i]);
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
        case pvString: {
            PVStringArrayPtr pvArray = static_pointer_cast<PVStringArray>(pvScalarArray);
            PVStringArray::const_svector data = pvArray->view();
            int num = data.size();
            PyObject *result = PyTuple_New(num);
            for(int i=0; i<num; i++) {
                PyObject *elem = Py_BuildValue("s",data[i].c_str());
                PyTuple_SetItem(result, i, elem);
            }
            return result;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *getStructureValue(PVStructurePtr pvStructure);
static PyObject *getStructureArrayValue(PVStructureArrayPtr pvStructureArray)
{
    int num = pvStructureArray->getLength();
    PyObject *result = PyTuple_New(num);
    PVStructureArray::const_svector structureData = pvStructureArray->view();
    for(int i=0; i<num; i++) {
        PVStructurePtr pvStructure = structureData[i];
        PVFieldPtrArray pvFields = pvStructure->getPVFields();
        StructureConstPtr structure = pvStructure->getStructure();
        int n = structure->getNumberFields();
        PyObject *fieldObj = PyTuple_New(n);
        for(int j=0; j<n; j++) {
            FieldConstPtr field = pvFields[j]->getField();
            switch(field->getType()) {
                case scalar: {
                    PVScalarPtr xxx =
                         static_pointer_cast<PVScalar>(pvFields[j]);
                    PyObject *yyy = getScalarValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                case scalarArray: {
                    PVScalarArrayPtr xxx =
                         static_pointer_cast<PVScalarArray>(pvFields[j]);
                    PyObject *yyy = getScalarArrayValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                case epics::pvData::structure: {
                    PVStructurePtr xxx =
                         static_pointer_cast<PVStructure>(pvFields[j]);
                    PyObject *yyy = getStructureValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                case structureArray: {
                    PVStructureArrayPtr xxx =
                         static_pointer_cast<PVStructureArray>(pvFields[j]);
                    PyObject *yyy = getStructureArrayValue(xxx);
                    PyTuple_SetItem(fieldObj,j,yyy);
                    break;
                }
                default:
                    break;
            }
        }
        PyObject *xxx = Py_BuildValue("O",fieldObj);
        PyTuple_SetItem(result, i, xxx);
        
    }
    return result;
}

static PyObject *getStructureValue(PVStructurePtr pvStructure)
{
    PVFieldPtrArray pvFields = pvStructure->getPVFields();
    StructureConstPtr structure = pvStructure->getStructure();
    int n = structure->getNumberFields();
    PyObject *fieldObj = PyTuple_New(n);
    for(int j=0; j<n; j++) {
        FieldConstPtr field = pvFields[j]->getField();
        switch(field->getType()) {
            case scalar: {
                PVScalarPtr xxx =
                     static_pointer_cast<PVScalar>(pvFields[j]);
                PyObject *yyy = getScalarValue(xxx);
                PyTuple_SetItem(fieldObj,j,yyy);
                break;
            }
            case scalarArray: {
                PVScalarArrayPtr xxx =
                     static_pointer_cast<PVScalarArray>(pvFields[j]);
                PyObject *yyy = getScalarArrayValue(xxx);
                PyTuple_SetItem(fieldObj,j,yyy);
                break;
            }
            case epics::pvData::structure: {
                break;
            }
            case structureArray: {
                PVStructureArrayPtr xxx =
                     static_pointer_cast<PVStructureArray>(pvFields[j]);
                PyObject *yyy = getStructureArrayValue(xxx);
                PyTuple_SetItem(fieldObj,j,yyy);
                break;
            }
            default:
                break;
        }
    }
    return fieldObj;
}

static PyObject * _getValue(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    int index = 0;
    if(!PyArg_ParseTuple(args,"Oi:nttablePy",
        &pcapsule,
        &index))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,index)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"nttablePvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTTablePvt *pvt = static_cast<NTTablePvt *>(pvoid);
    PVStringArrayPtr pvLabel = pvt->nttable->getLabels();
    if(!pvLabel) {
        PyErr_SetString(PyExc_RuntimeError, "table has no labels");
        return NULL;
    }
    PVStringArray::const_svector labels = pvLabel->view();
    PVFieldPtr pvField;
    if(index>=0 && static_cast<size_t>(index)<labels.size()) {
        std::string label = labels[index];
        pvField = pvt->nttable->getColumn(label);
        if(!pvField) {
            pvField = pvt->nttable->getPVStructure()->getSubField<PVField>(label);
        }
    } else if(index==13) {
        pvField = pvt->nttable->getPVStructure()->getSubField<PVField>("array_value");
    } else {
        PyErr_SetString(PyExc_IndexError, "column index out of range");
        return NULL;
    }
    if(!pvField) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    Type type = pvField->getField()->getType();
    if(type==scalarArray) {
        PVScalarArrayPtr pvScalarArray = static_pointer_cast<PVScalarArray>(pvField);
        return getScalarArrayValue(pvScalarArray);
    }
    if(type==structureArray) {
        PVStructureArrayPtr pvStructureArray = static_pointer_cast<PVStructureArray>(pvField);
        return getStructureArrayValue(pvStructureArray);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static char _initDoc[] = "_init nttablePy.";
static char _init1Doc[] = "_init1 nttablePy.";
static char _destroyDoc[] = "_destroy nttablePy.";
static char _strDoc[] = "_str  nttablePy.";
static char _getNTTablePyDoc[] = "_getNTTablePy nttablePy.";
static char _getTimeStampDoc[] = "_getTimeStamp nttablePy.";
static char _getAlarmDoc[] = "_getAlarm nttablePy.";
static char _getNumberValuesDoc[] = "_getNumberValues nttablePy.";
static char _getLabelDoc[] = "_getLabel nttablePy.";
static char _getValueDoc[] = "_getValue nttablePy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_init1",_init1,METH_VARARGS,_init1Doc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getNTTablePy",_getNTTablePy,METH_VARARGS,_getNTTablePyDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getNumberValues",_getNumberValues,METH_VARARGS,_getNumberValuesDoc},
    {"_getLabel",_getLabel,METH_VARARGS,_getLabelDoc},
    {"_getValue",_getValue,METH_VARARGS,_getValueDoc},
    {NULL,NULL,0,NULL}
};

static struct PyModuleDef nttablepy_module = {
    PyModuleDef_HEAD_INIT,
    "nttablePy",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_nttablePy(void)
{
    return PyModule_Create(&nttablepy_module);
}

}}
