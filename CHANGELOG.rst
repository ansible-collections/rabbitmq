================================
Community.Rabbitmq Release Notes
================================

.. contents:: Topics

v1.1.0
======

Minor Changes
-------------

- rabbitmq_user_limit: Added to support per-user limits introduced in Rabbitmq 3.8.10.

v1.0.2
======

Bugfixes
--------

- rabbitmq_user: fix parsing of user output when no tags are associated
- rabbitmq_exchange: Add x-delayed-message as a valid exchange type
- rabbitmq_global_parameter: Fix parsing of empty result of list_global_parameters with RabbitMQ 3.7 and ignore header with RabbitMQ 3.8

v1.0.0
======

Minor Changes
-------------

- rabbitmq_publish - Support for connecting with SSL certificates.

Bugfixes
--------

- Refactor RabbitMQ user module to first check the version of the daemon and then, when possible add flags to `rabbitmqctl` so that a machine readable  output is returned. Also, depending on the version, parse the output in correctly. Expands tests accordingly. (https://github.com/ansible/ansible/issues/48890)
- rabbitmq lookup plugin - Fix for rabbitmq lookups failing when using pika v1.0.0 and newer.
- rabbitmq_publish - Fix to ensure the module works correctly for pika v1.0.0 and later. (https://github.com/ansible/ansible/pull/61960)
