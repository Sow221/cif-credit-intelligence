import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "@/hooks/useAuth";
import { Avatar } from "@/components/ui/Avatar";
import { Dropdown } from "@/components/ui/Dropdown";

export function UserDropdown() {
  const { t } = useTranslation();
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <Dropdown
      ariaLabel="Profil utilisateur"
      align="right"
      trigger={<Avatar name={user.full_name} size="md" />}
      items={[
        {
          label: `${user.full_name} — ${t(`common:roles.${user.role}`)}`,
          onSelect: () => navigate("/admin"),
        },
        {
          label: t("common:actions.logout"),
          danger: true,
          onSelect: signOut,
        },
      ]}
    />
  );
}
