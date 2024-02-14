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

::

Labels
^^^^^^

A label can be used as an additional identifier for an app token and makes storage of the app token more useful.
Currently, labels can be forced for use on the configuration page of the integration bridge.
If labels aren't being forced, they should still be used as an additional identifier for admins to use when tracking many
app tokens.

See the configuration page documentation for more information about forcing label usage.
Future use for labels to be introduced:

* Requiring the use of labels will help to obfuscate tokens completely if used with a special key. This eliminates the need to pass
  around tokens and ids altogether.
* Labels will help to provide meaningful information in logs.


Pull Additional Token Info Checkbox
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is optional but will allow an admin to pull more information from Kaltura when adding a token to the integration bridge.
A Kaltura admin will need to generate a Kaltura Session token (KS) and populate the provided
text box before submission of the token.

.. image:: img/addtoken-ks.jpg
   :alt: KS entry field
   :align: center
::

If the box is checked and no KS is provided (or if the box isn't selected at all), the token will be added to the management list / database,
without the following additional information:

* Assigned Privileges (if any)
* Expiration Date and Time
* Session Duration
* Session User ID (if any)
* Description (if any) - Can be added by an admin when creating a Kaltura App Token

Once the token has been added, it will show in the list on the Manage Tokens page.
