import { Card } from "@/components/ui/Card";
import { Timeline } from "@/components/ui/Timeline";
import type { TimelineItemData } from "@/components/ui/Timeline";

interface AuditTimelineProps {
  items: TimelineItemData[];
  title?: string;
}

export function AuditTimeline({ items, title = "Audit" }: AuditTimelineProps) {
  return (
    <Card title={title}>
      <Timeline items={items} />
    </Card>
  );
}
