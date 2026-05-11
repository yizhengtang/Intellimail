//provider.ts
//Defines Provider — the union of all connected communication platforms in this application.
//This is a cross-cutting type used by the frontend UI, backend routers, and ChromaDB metadata.
//It is NOT an email-specific concept and must not live in types/email.ts.

export type Provider = 'gmail' | 'outlook' | 'teams';
