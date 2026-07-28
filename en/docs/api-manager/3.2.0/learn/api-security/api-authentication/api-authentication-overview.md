# Overview

API authentication is a way of protecting API access from unidentified or anonymous access. It ensures that the API is secured and accessible only by the consumers who prove their identity and whose identities are found within the API Management Platform. 

WSO2 API Manager offers the following authentication mechanisms to secure your API from unauthenticated access.

- [Securing APIs using OAuth2 Access Tokens](../../../learn/api-security/api-authentication/secure-apis-using-oauth2-tokens)

    - [JWT (Self Contained) Access Tokens](../../../learn/api-security/oauth2/access-token-types/jwt-tokens)
    
- [Secure APIs Using API Keys](../../../learn/api-security/api-authentication/secure-apis-using-api-keys)

- [Secure APIs Using Mutual SSL](../../../learn/api-security/api-authentication/secure-apis-using-mutual-ssl)

- [Secure APIs Using Basic Authentication](../../../learn/api-security/api-authentication/secure-apis-using-basic-authentication)


WSO2 API Manager allows you to enable multiple Key Managers for authentication.

- The tenant admin can configure preferred Key Managers via the Admin Portal console. For more information, see
[Configuring Key Managers](../../../administer/key-managers/overview).

- The enabled Key Managers can be disabled for a given API via the Publisher by navigating to
**Runtime Configurations -> Application Level Security -> Key Managers**

    [![Disable Key Managers](../../../assets/img/learn/multiple-km-publisher.png)](../../../assets/img/learn/multiple-km-publisher.png)

- Application users can generate keys for an application using a preferred Key Manager as shown below.

    ![Disable Key Managers](../../../assets/img/learn/multiple-km-devportal.png)
