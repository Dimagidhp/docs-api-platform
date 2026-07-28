# About Mediators

Mediators are individual processing units that perform a specific function on messages that pass through the Micro Integrator. The mediator takes the message received by the proxy service or REST API, carries out some predefined actions on it (such as transforming, enriching, filtering), and outputs the modified message. 

For example, the [Clone](../../reference/mediators/clone-mediator) mediator splits a message into several clones, the [Send](../../reference/mediators/send-Mediator) mediator sends the messages, and the [Aggregate](../../reference/mediators/aggregate-mediator) mediator collects and merges the responses before sending them back to the client. 

Mediators also include functionality to match incompatible protocols, data formats, and interaction patterns across different resources. [XQuery](../../reference/mediators/xquery-mediator) and [XSLT](../../reference/mediators/xslt-mediator) mediators allow rich transformations on the messages. Content-based routing using XPath filtering is supported in different flavors, allowing users to get the most convenient configuration experience. Built-in capability to handle transactions allow message mediation to be done transactionally inside the Micro Integrator.

Mediators are always defined within a [mediation sequence](../../reference/synapse-properties/sequence-properties).

## Classification of Mediators

Mediators are classified as follows based on whether or not they access the message's content: 

<table>
  <col width="140">
  <tr>
    <th>Classification</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><b>Content-Aware</b> mediators</td>
    <td>
      These mediators always access the message content when mediating messages (e.g., <a href="../../../reference/mediators/enrich-Mediator">Enrich</a> mediator).
    </td>
  </tr>
  <tr>
    <td><b>Content-Unaware</b> mediators</td>
    <td>
      These mediators never access the message content when mediating messages (e.g., <a href="../../../reference/mediators/send-Mediator">Send</a> mediator).
    </td>
  </tr>
  <tr>
    <td><b>Conditionally Content-Aware</b> mediators</td>
    <td>
      These mediators could be either content-aware or content-unaware depending on their exact instance configuration. For example, a simple <a href="../../../reference/mediators/log-Mediator"></a> mediator instance (i.e. configured as <log/>) is content-unaware. However a log mediator configured as <log level=”full”/> would be content-aware since it is expected to log the message payload.
    </td>
  </tr>
</table>

## List of Mediators

WSO2 Micro Integrator includes a comprehensive library of mediators that provide functionality for implementing widely used **Enterprise Integration Patterns** (EIPs). You can also easily write a custom mediator to provide additional functionality using various technologies such as Java, scripting, and Spring.

**Core Mediators**

[Call](../../reference/mediators/call-mediator) | [Send](../../reference/mediators/send-mediator) | [Loopback](../../reference/mediators/loopback-mediator) | [Sequence](../../reference/mediators/sequence-mediator) | [Respond](../../reference/mediators/respond-mediator) | [Drop](../../reference/mediators/drop-mediator) | [Call Template](../../reference/mediators/call-template-mediator) | [Enrich](../../reference/mediators/enrich-mediator) | [Property](../../reference/mediators/property-mediator) | [Property Group](../../reference/mediators/property-group-mediator) | [Log](../../reference/mediators/log-mediator) | 

**Filter Mediators**

[Filter](../../reference/mediators/filter-mediator) | [Validate](../../reference/mediators/validate-mediator) | [Switch](../../reference/mediators/switch-mediator) | 

**Transform Mediators**

[XSLT](../../reference/mediators/xslt-mediator) | [FastXSLT](../../reference/mediators/fastxslt-mediator) | [URLRewrite](../../reference/mediators/urlrewrite-mediator) | [XQuery](../../reference/mediators/xquery-mediator) | [Header](../../reference/mediators/header-mediator) | [Fault](../../reference/mediators/fault-mediator) | [PayloadFactory](../../reference/mediators/payloadfactory-mediator) | [JSONTransform](../../reference/mediators/json-transform-mediator) |

**Advanced Mediators**

[Cache](../../reference/mediators/cache-mediator) | [ForEach](../../reference/mediators/foreach-mediator) | [Clone](../../reference/mediators/clone-mediator) | [Store](../../reference/mediators/store-mediator) | [Iterate](../../reference/mediators/iterate-mediator) | [Aggregate](../../reference/mediators/aggregate-mediator) | [Callout](../../reference/mediators/callout-mediator) | [Transaction](../../reference/mediators/transaction-mediator) | [Throttle](../../reference/mediators/throttle-mediator) | [DBReport](../../reference/mediators/db-report-mediator) | [DBLookup](../../reference/mediators/dblookup-mediator) | [EJB](../../reference/mediators/ejb-mediator) | [Binder](../../reference/mediators/builder-mediator) | [Entitlement](../../reference/mediators/call-mediator) | [OAuth](../../reference/mediators/call-mediator) | [Smooks](../../reference/mediators/smooks-mediator) | [Data Mapper](../../reference/mediators/data-mapper-mediator) | 

**Extension Mediators**

[Class](../../reference/mediators/class-mediator) | [Script](../../reference/mediators/script-mediator) |
