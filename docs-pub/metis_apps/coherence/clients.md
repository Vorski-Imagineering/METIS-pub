# Client spaces

A **Client** is a client's own space inside a tenant. It holds that client's events and asks, and the team who work on them.

## How it fits together

- **Keep the organisation where it is.** A client's organisation stays one record outside the tenant, and the Client links to it. An organisation that works with several tenants then has one record and a space in each.
- **The team works on what is beneath the Client.** Someone on a Client's team, on a step that carries team rights such as **Active**, can open and edit that client's events. Coherence's own pages also need access to Coherence. Who may create a new event is a separate rule. See [Permissions](../../core/PERMISSIONS.md) for both.
- **Events a tenant runs for itself** stay directly under the tenant.

## Create a Client

You need to be on the tenant's team at its **Admin** step, or a global editor.

1. The tenant's page has no button for this yet. Take the number from the end of its address, `/app/metis/holon/<number>/`, and open `/holon/<number>/events/add/` on the same site.
2. Choose **Client** if the form offers a choice, and give it the client's name. The **Journey** is already chosen for you: **Tenant clients**, at its first step, **Prospect**.
3. Click **Create Event**. That is the button's label on this form, whatever you are creating.
4. For your records, when the engagement starts, open the new Client's configuration (the gear) and move **Relationship to** the tenant on to **Active**. This grants nothing.

## Link its organisation

1. Open the Client's page and find **Related Organisations**.
2. Add the organisation, on the **Client → organisation** journey.

It then shows under Related Organisations on the Client's page.
