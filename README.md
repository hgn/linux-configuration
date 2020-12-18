# A Generic Linux Configuration Framework with Rollback Support

A specification and example implementation

# Goals

- Keep it simple (files are great)
- Easy to deploy (do not depend on non-basic or complex set of functionality)
- Keep it fast (IPC and context switch are not that cheap)
- Provide rollback mechanism and clean communication channel in case of configuration erros
- Programming language independend
- Easy to develop (configuration files are text files, easy modifyable during development)



# Basic Concept

- Services are reading from configuration files (format does not matter, may ini, json, xml, ..)
- Services are notified about configuration changes via SIGHUP signal
- A system wide service (called configd) manages and coordinates ordering and rollback functionality
- Configd agents (e.g. SNMP deamon getting new configuration values from clients) communicates only with configd

# SIGNALS

Signals are used as a lightweight communucation channel betwenn application. Advantage is the easy to use mechanics of signals without heavy IPC mechnanism. But note: other IPC transport mechanism are also legit, like IPC, but if using dbus-deamon the number of context switches will be increased (because the dbus-deamon is always in between) as well as the application integration (dbus implemenation within service vs. signal callback handler within service)

## To Services

## To Configd

# Example:

- Two services:
 - network service, configures the Linux network subsystem, waiting for IP adress changes (`ip-address`)
 - calculator service, multiply parameters and discard results, waiting for new parameter (`calc-number`)
- Configd, coordinates everything
- Web agent, webgui where the two parameters (`ip-address` & `calc-number`) modified

1. User enters new calc-number
2. via IPC web-agent send the new address to configd and blocks for result (web gui spins, user waiting)
3. configd
  - check in local data-model and do sanity-checks (like valid type, not more)
  - saves old network.ini and common.ini
  - write calc-number in common.ini
  - notify first applications in their pre-defined about new configurations (not the exact change!) by sending a SIGHUP to application network service
4. network-service check network.ini if changes are done (e.g. md5 sum of content). No changes are done, so nothing must be done, network-service send SIGUSR1 to configd informing that everything was okay with the new configuration
5. configd will wait until signal is received from service or will resend after a pre-defined timeout (e.g. 2 seconds). Signal was returned by network-services with a positive signal, configd goes ahead.
6. calculator-service will check common.ini. Realize file was modified, calculating the changes parameters with the result `calc-number` was changed. caluclator-service will start no calculation.
  - Because the value was valid, calculator-service will send back SIGUSR1 to signal value was fine
7. configd will wait for signal, SIGUSR1 is received, everything is fine. configd will now inform web-agent that the configuration was successfully.

Summary Overhead:
- two IPC calls betwenn configd and web-agend ("new parameter and positive answer")
- one file write (new parameter)
- four signal between application


