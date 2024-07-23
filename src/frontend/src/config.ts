export const crmEndpoint = "api/crm";
export const protocol = import.meta.env.VITE_PROTOCOL;
export const backendDomain = import.meta.env.VITE_DOMAIN;
export const backendPort = import.meta.env.VITE_PORT;
export const fullBackendURL = `${protocol}://${backendDomain}:${backendPort}`;
