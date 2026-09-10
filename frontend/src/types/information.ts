export type InformationState = "FULL_FILE" | "THIN_FILE" | "NO_FILE" | "DATA_POOR" | "UNKNOWN";

export type InformationDepth = "IDENTITY" | "FULL" | "EXTENDED" | "UNKNOWN";

export type DataQualityStatus = "COMPLETE" | "PARTIAL" | "INCOMPLETE" | "UNKNOWN";

export interface InformationItem {
  key: string;
  label: string;
  value: string | number | null;
  quality: DataQualityStatus;
}

export interface InformationGap {
  item: string;
  type: "missing" | "stale" | "unavailable";
  depth: InformationDepth;
}

export interface InformationProfileEntry {
  depth: InformationDepth;
  state: InformationState;
  score: number;
  version: number;
  updated_at: string;
}

export interface InformationProfile {
  profile: InformationProfileEntry;
  gaps: InformationGap[];
  items: InformationItem[];
}

export interface InformationProfileCardData {
  state: InformationState;
  score: number;
  version: number;
  depths: Record<InformationDepth, boolean>;
  gaps: InformationGap[];
  updated_at?: string;
}
