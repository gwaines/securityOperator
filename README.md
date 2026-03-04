# securityOperator
StarlingX Security Operator

Providing a declarative interface for configuring Users and Groups of a local openldap/slapd deployment being used for SSH authentication.
The proposed CRDs are as follows:

* **LocalLdapUser**
```
metadata:
  name: gwaines
  namespace: deployment
spec:
  uid: gwaines
  
  # OPTIONAL 
  cn: Greg Waines
  sn: Waines
  givenName: Greg
  displayName: Greg W.

  mail:
  - greg.waines@windriver.com

  # OPTIONAL
  # if not specified then 
  # password initially set to username (uid) 
  # and user forced to change on first login (pwdReset = true)
  #
  # userPasswordSecret:
  #   name: gwaines-password
  #   key: password

  # pwdReset: true    # i.e. defaults to true

  passwordPolicyRef:
    name: standard-policy

  # OPTIONAL - defaults shown 
  # homeDirectory: /home/gwaines
  # loginShell: /bin/bash

 
status: 
  uidNumber: 10001
  gidNumber: 100     # 'users'; as default group

  temporaryLockOut: false
```

* **LocalLdapGroup**
```
metadata:
  name: starlingx-admins
  namespace: deployment
spec:
  cn: starlingx-admins
  
  description: "All StarlingX Administrators"

  members:
  - kind: LocalLdapUser
    name: gwaines
  - kind: LocalLdapGroup
    name: starlingx-archs

status: 
  gidNumber: <integer>
```

* **LocalLdapPasswordPolicy**
```
metadata:
  name: gwaines
  namespace: deployment

spec:
  pwdMinLength: 12
 
  pwdMaxAge: 7776000 # 90 days in seconds

  pwdInHistory: 5

  pwdLockout: true

  pwdMaxFailure: 3

  pwdLockoutDuration: 300 # 5 minutes

  pwdCheckQuality: 2

  pwdExpireWarning: 604800 # 7 days
  
  pwdGraceAuthnLimit: 2

status: 
  # None
```
<br>
<br>
<br>
AND<br>
providing a declarative interface for binding openldap/slapd Users and/or Groups to local Linux Groups (via /etc/security/group.conf) for the purpose of managing authorization.
The proposed CRD is as follows:

* **LinuxRoleBinding**
```
metadata:
  name (str): <arbitrary name of role binding>  

spec:
  description (str):   <description of role binding>

  subjects:
    users:
      - <username1>
      - <username2>
      - ...
    groups:
      - <groupname1>
      - <groupname2>
      - ...

  role:
    linuxGroups:
      - <Linux group 1>
      - <Linux group 2>
      - …

status: 
  # None
```

