.. _admin-docs-ref:

Administration
==============

Authentication
--------------

Once the application has been deployed, an administrator can access the interface at the root of the domain.
Login with the default credentials to get started.

.. image:: img/loginpage.jpg
   :alt: Login Page
   :align: center

The application currently uses basic authentication but can be adapted for use with SSO, OAuth2, or LDAP.
Clicking on "Remember Me" will place a tamper-proof cookie in the user's local browser storage.

Passwords are hashed and salted when stored in the database.

Add Token
---------

The **Add Token** page is where administrators can add App Tokens that they've generated for third party integrators to use
for accessing the Kaltura APIs. The App Token Id and App Token are required. Entering a label is optional.

.. image:: img/addtoken1.jpg
   :alt: Add Token Page
   :align: center

Labels
~~~~~~

A label can be used as an additional identifier for an app token and makes storage of the app token more useful.
Currently, labels can be forced for use on the configuration page of the integration bridge.
If labels aren't being forced, they should still be used an an additional identifier for admins to use when tracking many
app tokens.

See the configuration page documentation for more information about forcing label usage.
Future use for labels to be introduced:
  * requiring the use of labels will help to obfuscate tokens completely if used with a special key. This eliminates the need to pass
  around tokens and ids altogether.
  * labels will help to provide meaningful information in logs.