Welcome to the EdTech Platform Integration Bridge - Beta Project
================================================================

The first iteration of the EdTech Platform Integration Bridge serves as a "middleware" application and abstraction tool for working with Kaltura APIs.
Due to policies and standards in dealing with sensitive data (students, trainees) it is important for schools (Higher Ed, K12) and corporations to track interactions between third party (external, SaaS, cloud-hosted) vendor integrations and internal platforms.

The EdTech Platform Integration Bridge currently performs the following
========================================================================

* Allows administrators to store and track Kaltura App Tokens. In some cases, many app tokens may need to be created in order to provide proper security.
* Can create customized API endpoints for third party vendors who want to integrate with Kaltura, abstracting existing APIs into only those that are needed.
* Logs all interactions.
* Creates a way to filter on allowed categories.
* Labels (tied to app tokens) can be created. Vendors use the labels for creating Kaltura sessions, preventing direct access to the Kaltura APIs.
* Leverages a swagger UI for rapid endpoint development and testing on the fly.
* Easy Deployment. Open Source. Host anywhere.

Future development
==================

* Support for LTI 1.3 / Advantage integrations. One connection, abstracting endpoints from many tools into what is needed for a single third party tool.
* Kaltura support will become a separate module. Support for major LMSs.

Reasons for this project
========================

* The demand for adherance to LTI standards by third party companies and solution providers.
* While the Kaltura video content management platform is a wonderful product (and comes highly recommended), there are some shortfalls when scaled to enterprise levels within the institution:

  * Multiple app tokens need to be created and tracked in order to provide the security and restrictions that university admins desire (read-only access to specific categories).
  * Setting entitlements on specific categories manually in KMC isn’t scalable and may not provide the granularity necessary when a third party is using APIs.
  * Setting Privacy Contexts in the KMC would provide access to specific categories that could then be applied to a single app token… but it breaks in production: “Cannot set multiple privacy contexts when Disable Category Limit feature is turned on”.


:ref:`admin-docs-ref`

:ref:`deployment-docs-ref`



Note: This product is not affiliated with Kaltura, Inc and utilizes the existing Kaltura vPaaS for development against their current APIs.
