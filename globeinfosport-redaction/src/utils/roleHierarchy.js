export const HIERARCHIE = { REDACTEUR: 1, EDITEUR_EN_CHEF: 2, ADMINISTRATEUR: 3 };
export const roleOf = (user) => user?.role_code ?? user?.role_redaction?.nomRole;
export const can = (user, role) => (HIERARCHIE[roleOf(user)] ?? 0) >= HIERARCHIE[role];
