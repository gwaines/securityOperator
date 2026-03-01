# securityOperator
StarlingX Security Operator

* provides configuration and management of
  * Trusted CA Certificates,
  * Local Users and Groups,
  * StxRoleBindings ( for     local and/or remote     users and/or groups )
  * LinuxRoleBindings ( for     local and/or remote     users and/or groups )
* Applies configuration of Platform Certificates defined in Certificate CRs
  * system-local-ca
  * system-restapi-gui-certificate
  * system-registry-local-certificate
* Raises expired and expiring-soon Alarms for 'ALL' certificates in system
  * in Certificate CRs, Secret CRs and in Linux Filesystem
