/* masarService.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * EPICS pvDataCPP is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Marty Kraimer 2011.03 */
/* This connects to a V3 record and presents the data as a PVStructure
 * It provides access to  value, alarm, display, and control.
 */

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>
#include <stdexcept>
#include <memory>

#include <pv/nt.h>
#include <pv/convert.h>

#include <pv/masarService.h>


namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::nt;
typedef std::string String;
using std::tr1::static_pointer_cast;

MasarService::MasarService()
: dslRdb(createDSL_RDB())
{}

MasarService::~MasarService()
{
//printf("MasarService::~MasarService()\n");
}

void MasarService::destroy()
{
//printf("MasarService::destroy()\n");
}

PVStructurePtr MasarService::request(
    PVStructurePtr const & pvArgument) throw (epics::pvAccess::RPCRequestException)
{
    static const int numberFunctions = 9;
    static const String functionNames[numberFunctions] = {
        "saveSnapshot",
        "retrieveSnapshot",
        "retrieveServiceConfigProps",
        "retrieveServiceConfigs",
        "saveServiceConfig",
        "retrieveServiceEvents",
        "saveServiceEvent",
        "updateSnapshotEvent",
        "getLiveMachine"
    };

    PVStringPtr pvFunction = pvArgument->getSubField<PVString>("function");
    if(!pvFunction) {
        throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,"unknown MASAR function");
    }

    String functionName = pvFunction->get();
    bool supported = false;
    for(int i=0; i<numberFunctions; i++) {
        if(functionName==functionNames[i]) {
            supported = true;
            break;
        }
    }
    if(!supported) {
        throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
    }

    StringArray fieldNames = pvArgument->getStructure()->getFieldNames();
    std::vector<std::string> names;
    std::vector<std::string> values;
    names.reserve(fieldNames.size());
    values.reserve(fieldNames.size());
    ConvertPtr convert = getConvert();

    PVStringArrayPtr argNames = pvArgument->getSubField<PVStringArray>("name");
    PVStringArrayPtr argValues = pvArgument->getSubField<PVStringArray>("value");
    if(argNames && argValues) {
        PVStringArray::const_svector nview = argNames->view();
        PVStringArray::const_svector vview = argValues->view();
        size_t n = nview.size();
        if(vview.size()<n) n = vview.size();
        for(size_t i=0; i<n; i++) {
            if(nview[i].empty()) continue;
            names.push_back(nview[i]);
            values.push_back(vview[i]);
        }
    }

    for(size_t i=0; i<fieldNames.size(); i++) {
        if(fieldNames[i]=="function") continue;
        if(fieldNames[i]=="name" || fieldNames[i]=="value") continue;
        PVFieldPtr fld = pvArgument->getSubField<PVField>(fieldNames[i]);
        if(!fld) continue;
        names.push_back(fieldNames[i]);
        if(fld->getField()->getType()==scalar) {
            PVScalarPtr scalarFld = static_pointer_cast<PVScalar>(fld);
            values.push_back(convert->toString(scalarFld));
        } else {
            values.push_back("");
        }
    }
    return dslRdb->request(functionName,names.size(),names,values);
}

}}
