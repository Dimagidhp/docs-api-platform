# Broken links and images — `api-manager/4.6.0`

**348 findings** across 574 pages. **71** have an exact or high-confidence mechanical fix; **118** need a human decision.

### Fixable by script

Run in this order. Each is a separate `fix_links.py --tier` run, and every rewrite is verified against the files on disk before it is written.

| Order | Group | Cause | Count | Fix |
|---|---|---|---|---|
| 1 | `malformed` | Malformed link syntax | 0 | Exact — no judgement |
| 2 | `dir_style` | Written as a URL, so mkdocs never resolves it | 39 | Add `.md` — mkdocs then owns the depth |
| 3 | `depth` | Wrong relative depth | 0 | Exact — no judgement |
| 4 | `renamed` | Renamed or moved target | 39 | Proposed; `high` confidence applied by default |
| 5 | `templated_fixable` | `{{base_path}}` where the resource exists | 0 | Exact rewrite to a relative path |

### Needs a person

`fix_links.py` refuses these. The information needed is not in the repository, and a guess produces a confident link to the wrong page — worse than a visibly broken one, because nobody re-checks it.

| Group | Cause | Count | Why it cannot be automated |
|---|---|---|---|
| `templated` | `{{base_path}}` where the resource does not exist | 1 | May be served by a redirect |
| `stale` | Pre-migration domain | 38 | Needs the equivalent page on the new site |
| `anchor` | Missing anchor | 113 | The heading was reworded — which one now? |
| `gone` | No target anywhere | 118 | Was it dropped, missed, or merged? |

## Excluded — `{{base_path}}` where the resource does not exist

Same variable, but the target is not present at that path in this version. It may be served by a redirect, or the page may not have been migrated. **Leave these alone** until the redirect strategy is settled — a rewrite here would be a guess.

| Page | Link | Variable |
|---|---|---|
| `api-manager/4.6.0/reference/faq.md` | `{{base}}/install-and-setup/setup/security/configuring-transport-level-security/#disabling-weak-ciphers` | `{{base}}` |

## `dir_style` — Written as a URL, so mkdocs never resolves it

These point at the right page already. Because the target is written in URL shape rather than naming the `.md` file, mkdocs passes it through untouched and the browser resolves it against the rendered page URL — one directory deeper than the source file, so it lands one level short. Adding the extension hands the depth calculation back to mkdocs, permanently.

| Page | Currently | Change to |
|---|---|---|
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../administer/managing-users-and-roles/managing-user-roles/#update-before-the-first-startup-recommended` | `managing-user-roles.md#update-before-the-first-startup-recommended` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-users.md` | `../../administer/managing-users-and-roles/managing-user-roles/#create-user-roles` | `managing-user-roles.md#create-user-roles` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-users.md` | `../../administer/managing-users-and-roles/managing-user-roles/#create-user-roles` | `managing-user-roles.md#create-user-roles` |
| `api-manager/4.6.0/administer/multiple-gateways/configure-gateway-visibility.md` | `../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/administer/multiple-gateways/configure-gateway-visibility.md` | `../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/administer/multiple-gateways/configure-gateway.md` | `../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-design-manage/deploy-and-publish/deploy-on-gateway/deploy-api/exposing-apis-via-custom-hostnames.md` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-design-manage/deploy-and-publish/deploy-on-gateway/deploy-api/exposing-apis-via-custom-hostnames.md` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-design-manage/deploy-and-publish/deploy-on-gateway/deploy-api/exposing-apis-via-custom-hostnames.md` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-gateway/policies/configuring-message-builders-formatters.md` | `../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-security/key-management/applications/provisioning-out-of-band-oauth-clients.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-security/key-management/authentication/grant-types/jwt-grant.md` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-forgerock-connector.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-global-key-manager.md` | `../../../api-security/key-management/third-party-key-managers/overview/#configuring-key-managers-with-wso2-api-m` | `overview.md#configuring-key-managers-with-wso2-api-m` |
| `api-manager/4.6.0/api-security/key-management/tokens/encrypting-oauth2-tokens.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-security/key-management/tokens/hashing-oauth-keys.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/api-security/key-management/tokens/jwt-tokens.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#accessing-the-api-publisher` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#accessing-the-api-publisher` |
| `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `../../../reference/product-apis/devportal-apis/devportal-v3/devportal-v3/#tag/Applications/paths/~1applications~1%7BapplicationId%7D/put` | `../../../reference/product-apis/devportal-apis/devportal-v3/devportal-v3.md#tag/Applications/paths/~1applications~1{applicationId}/put` |
| `api-manager/4.6.0/api-security/runtime/api-authentication/secure-apis-using-oauth2-tokens.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#accessing-the-api-publisher` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#accessing-the-api-publisher` |
| `api-manager/4.6.0/api-security/runtime/api-authentication/secure-apis-using-oauth2-tokens.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#accessing-the-api-publisher` | `../../../install-and-setup/install/installing-the-product/running-the-api-m.md#accessing-the-api-publisher` |
| `api-manager/4.6.0/apiops/cli/advanced-topics/creating-custom-users-to-perform-api-controller-operations.md` | `../../../administer/managing-users-and-roles/managing-user-roles/#create-user-roles` | `../../../administer/managing-users-and-roles/managing-user-roles.md#create-user-roles` |
| `api-manager/4.6.0/get-started/api-manager-quick-start-guide.md` | `../install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-0-all-in-one/#step-1-set-up-basic-configurations` | `../install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-0-all-in-one.md#step-1-set-up-basic-configurations` |
| `api-manager/4.6.0/get-started/apim-architecture.md` | `../monitoring/api-analytics/analytics-overview/#architecture/` | `../monitoring/api-analytics/analytics-overview.md#architecture/` |
| `api-manager/4.6.0/install-and-setup/setup/multi-dc-deployment/configuring-multi-dc-deployment-pattern-2.md` | `../../../install-and-setup/setup/distributed-deployment/deploying-wso2-api-m-in-a-distributed-setup/#configure-the-gateway-nodes` | `../distributed-deployment/deploying-wso2-api-m-in-a-distributed-setup.md#configure-the-gateway-nodes` |
| `api-manager/4.6.0/install-and-setup/setup/multi-dc-deployment/configuring-multi-dc-deployment-pattern-2.md` | `../../../install-and-setup/setup/distributed-deployment/deploying-wso2-api-m-in-a-distributed-setup/#configure-the-traffic-manager-nodes` | `../distributed-deployment/deploying-wso2-api-m-in-a-distributed-setup.md#configure-the-traffic-manager-nodes` |
| `api-manager/4.6.0/install-and-setup/setup/single-node/configuring-a-single-node.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/install-and-setup/setup/single-node/configuring-an-active-active-deployment.md` | `../../..//install-and-setup/setup/deployment-best-practices/production-deployment-guidelines/#common-guidelines-and-checklist/` | `../deployment-best-practices/production-deployment-guidelines.md#common-guidelines-and-checklist/` |
| `api-manager/4.6.0/install-and-setup/setup/single-node/configuring-an-active-active-deployment.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `../../install/installing-the-product/running-the-api-m.md#starting-the-server` |
| `api-manager/4.6.0/integrate/develop/working-with-service-catalog.md` | `../../tutorials/tutorials-overview/#integration-tutorials` | `../../tutorials/tutorials-overview.md#integration-tutorials` |
| `api-manager/4.6.0/monitoring/observability/monitoring-correlation-logs.md` | `../../reference/product-apis/devops-apis/devops-v0/devops-v0/#/paths/~1config~1correlation~1/get` | `../../reference/product-apis/devops-apis/devops-v0/devops-v0.md#/paths/~1config~1correlation~1/get` |
| `api-manager/4.6.0/reference/customize-product/extending-api-manager/extending-workflows/configuring-http-redirection-for-workflows.md` | `../../../../reference/product-apis/admin-apis/admin-v4/admin-v4/#tag/Workflows-(Individual` | `../../../product-apis/admin-apis/admin-v4/admin-v4.md#tag/Workflows-(Individual` |
| `api-manager/4.6.0/reference/customize-product/extending-api-manager/extending-workflows/configuring-http-redirection-for-workflows.md` | `../../../../reference/product-apis/admin-apis/admin-v4/admin-v4/#tag/Workflows-(Individual` | `../../../product-apis/admin-apis/admin-v4/admin-v4.md#tag/Workflows-(Individual` |
| `api-manager/4.6.0/reference/default-product-ports.md` | `../install-and-setup/setup/deployment-best-practices/changing-the-default-ports-with-offset/#configuring-the-port-offset` | `../install-and-setup/setup/deployment-best-practices/changing-the-default-ports-with-offset.md#configuring-the-port-offset` |
| `api-manager/4.6.0/reference/faq.md` | `../install-and-setup/setup/security/logins-and-passwords/maintaining-logins-and-passwords/#setting-up-an-e-mail-login` | `../install-and-setup/setup/security/logins-and-passwords/maintaining-logins-and-passwords.md#setting-up-an-e-mail-login` |
| `api-manager/4.6.0/reference/faq.md` | `../install-and-setup/install/installing-the-product/running-the-api-m/#configuring-the-session-time-out` | `../install-and-setup/install/installing-the-product/running-the-api-m.md#configuring-the-session-time-out` |
| `api-manager/4.6.0/reference/product-apis/advanced-configurations.md` | `../../administer/managing-users-and-roles/managing-permissions/#adding-role-based-permissions` | `../../administer/managing-users-and-roles/managing-permissions.md#adding-role-based-permissions` |


## `renamed` — Renamed or moved target

The target does not exist at the path written, but a file of the same name exists elsewhere under the same version. This is the restructure: directories were renamed and the inbound links were never updated.

### Exactly one candidate — high confidence (32)

| Page | Currently | Change to |
|---|---|---|
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../administer/product-administration/managing-users-and-roles/managing-permissions/#adding-role-based-permissions` | `managing-permissions.md#adding-role-based-permissions` |
| `api-manager/4.6.0/ai-gateway/mcp-gateway/invoke-a-mcp-server-using-playground.md` | `../../consume/invoke-apis/invoke-apis-using-tools/invoke-an-api-using-the-integrated-api-console/#step-3-get-an-access-token` | `../../api-developer-portal/invoke-apis/invoke-apis-using-tools/invoke-an-api-using-the-integrated-api-console.md#step-3-get-an-access-token` |
| `api-manager/4.6.0/api-design-manage/deploy-and-publish/deploy-on-gateway/api-gateway/scaling-the-gateway.md` | `../../../../administer/product-configurations/configuring-caching/#key-cache` | `../../../../install-and-setup/setup/advance-configurations/configuring-caching.md#key-cache` |
| `api-manager/4.6.0/api-developer-portal/collaboration/interact-with-the-community.md` | `../../manage-apis/design/api-collaborations/enable-social-media-interaction/#enable-sharing-api-links-on-social-media` | `../../api-design-manage/design/api-collaborations/enable-social-media-interaction.md#enable-sharing-api-links-on-social-media` |
| `api-manager/4.6.0/api-gateway/scaling-the-gateway.md` | `../administer/product-configurations/configuring-caching/#key-cache` | `../install-and-setup/setup/advance-configurations/configuring-caching.md#key-cache` |
| `api-manager/4.6.0/apiops/cli/cicd-using-cli.md` | `../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/cicd-using-cli.md` | `../../install-and-setup/setup/api-controller/getting-started-with-wso2-api-controller/##set-export-directory` | `getting-started-with-wso2-api-controller.md##set-export-directory` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/importing-apis-via-dev-first-approach.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/using-dynamic-data-in-api-controller-projects/#initialize-api-projects-with-dynamic-data` | `../advanced-topics/using-dynamic-data-in-api-controller-projects.md#initialize-api-projects-with-dynamic-data` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/importing-apis-via-dev-first-approach.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/migrating-api-products-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/migrating-api-products-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/configuring-environment-specific-parameters/#defining-the-params-file-for-an-api-product` | `../advanced-topics/configuring-environment-specific-parameters.md#defining-the-params-file-for-an-api-product` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/migrating-api-products-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/using-dynamic-data-in-api-controller-projects/#add-dynamic-data-to-environment-configs` | `../advanced-topics/using-dynamic-data-in-api-controller-projects.md#add-dynamic-data-to-environment-configs` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/migrating-apis-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/migrating-apis-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/configuring-environment-specific-parameters/#defining-the-params-file-for-an-api` | `../advanced-topics/configuring-environment-specific-parameters.md#defining-the-params-file-for-an-api` |
| `api-manager/4.6.0/apiops/cli/managing-apis-api-products/migrating-apis-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/using-dynamic-data-in-api-controller-projects/#add-dynamic-data-to-environment-configs` | `../advanced-topics/using-dynamic-data-in-api-controller-projects.md#add-dynamic-data-to-environment-configs` |
| `api-manager/4.6.0/apiops/cli/managing-applications/migrating-applications-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-common-api-policies/migrating-common-api-policies-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-mcp-servers/importing-mcp-servers-via-dev-first-approach.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-mcp-servers/migrating-mcp-servers-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/creating-custom-users-to-perform-api-controller-operations/#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` | `../advanced-topics/creating-custom-users-to-perform-api-controller-operations.md#steps-to-create-a-custom-user-who-can-perform-api-controller-operations` |
| `api-manager/4.6.0/apiops/cli/managing-mcp-servers/migrating-mcp-servers-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/configuring-environment-specific-parameters/#defining-the-params-file-for-an-mcp-server` | `../advanced-topics/configuring-environment-specific-parameters.md#defining-the-params-file-for-an-mcp-server` |
| `api-manager/4.6.0/apiops/cli/managing-mcp-servers/migrating-mcp-servers-to-different-environments.md` | `../../../install-and-setup/setup/api-controller/advanced-topics/using-dynamic-data-in-api-controller-projects/#add-dynamic-data-to-environment-configs` | `../advanced-topics/using-dynamic-data-in-api-controller-projects.md#add-dynamic-data-to-environment-configs` |
| `api-manager/4.6.0/includes/deploy/steps-to-deploy-apim-in-a-distributed-setup-with-km-separation.md` | `../../../../install-and-setup/deploying-wso2-api-manager/production-deployment-guidelines/#common-guidelines-and-checklist` | `../../install-and-setup/setup/deployment-best-practices/production-deployment-guidelines.md#common-guidelines-and-checklist` |
| `api-manager/4.6.0/includes/deploy/steps-to-deploy-apim-in-a-distributed-setup-with-tm-separation.md` | `../../../../install-and-setup/deploying-wso2-api-manager/production-deployment-guidelines/#common-guidelines-and-checklist` | `../../install-and-setup/setup/deployment-best-practices/production-deployment-guidelines.md#common-guidelines-and-checklist` |
| `api-manager/4.6.0/install-and-setup/install/installation-prerequisites.md` | `../../install-and-setup/setup/reference/product-compatibility/#tested-operating-systems-and-jdks` | `../../reference/product-compatibility.md#tested-operating-systems-and-jdks` |
| `api-manager/4.6.0/install-and-setup/install/installation-prerequisites.md` | `../../install-and-setup/setup/reference/product-compatibility/#tested-wso2-products` | `../../reference/product-compatibility.md#tested-wso2-products` |
| `api-manager/4.6.0/install-and-setup/setup/configure-userstores/configure-primary-user-store/configuring-a-read-only-ldap-user-store.md` | `../../../../administer/product-security/logins-and-passwords/maintaining-logins-and-passwords/#setting-up-an-e-mail-login` | `../../security/logins-and-passwords/maintaining-logins-and-passwords.md#setting-up-an-e-mail-login` |
| `api-manager/4.6.0/install-and-setup/setup/configure-userstores/configure-primary-user-store/configuring-a-read-write-ldap-user-store.md` | `../../../../administer/product-security/logins-and-passwords/maintaining-logins-and-passwords/#setting-up-an-e-mail-login` | `../../security/logins-and-passwords/maintaining-logins-and-passwords.md#setting-up-an-e-mail-login` |
| `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/security-guidelines-for-production-deployment.md` | `../../../install-and-setup/setup/reference/product-compatibility/#tested-operating-systems-and-jdks` | `../../../reference/product-compatibility.md#tested-operating-systems-and-jdks` |
| `api-manager/4.6.0/install-and-setup/setup/distributed-deployment/deploying-wso2-api-m-in-a-simple-scalable-setup.md` | `../../../../install-and-setup/deploying-wso2-api-manager/production-deployment-guidelines/#common-guidelines-and-checklist` | `../deployment-best-practices/production-deployment-guidelines.md#common-guidelines-and-checklist` |
| `api-manager/4.6.0/install-and-setup/setup/single-node/configuring-a-single-node.md` | `../../../install-and-setup/deploying-wso2-api-manager/production-deployment-guidelines/#common-guidelines-and-checklist` | `../deployment-best-practices/production-deployment-guidelines.md#common-guidelines-and-checklist` |
| `api-manager/4.6.0/reference/customize-product/customizations/adding-internationalization.md` | `../../../consume/customizations/customizing-the-developer-portal/overriding-developer-portal-theme/#uploading-via-the-admin-portal-tenants-only` | `customizing-the-developer-portal/overriding-developer-portal-theme.md#uploading-via-the-admin-portal-tenants-only` |
| `api-manager/4.6.0/reference/faq.md` | `../install-and-setup/setup/reference/default-product-ports/#api-manager` | `default-product-ports.md#api-manager` |

### Several candidates — verify before applying (7)

| Page | Currently | Best guess | Confidence |
|---|---|---|---|
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../administer/product-administration/managing-users-and-roles/managing-user-stores/introduction-to-userstores` | `managing-user-stores/introduction-to-userstores.md` | low (2 candidates) |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../administer/product-administration/managing-users-and-roles/managing-user-stores/introduction-to-userstores` | `managing-user-stores/introduction-to-userstores.md` | low (2 candidates) |
| `api-manager/4.6.0/api-developer-portal/invoke-apis/invoke-apis-using-tools/invoke-an-api-using-the-integrated-api-console.md` | `../../../manage-apis/deploy-and-publish/deploy-on-gateway/api-gateway/maintaining-separate-production-and-sandbox-gateways/#multiple-gateways-to-handle-production-and-sandbox-requests-separately` | `../../../api-design-manage/deploy-and-publish/deploy-on-gateway/api-gateway/maintaining-separate-production-and-sandbox-gateways.md#multiple-gateways-to-handle-production-and-sandbox-requests-separately` | low (2 candidates) |
| `api-manager/4.6.0/api-developer-portal/invoke-apis/invoke-apis-using-tools/invoke-an-graphql-api-using-the-integrated-graphql-console.md` | `../../../manage-apis/deploy-and-publish/deploy-on-gateway/api-gateway/maintaining-separate-production-and-sandbox-gateways/#multiple-gateways-to-handle-production-and-sandbox-requests-separately` | `../../../api-design-manage/deploy-and-publish/deploy-on-gateway/api-gateway/maintaining-separate-production-and-sandbox-gateways.md#multiple-gateways-to-handle-production-and-sandbox-requests-separately` | low (2 candidates) |
| `api-manager/4.6.0/get-started/about-this-release.md` | `../manage-apis/deploy-and-publish/deploy-on-gateway/api-gateway/maintain-seperate-gateways-per-tenants/` | `../api-gateway/maintain-seperate-gateways-per-tenants.md` | low (2 candidates) |
| `api-manager/4.6.0/install-and-setup/setup/advance-configurations/configuring-caching.md` | `../../../manage-apis/deploy-and-publish/deploy-on-gateway/api-gateway/response-caching/` | `../../../api-design-manage/deploy-and-publish/deploy-on-gateway/api-gateway/response-caching.md` | low (2 candidates) |
| `api-manager/4.6.0/install-and-setup/setup/multi-dc-deployment/multi-dc-deployment-patterns-overview.md` | `../../../manage-apis/deploy-and-publish/deploy-on-gateway/api-gateway/scaling-the-gateway` | `../../../api-gateway/scaling-the-gateway.md` | low (2 candidates) |

## `stale` — Links to the pre-migration site

These point at a location the documentation has migrated away from. For each one: find the equivalent page on the new site and link to it relatively, or if the content wasn't migrated, remove the link and say so in the prose. Never leave a reader on the old site.

| Page | Link |
|---|---|
| `api-manager/4.6.0/api-design-manage/deploy-and-publish/publish-on-dev-portal/publish-an-api.md` | `https://apim.docs.wso2.com/en/latest/design/api-monetization/monetizing-an-api/#step-2-enable-monetization` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-0-all-in-one.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-0-all-in-one.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/api-controller/encrypting-secrets-with-ctl/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-0-all-in-one.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/deploy-and-publish/deploy-on-gateway/deploy-api/deploy-through-multiple-api-gateways/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-0-all-in-one.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-1-all-in-one-ha.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-1-all-in-one-ha.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/deploy-and-publish/deploy-on-gateway/deploy-api/deploy-through-multiple-api-gateways/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-1-all-in-one-ha.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-2-all-in-one-gw.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-2-all-in-one-gw.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/deploy-and-publish/deploy-on-gateway/deploy-api/deploy-through-multiple-api-gateways/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-2-all-in-one-gw.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-3-acp-tm-gw.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-3-acp-tm-gw.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/deploy-and-publish/deploy-on-gateway/deploy-api/deploy-through-multiple-api-gateways/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-3-acp-tm-gw.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-4-acp-tm-gw-km.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-4-acp-tm-gw-km.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/deploy-and-publish/deploy-on-gateway/deploy-api/deploy-through-multiple-api-gateways/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-4-acp-tm-gw-km.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-5-all-in-one-gw-km.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-5-all-in-one-gw-km.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/deploy-and-publish/deploy-on-gateway/deploy-api/deploy-through-multiple-api-gateways/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-5-all-in-one-gw-km.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-6-all-in-one-is-as-km.md` | `https://apim.docs.wso2.com/en/4.6.0/install-and-setup/setup/security/configuring-keystores/keystore-basics/creating-new-keystores/#step-3-importing-certificates-to-the-truststore` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-6-all-in-one-is-as-km.md` | `https://apim.docs.wso2.com/en/4.6.0/install-and-setup/setup/security/configuring-keystores/keystore-basics/creating-new-keystores/#step-3-importing-certificates-to-the-truststore` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-6-all-in-one-is-as-km.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/security/configuring-keystores/configuring-keystores-in-wso2-api-manager/` |
| `api-manager/4.6.0/install-and-setup/setup/kubernetes-deployment/kubernetes/am-pattern-6-all-in-one-is-as-km.md` | `https://apim.docs.wso2.com/en/latest/administer/managing-users-and-roles/managing-user-stores/working-with-properties-of-user-stores/` |
| `api-manager/4.6.0/monitoring/api-analytics/choreo-analytics/choreo-based-analytics-via-proxy.md` | `https://apim.docs.wso2.com/en/latest/monitoring/api-analytics/choreo-analytics/getting-started-guide/#step-2-register-your-environment` |
| `api-manager/4.6.0/monitoring/api-analytics/moesif-analytics/moesif-integration-guide.md` | `https://apim.docs.wso2.com/` |
| `api-manager/4.6.0/tutorials/deploying-apis-to-federated-gateways-with-wso2.md` | `https://apim.docs.wso2.com/en/latest/tutorials/single-control-plane-for-multiple-gateways/#setting-up-the-api-control-plane-and-universal-gateway` |
| `api-manager/4.6.0/tutorials/deploying-apis-to-federated-gateways-with-wso2.md` | `https://apim.docs.wso2.com/en/latest/administer/key-managers/configure-auth0-connector/` |
| `api-manager/4.6.0/tutorials/single-control-plane-for-multiple-gateways.md` | `https://apim.docs.wso2.com/en/latest/install-and-setup/setup/setting-up-databases/changing-default-databases/changing-to-mysql/` |
| `api-manager/4.6.0/tutorials/single-control-plane-for-multiple-gateways.md` | `https://apim.docs.wso2.com/en/latest/manage-apis/design/create-api/create-rest-api/create-a-rest-api-from-an-openapi-definition/` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/install-and-setup/install/installing-the-product/running-the-si/#starting-the-si-server` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/develop/streaming-apps/creating-a-siddhi-application/` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/develop/streaming-apps/creating-a-siddhi-application/` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/develop/streaming-apps/working-with-the-async-api-view/` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/assets/img/streaming/working-with-async-api/async-api-websocket-deploy-to-server.png` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/develop/streaming-apps/deploying-streaming-applications` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/assets/img/integrate/tutorials/service-catalog/open-service-catalog.png` |
| `api-manager/4.6.0/use-cases/streaming-usecase/exposing-stream-as-managed-api-in-service-catalog.md` | `https://apim.docs.wso2.com/en/4.3.0/get-started/streaming-quick-start-guide/` |

## `anchor` — Missing anchor

The page resolves but the `#fragment` matches no heading, so the reader lands at the top instead of the section. Usually the heading was reworded. Open the target, find the heading that was meant, and use its current slug.

| Page | Link | Target file | Missing anchor |
|---|---|---|---|
| `api-manager/4.6.0/administer/governance/governance-concept.md` | `#Artifact` | `api-manager/4.6.0/administer/governance/governance-concept.md` | `Artifact` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-stores/configuring-the-authorization-manager.md` | `#ConfiguringtheAuthorizationManager-Step1:Settinguptherepository` | `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-stores/configuring-the-authorization-manager.md` | `ConfiguringtheAuthorizationManager-Step1:Settinguptherepository` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-stores/configuring-the-authorization-manager.md` | `#ConfiguringtheAuthorizationManager-Step2:Updatingtheuserrealmconfigurations` | `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-stores/configuring-the-authorization-manager.md` | `ConfiguringtheAuthorizationManager-Step2:Updatingtheuserrealmconfigurations` |
| `api-manager/4.6.0/administer/multiple-gateways/configure-gateway.md` | `../../../install-and-setup/install/installing-the-product/running-the-api-m/#starting-the-server` | `api-manager/4.6.0/install-and-setup/install/installing-the-product/running-the-api-m.md` | `starting-the-server` |
| `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `#step-1---enable-the-community-links-option` | `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `step-1---enable-the-community-links-option` |
| `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `#step-2---verify-the-changes` | `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `step-2---verify-the-changes` |
| `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `#step-1---define-your-github-and-slack-channel-urls` | `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `step-1---define-your-github-and-slack-channel-urls` |
| `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `#step-2---verify-the-changes-1` | `api-manager/4.6.0/api-design-manage/design/api-collaborations/enable-social-media-interaction.md` | `step-2---verify-the-changes-1` |
| `api-manager/4.6.0/api-design-manage/design/api-documentation/add-api-documentation.md` | `#add-in-line-documentation` | `api-manager/4.6.0/api-design-manage/design/api-documentation/add-api-documentation.md` | `add-in-line-documentation` |
| `api-manager/4.6.0/api-design-manage/design/api-documentation/add-api-documentation.md` | `#add-documentation-using-a-url` | `api-manager/4.6.0/api-design-manage/design/api-documentation/add-api-documentation.md` | `add-documentation-using-a-url` |
| `api-manager/4.6.0/api-design-manage/design/api-documentation/add-api-documentation.md` | `#add-documentation-using-a-file` | `api-manager/4.6.0/api-design-manage/design/api-documentation/add-api-documentation.md` | `add-documentation-using-a-file` |
| `api-manager/4.6.0/api-design-manage/design/api-policies/create-policy.md` | `../../../../install-and-setup/setup/deployment-best-practices/security-guidelines-for-production-deployment/#restrict-access-java` | `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/security-guidelines-for-production-deployment.md` | `restrict-access-java` |
| `api-manager/4.6.0/api-design-manage/design/api-policies/create-policy.md` | `../../../../install-and-setup/setup/deployment-best-practices/security-guidelines-for-production-deployment/#restrict-access-java` | `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/security-guidelines-for-production-deployment.md` | `restrict-access-java` |
| `api-manager/4.6.0/api-developer-portal/collaboration/interact-with-the-community.md` | `#rate-an-API` | `api-manager/4.6.0/api-developer-portal/collaboration/interact-with-the-community.md` | `rate-an-API` |
| `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `#jwt-generation-configuration-details` | `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `jwt-generation-configuration-details` |
| `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `#sample-jwt` | `api-manager/4.6.0/api-gateway/passing-enduser-attributes-to-the-backend-via-api-gateway.md` | `sample-jwt` |
| `api-manager/4.6.0/api-security/design-time/configuring-api-security-audit.md` | `#auditreports` | `api-manager/4.6.0/api-security/design-time/configuring-api-security-audit.md` | `auditreports` |
| `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-keycloak-connector.md` | `#step12` | `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-keycloak-connector.md` | `step12` |
| `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-okta-connector.md` | `#section3` | `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-okta-connector.md` | `section3` |
| `api-manager/4.6.0/api-security/key-management/tokens/securing-oauth-token-with-hmac-validation.md` | `#SecuringOAuthTokenwithHMACValidation-Preventingmiss-useofOAuthTokens` | `api-manager/4.6.0/api-security/key-management/tokens/securing-oauth-token-with-hmac-validation.md` | `SecuringOAuthTokenwithHMACValidation-Preventingmiss-useofOAuthTokens` |
| `api-manager/4.6.0/api-security/key-management/tokens/securing-oauth-token-with-hmac-validation.md` | `#SecuringOAuthTokenwithHMACValidation-WSO2ISExtension-OAuthTokenGeneratorExtension` | `api-manager/4.6.0/api-security/key-management/tokens/securing-oauth-token-with-hmac-validation.md` | `SecuringOAuthTokenwithHMACValidation-WSO2ISExtension-OAuthTokenGeneratorExtension` |
| `api-manager/4.6.0/api-security/key-management/tokens/securing-oauth-token-with-hmac-validation.md` | `#SecuringOAuthTokenwithHMACValidation-WSO2APIManagerextension-HMACandtimestampverificationhandler` | `api-manager/4.6.0/api-security/key-management/tokens/securing-oauth-token-with-hmac-validation.md` | `SecuringOAuthTokenwithHMACValidation-WSO2APIManagerextension-HMACandtimestampverificationhandler` |
| `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `#conn-app-key-constraint` | `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `conn-app-key-constraint` |
| `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `#asynchronous-token-persistence-recovery-flow` | `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `asynchronous-token-persistence-recovery-flow` |
| `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `#synchronous-token-persistence-recovery-flow` | `api-manager/4.6.0/api-security/key-management/tokens/token-persistence.md` | `synchronous-token-persistence-recovery-flow` |
| `api-manager/4.6.0/api-security/runtime/authorization/role-based-access-control-using-xacml.md` | `../../../reference/customize-product/extending-api-manager/saml2-sso/configuring-identity-server-as-idp-for-sso.md#sharing-the-user-store` | `api-manager/4.6.0/reference/customize-product/extending-api-manager/saml2-sso/configuring-identity-server-as-idp-for-sso.md` | `sharing-the-user-store` |
| `api-manager/4.6.0/api-security/runtime/opa-validation/overview.md` | `#custom-opa-policy-with-custom-request-generator` | `api-manager/4.6.0/api-security/runtime/opa-validation/overview.md` | `custom-opa-policy-with-custom-request-generator` |
| `api-manager/4.6.0/api-security/runtime/opa-validation/overview.md` | `#custom-opa-policy-with-custom-request-generator` | `api-manager/4.6.0/api-security/runtime/opa-validation/overview.md` | `custom-opa-policy-with-custom-request-generator` |
| `api-manager/4.6.0/apiops/cli/advanced-topics/configuring-environment-specific-parameters.md` | `#handling-the-certificates-using-the-params-file` | `api-manager/4.6.0/apiops/cli/advanced-topics/configuring-environment-specific-parameters.md` | `handling-the-certificates-using-the-params-file` |
| `api-manager/4.6.0/apiops/cli/advanced-topics/configuring-environment-specific-parameters.md` | `#handling-the-certificates-using-the-params-file` | `api-manager/4.6.0/apiops/cli/advanced-topics/configuring-environment-specific-parameters.md` | `handling-the-certificates-using-the-params-file` |
| `api-manager/4.6.0/get-started/choosing-your-deployment-strategy.md` | `../get-started/deployment-platforms.md#on-premises--virtual-machines-vms` | `api-manager/4.6.0/get-started/deployment-platforms.md` | `on-premises--virtual-machines-vms` |
| `api-manager/4.6.0/get-started/choosing-your-deployment-strategy.md` | `../get-started/deployment-platforms.md#on-premises--virtual-machines-vms` | `api-manager/4.6.0/get-started/deployment-platforms.md` | `on-premises--virtual-machines-vms` |
| `api-manager/4.6.0/get-started/choosing-your-deployment-strategy.md` | `../get-started/deployment-platforms.md#on-premises--virtual-machines-vms` | `api-manager/4.6.0/get-started/deployment-platforms.md` | `on-premises--virtual-machines-vms` |
| `api-manager/4.6.0/get-started/choosing-your-deployment-strategy.md` | `../get-started/deployment-platforms.md#on-premises--virtual-machines-vms` | `api-manager/4.6.0/get-started/deployment-platforms.md` | `on-premises--virtual-machines-vms` |
| `api-manager/4.6.0/get-started/choosing-your-deployment-strategy.md` | `../get-started/deployment-platforms.md#on-premises--virtual-machines-vms` | `api-manager/4.6.0/get-started/deployment-platforms.md` | `on-premises--virtual-machines-vms` |
| `api-manager/4.6.0/get-started/choosing-your-deployment-strategy.md` | `../get-started/deployment-patterns.md#pattern-4-fully-distributed-deployment` | `api-manager/4.6.0/get-started/deployment-patterns.md` | `pattern-4-fully-distributed-deployment` |
| `api-manager/4.6.0/install-and-setup/setup/configure-userstores/configure-primary-user-store/configuring-a-read-only-ldap-user-store.md` | `#admin_ConfiguringaRead-OnlyLDAPUserStore-Updatingthesystemadministrator` | `api-manager/4.6.0/install-and-setup/setup/configure-userstores/configure-primary-user-store/configuring-a-read-only-ldap-user-store.md` | `admin_ConfiguringaRead-OnlyLDAPUserStore-Updatingthesystemadministrator` |
| `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/production-deployment-guidelines.md` | `#cb1-1` | `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/production-deployment-guidelines.md` | `cb1-1` |
| `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/tuning-performance.md` | `#configuring-wso2-api-m-to-perform-regular-cleaning` | `api-manager/4.6.0/install-and-setup/setup/deployment-best-practices/tuning-performance.md` | `configuring-wso2-api-m-to-perform-regular-cleaning` |
| `api-manager/4.6.0/install-and-setup/setup/distributed-deployment/configuring-wso2-identity-server-as-a-key-manager.md` | `#Linux-Mac` | `api-manager/4.6.0/install-and-setup/setup/distributed-deployment/configuring-wso2-identity-server-as-a-key-manager.md` | `Linux-Mac` |

_…and 73 more. Full list in the JSON sidecar._

## `gone` — No target anywhere

No file of this name exists anywhere under the docs root, so there is nothing to point at. Each needs a decision: was the page meant to be migrated and missed, was it deliberately dropped (then the link and its sentence should go), or was it merged into another page (then link there)? **Do not guess these.**

| Page | Broken target | Note |
|---|---|---|
| `api-manager/4.6.0/administer/admin-overview.md` | `../administer/key-managers/overview` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../getting-started/overview/#api-gateway` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../getting-started/overview/#api-publisher` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/administer/managing-users-and-roles/managing-user-roles.md` | `../../getting-started/overview/#developer-portal` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/administer/rate-limiting/manage-subscription-policies.md` | `../../manage-apis/design/rate-limiting/graphql-api/query-complexity-limitation/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/administer/rate-limiting/manage-subscription-policies.md` | `../../manage-apis/design/rate-limiting/graphql-api/query-depth-limitation/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/ai-gateway/ai-vendor-management/custom-ai-vendors/custom-connector.md` | `../../../assets/attachments/administer/llm.provider.connector.zip` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/ai-gateway/getting-started-with-ai-gateway.md` | `../mcp/overview/` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/block-subscription-to-an-api.md` | `../../../api-design-manage/design/rate-limiting/access-control/#denying-requests` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/block-subscription-to-an-api.md` | `../../../getting-started/overview/#api-gateway` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/block-subscription-to-an-api.md` | `../../../getting-started/overview/#api-gateway` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/block-subscription-to-an-api.md` | `../../../getting-started/overview/#api-gateway` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/control-api-visibility-and-subscription-availability-in-developer-portal.md` | `../../../develop/product-apis/restful-apis/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/control-api-visibility-and-subscription-availability-in-developer-portal.md` | `../../../develop/product-apis/restful-apis/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/advanced-topics/enable-publisher-access-control-in-api-publisher-portal.md` | `../../../reference/product-apis/restful-apis/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/api-versioning/create-a-new-api-version.md` | `../../../manage-apis/design/rate-limiting/introducing-throttling-use-cases/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-a-graphql-api.md` | `../../../api-design-manage/design/rate-limiting/graphql-api/overview-query-limits-for-graphql/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-ai-api/create-an-ai-api.md` | `../../../../ai-gateway/overview/` | `17 files share this name — too ambiguous to propose one` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-an-api-using-a-service.md` | `../../../api-design-manage/design/rate-limiting/introducing-throttling-use-cases/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-an-api-using-a-service.md` | `../../../api-design-manage/design/rate-limiting/rate-limiting-for-streaming-apis/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-rest-api/create-a-rest-api-from-an-openapi-definition.md` | `../../../../manage-apis/design/rate-limiting/introducing-throttling-use-cases/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-rest-api/create-a-rest-api-from-an-openapi-definition.md` | `../../../../assets/attachments/design/sample-archive.zip` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-rest-api/create-a-rest-api.md` | `../../../../manage-apis/design/rate-limiting/introducing-throttling-use-cases/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/create-api/create-rest-api/expose-a-soap-service-as-a-rest-api.md` | `../../../../manage-apis/design/rate-limiting/setting-throttling-limits/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/endpoints/resiliency/endpoint-timeouts.md` | `../../../../reference/synapse-properties/endpoint-properties` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-design-manage/design/prototype-api/create-mocked-js-api.md` | `../../../manage-apis/design/rate-limiting/introducing-throttling-use-cases/` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-developer-portal/consume-api-overview.md` | `../manage-apis/design/rate-limiting/introducing-throttling-use-cases` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-developer-portal/manage-application/create-application.md` | `../../consume/manage-application/create-application/#create-a-new-application` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/federated-gateways/configure-custom-gateway-agent.md` | `../../assets/attachments/deploy-and-publish/custom.gw.client.zip` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/policies/adding-dynamic-endpoints.md` | `../../learn/api-gateway/message-mediation/changing-the-default-mediation-flow-of-api-requests#creating-and-uploading-manually-in-api-publisher` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/policies/removing-specific-request-headers-from-response.md` | `../../api-gateway/message-mediation/changing-the-default-mediation-flow-of-api-requests` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/policies/transforming-api-message-payload.md` | `../../integrate/examples/json_examples/json-examples/#accessing-content-from-json-payloads` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/policies/transforming-api-message-payload.md` | `../../integrate/examples/json_examples/json-examples/#logging-json-payloads` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/policies/transforming-api-message-payload.md` | `../../integrate/examples/json_examples/json-examples/#constructing-and-transforming-json-payloads` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-gateway/policies/transforming-api-message-payload.md` | `../../integrate/examples/json_examples/json-examples/#troubleshooting-debugging-and-logging` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-security/design-time/configuring-api-security-audit.md` | `auditreports` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-security/key-management/authentication/grant-types/kerberos-oauth2-grant.md` | `../../../../assets/attachments/kerberos-grant-1.0.0.jar` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-security/key-management/authentication/grant-types/saml-extension-grant.md` | `../../../../assets/attachments/learn/saml2-assertion-creator.zip` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-custom-connector.md` | `../../../assets/attachments/administer/custom.auth.client.zip` | `no file of this name exists anywhere under the docs root` |
| `api-manager/4.6.0/api-security/key-management/third-party-key-managers/configure-wso2is-connector.md` | `../../../assets/attachments/administer/wso2is-extensions-1.7.17.zip` | `no file of this name exists anywhere under the docs root` |

_…and 78 more. Full list in the JSON sidecar._

---

## Prompt for an AI coding agent

Paste the block below to an agent working in the repo root. It is deliberately scoped to the four groups with a defensible mechanical answer. `templated`, `stale`, `anchor` and `gone` need judgement and are left out on purpose.

Alternatively, run `fix_links.py --tier <group>` yourself — same scope, one group at a time, and every rewrite verified against the files on disk before it is written.

````text
You are fixing broken links in the WSO2 API Platform docs, scope: api-manager/4.6.0.

Read the fix plan in `BROKEN-LINKS-4.6.0.md` and the machine-readable list in `BROKEN-LINKS-4.6.0.json`.

Apply ONLY these groups:
  - `templated_fixable`: apply every row as given.
  - `malformed`: apply every row exactly as given.
  - `dir_style`: apply every row exactly as given (adds `.md`).
  - `depth`: apply every row exactly as given.
  - `renamed`, the high-confidence subsection only: apply every row as given.

Rules:
  1. Replace only the link target inside the parentheses. Never change the link TEXT,
     the surrounding sentence, or anything else on the line.
  2. A target may appear more than once in a file — replace every occurrence of that
     exact target in that file.
  3. Preserve any `#fragment` already on the link unless the plan says otherwise.
  4. Do NOT touch `templated`, `stale`, `anchor` or `gone`. Do not invent a
     target that is not in the plan.
  5. Do not reformat, reflow, or reorder anything. Minimal diffs only.

Verify when done, from the repo root:
  python3 .claude/skills/wso2-doc-frontmatter/scripts/check_links.py en/docs --json /tmp/after.json

The blocking count must go DOWN and no new codes may appear. If any count rises, stop
and report what you changed rather than continuing.

Then report: rows applied per group, files touched, and the before/after blocking counts.
````

### Why `templated`, `stale`, `anchor` and `gone` are excluded

Each needs information that isn't in the repo: which new page replaces an old-site link, which reworded heading was meant, whether a missing page was dropped on purpose. An agent asked to fix those will produce plausible links to the wrong places, which is worse than a visibly broken link because nobody re-checks it.

Template-variable links are excluded for a different reason: they are not broken at all in their original context. They depend on a build-time substitution, and whether that survives migration is a redirect-strategy decision, not a link fix.
