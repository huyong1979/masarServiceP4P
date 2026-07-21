import sys

from masarclient import masarClient
from masarclient.channelRPC import epicsExit

channel='masarService'

mc = masarClient.client( channelname = channel)

# retrieve all system defined in masar configuration
print '==== retrieve system list ===='
result = mc.retrieveSystemList()
print result

# retrieve all configuration with given constrains
print '==== retrieve service config ===='
params = {'system': 'LTD2'}
result = mc.retrieveServiceConfigs(params)
print result

# retrieve all events list with given constrains
print '==== retrieve service event list ===='
params = {'configid': '1'}
result = mc.retrieveServiceEvents(params)
print result

# Call this function before exit.
sys.exit(epicsExit())
