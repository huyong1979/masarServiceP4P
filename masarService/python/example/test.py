import sys

from masarclient import masarClient
from masarclient.channelRPC import epicsExit

channel='masarService'

mc = masarClient.client( channelname = channel)

# retrieve all configuration with given constrains
print '==== retrieve service config ===='
params = {'eventid': '106'}
result = mc.retrieveServiceConfigs(params)
print result

print '==== retrieve service event ===='
params = {'eventid': '106'}
result = mc.retrieveServiceEvents(params)
print result

print '==== retrieve service event data===='
params = {'eventid': '106'}
result = mc.retrieveSnapshot(params)
print result

# Call this function before exit.
sys.exit(epicsExit())


