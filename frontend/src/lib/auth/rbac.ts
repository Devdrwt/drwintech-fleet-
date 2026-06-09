// RBAC côté front (miroir des rôles backend — voir SECURITY.md).
// Le contrôle réel reste backend ; ceci ne fait que l'affichage.

export const ROLE_LEVELS: Record<string, number> = {
  superadmin: 4,
  admin: 3,
  superviseur: 2,
  technicien: 2,
  comptable: 2,
  support: 2,
  client: 1,
};

export const MODULE_MIN_LEVEL: Record<string, number> = {
  dashboard: 1,
  carte: 2,
  clients: 2,
  materiel: 2,
  paiements: 2,
  maintenance: 2,
  reporting: 2,
  notifications: 2,
  audit: 3,
  utilisateurs: 3,
  parametres: 4,
};

export function canAccessModule(roleCode: string, moduleId: string): boolean {
  const level = ROLE_LEVELS[roleCode] ?? 0;
  const required = MODULE_MIN_LEVEL[moduleId] ?? 1;
  return level >= required;
}
