import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { informationStateBadge } from "@/utils/constants";
import type { InformationProfileCardData } from "@/types/information";

interface InformationProfileCardProps {
  profile: InformationProfileCardData;
}

const depthLabels = ["IDENTITY", "FULL", "EXTENDED", "UNKNOWN"] as const;

export function InformationProfileCard({ profile }: InformationProfileCardProps) {
  const { t } = useTranslation();

  return (
    <Card title={t("applications:sections.informationProfile")}>
      <div className="flex items-center justify-between">
        <Badge variant={informationStateBadge(profile.state)}>
          {t(`common:informationState.${profile.state}`)}
        </Badge>
        <span className="text-label text-primary-500">
          v{profile.version}
          {typeof profile.score === "number" ? ` · ${profile.score.toFixed(0)}` : ""}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {depthLabels.map((depth) => (
          <div key={depth} className="flex items-center justify-between gap-2">
            <span className="text-label text-primary-500">{depth}</span>
            <ProgressBar value={profile.depths[depth] ? 100 : 0} className="w-24" />
          </div>
        ))}
      </div>
      {profile.updated_at ? (
        <p className="mt-3 text-label text-primary-500">{profile.updated_at}</p>
      ) : null}
    </Card>
  );
}
