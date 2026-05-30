import { useEffect, useState } from "react";
import { ExternalLink, Archive } from "lucide-react";

interface IntegrityPanelProps {
  reviewQueue: any[];
  onViewEvidence?: (item: any) => void;
}

interface IntegrityMetrics {
  integrity_score: number;
  replay_confidence: number;
  evidence_density: number;
  lineage_depth: number;
  contradiction_pressure: number;
  total_workflows: number;
}

function useIntegrityMetrics() {
  const [metrics, setMetrics] = useState<IntegrityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/system/integrity-metrics")
      .then((r) => r.json())
      .then((data) => {
        if (data.integrity_score !== undefined) setMetrics(data);
      })
      .catch((err) => console.error("Integrity metrics fetch failed:", err))
      .finally(() => setLoading(false));
  }, []);

  return { metrics, loading };
}

function getHighestSeverity(queue: any[]): string {
  const levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  let max = -1;
  for (const item of queue) {
    const idx = levels.indexOf(item.risk_level?.toUpperCase() || "LOW");
    if (idx > max) max = idx;
  }
  return max >= 0 ? levels[max] : "LOW";
}

function getSeverityColor(severity: string) {
  switch (severity.toUpperCase()) {
    case "CRITICAL": return "text-red-400 border-red-400/30 bg-red-400/5";
    case "HIGH":     return "text-orange-400 border-orange-400/30 bg-orange-400/5";
    case "MEDIUM":   return "text-yellow-400 border-yellow-400/30 bg-yellow-400/5";
    default:         return "text-zinc-400 border-zinc-400/30 bg-zinc-400/5";
  }
}

function getNextAction(severity: string): string {
  switch (severity.toUpperCase()) {
    case "CRITICAL": return "Approve override or escalate to executive";
    case "HIGH":     return "Review contradiction and collect supporting evidence";
    case "MEDIUM":   return "Collect additional evidence for verification";
    default:         return "Monitor and verify incoming signals";
  }
}

function useFreezeTimer(queue: any[]) {
  const [elapsed, setElapsed] = useState("");
  useEffect(() => {
    if (queue.length === 0) { setElapsed(""); return; }
    const earliest = queue.reduce((min, item) => {
      const t = item.created_at ? new Date(item.created_at).getTime() : Date.now();
      return t < min ? t : min;
    }, Date.now());
    const update = () => {
      const diff = Math.floor((Date.now() - earliest) / 1000);
      const h = Math.floor(diff / 3600);
      const m = Math.floor((diff % 3600) / 60);
      const s = diff % 60;
      if (h > 0) setElapsed(`${h}h ${m}m ${s}s`);
      else if (m > 0) setElapsed(`${m}m ${s}s`);
      else setElapsed(`${s}s`);
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, [queue]);
  return elapsed;
}

function computeGovernanceHealth(
  queue: any[],
  severity: string,
  metrics: IntegrityMetrics
): number {
  let score = 100;
  const severityPenalty: Record<string, number> = {
    CRITICAL: 25, HIGH: 15, MEDIUM: 8, LOW: 3,
  };
  if (queue.length > 0) {
    score -= severityPenalty[severity.toUpperCase()] ?? 5;
    score -= Math.min(queue.length * 3, 20);
  }
  score -= Math.min(metrics.contradiction_pressure * 2, 10);
  return Math.max(0, Math.min(100, Math.round(score)));
}

function HealthBar({ score }: { score: number }) {
  const filled = Math.round(score / 10);
  const empty = 10 - filled;
  const color =
    score >= 80 ? "text-emerald-400" :
    score >= 60 ? "text-yellow-400" :
    score >= 40 ? "text-orange-400" : "text-red-400";
  return (
    <div className="flex items-center gap-3">
      <span className={`text-[11px] font-mono ${color}`}>
        {"█".repeat(filled)}{"░".repeat(empty)}
      </span>
      <span className={`text-sm font-light ${color}`}>{score}/100</span>
    </div>
  );
}

function MetricValue({ value, suffix = "" }: { value: number | undefined; suffix?: string }) {
  if (value === undefined) {
    return <div className="text-4xl font-light text-zinc-700 animate-pulse">—</div>;
  }
  return <div className="text-4xl font-light text-zinc-300">{value}{suffix}</div>;
}

function formatTimestamp(ts: string | undefined): string {
  if (!ts) return "—";
  try {
    return new Date(ts).toISOString().replace("T", " ").substring(0, 16) + " UTC";
  } catch {
    return ts;
  }
}

function extractDomain(url: string | undefined): string {
  if (!url) return "—";
  try {
    return new URL(url).hostname.replace("www.", "");
  } catch {
    return url;
  }
}

function EvidenceAnchor({ anchor, label }: { anchor: any; label: string }) {
  const url = anchor?.source_url || anchor?.url;
  const domain = extractDomain(url);
  const capturedAt = formatTimestamp(anchor?.capture_timestamp || anchor?.created_at);
  const confidence = anchor?.confidence !== undefined
    ? `${Math.round(anchor.confidence * 100)}%`
    : anchor?.confidence_score
    ? `${anchor.confidence_score}%`
    : null;
  const snapshotId = anchor?.snapshot_id || anchor?.id;
  const archiveUrl = anchor?.archive_url;

  return (
    <div className="bg-zinc-900/60 border border-zinc-800/60 rounded p-2 space-y-1">
      <div className="text-[8px] font-mono text-zinc-500 uppercase tracking-widest">{label}</div>
      {domain !== "—" && (
        <div className="flex items-center gap-1.5">
        <img
          src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`}
          alt=""
          className="w-3 h-3 opacity-70"
          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
        />
        <span className="text-[9px] font-mono text-zinc-300">{domain}</span>
      </div>
      )}
      {snapshotId && (
        <div className="text-[8px] font-mono text-zinc-600">
          Snapshot: {typeof snapshotId === "string" ? snapshotId.substring(0, 12) : snapshotId}
        </div>
      )}
      <div className="text-[8px] font-mono text-zinc-600">Captured: {capturedAt}</div>
      {confidence && (
        <div className="text-[8px] font-mono text-zinc-600">Confidence: {confidence}</div>
      )}
      <div className="flex gap-3 mt-1.5">
        {url && url !== "#" && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-[8px] font-mono text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            <ExternalLink className="w-2.5 h-2.5" /> View Live Source
          </a>
        )}
        {archiveUrl && (
          <a
            href={archiveUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-[8px] font-mono text-zinc-500 hover:text-zinc-200 transition-colors"
          >
            <Archive className="w-2.5 h-2.5" /> View Archived Snapshot
          </a>
        )}
      </div>
    </div>
  );
}

function ConflictDetail({ item, onViewEvidence }: { item: any; onViewEvidence?: (item: any) => void }) {
  const anchors: any[] = item.evidence_anchors || [];

  return (
    <div className="mt-2 ml-4 space-y-2">
      {anchors.length >= 1 && (
        <EvidenceAnchor anchor={anchors[0]} label="Source A" />
      )}
      {anchors.length >= 2 && (
        <EvidenceAnchor anchor={anchors[1]} label="Source B" />
      )}
      {anchors.length === 0 && (
        <div className="text-[8px] font-mono text-zinc-700">
          {item.review_reason || "No evidence anchors available"}
        </div>
      )}
      {/* Trace ID */}
      {item.id && (
        <div className="text-[8px] font-mono text-zinc-700">
          Trace: {String(item.id).substring(0, 16)}
        </div>
      )}
      {/* View Evidence button */}
      {onViewEvidence && (
        <button
          onClick={() => onViewEvidence(item)}
          className="text-[8px] font-mono text-zinc-600 hover:text-zinc-200 underline underline-offset-2 transition-colors"
        >
          View Evidence →
        </button>
      )}
    </div>
  );
}

export function IntegrityPanel({ reviewQueue, onViewEvidence }: IntegrityPanelProps) {
  const { metrics, loading } = useIntegrityMetrics();
  const severity = getHighestSeverity(reviewQueue);
  const severityColor = getSeverityColor(severity);
  const nextAction = getNextAction(severity);
  const freezeTimer = useFreezeTimer(reviewQueue);
  const totalWorkflows = metrics?.total_workflows ?? 0;
  const frozenPct = reviewQueue.length > 0 && totalWorkflows > 0
    ? Math.round((reviewQueue.length / totalWorkflows) * 100)
    : 0;
  const governanceHealth = metrics
    ? computeGovernanceHealth(reviewQueue, severity, metrics)
    : null;

  const affectedSectors = [...new Set(
    reviewQueue.map(i => i.brief_data?.sector || i.sector).filter(Boolean)
  )];
  const affectedCompanies = [...new Set(
    reviewQueue.map(i => i.brief_data?.company || i.company).filter(Boolean)
  )];

  const isFrozen = reviewQueue.length > 0;

  return (
    <div className="flex-1 overflow-y-auto mt-4 px-8">
      <h2 className="text-xs font-mono text-zinc-500 uppercase tracking-[0.2em] mb-12 border-b border-zinc-800/50 pb-4">
        Institutional Trust Observability
      </h2>

      <div className="flex gap-24">
        {/* Platform Guarantees */}
        <div className="w-80 border-r border-zinc-800/30 pr-16 shrink-0">
          <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-12">
            Platform Guarantees
          </h3>
          <div className="space-y-6">
            {[
              "Replay Integrity",
              "Governance Enforcement",
              "Simulation Isolation",
              "Graceful Degradation",
              "Evidence-Constrained Cognition",
            ].map((g) => (
              <div key={g} className="flex items-start gap-6 text-[10px] font-mono text-zinc-400">
                <span className="text-zinc-700 mt-0.5">--</span> {g}
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 grid grid-cols-3 gap-y-24 gap-x-12">

          {/* Integrity Score */}
          <div className="flex flex-col items-start">
            <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Integrity Score</h3>
            <MetricValue value={metrics?.integrity_score} />
            <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Weighted Degradation</div>
            <div className="text-[7px] font-mono text-zinc-700 mt-1">
              40% Replay · 30% Evidence · 20% Lineage · 10% Consistency
            </div>
          </div>

          {/* Replay Confidence */}
          <div className="flex flex-col items-start">
            <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Replay Confidence</h3>
            <MetricValue value={metrics?.replay_confidence} suffix="%" />
            <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Deterministic Rate</div>
          </div>

          {/* Contradiction Pressure */}
          <div className="flex flex-col items-start">
            <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Contradiction Pressure</h3>
            <MetricValue value={metrics?.contradiction_pressure} />
            <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Instability Index</div>
          </div>

          {/* Lineage Depth */}
          <div className="flex flex-col items-start border-t border-zinc-800/30 pt-12">
            <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Avg Lineage Depth</h3>
            <MetricValue value={metrics?.lineage_depth} />
            <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Snapshot Generations</div>
          </div>

          {/* Evidence Density */}
          <div className="flex flex-col items-start border-t border-zinc-800/30 pt-12">
            <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase mb-3">Evidence Density</h3>
            <MetricValue value={metrics?.evidence_density} />
            <div className="text-[9px] font-mono text-zinc-600 mt-3 tracking-widest uppercase">Anchors Per Synthesis</div>
          </div>

          {/* Empty cell */}
          <div className="border-t border-zinc-800/30 pt-12" />

          {/* ── GOVERNANCE STATE PANEL ── */}
          <div className="flex flex-col items-start border-t border-zinc-800/30 pt-12 col-span-3">
            <div className="flex items-start justify-between w-full mb-6">
              <h3 className="text-[9px] font-mono text-zinc-600 tracking-[0.2em] uppercase">
                Governance State
              </h3>
              <div className="flex flex-col items-end gap-1">
                <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest">
                  Governance Health
                </div>
                {governanceHealth !== null ? (
                  <HealthBar score={governanceHealth} />
                ) : (
                  <div className="text-[9px] font-mono text-zinc-700 animate-pulse">Loading...</div>
                )}
              </div>
            </div>

            {loading ? (
              <div className="text-[9px] font-mono text-zinc-700 uppercase tracking-widest animate-pulse">
                Connecting to integrity mesh...
              </div>
            ) : isFrozen ? (
              <div className="w-full space-y-6">

                {/* Status + Severity */}
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-[10px] font-mono font-bold text-red-400 tracking-widest uppercase px-2 py-1 border border-red-400/30 bg-red-400/5">
                    GOVERNANCE_FROZEN
                  </span>
                  <span className={`text-[10px] font-mono font-bold tracking-widest uppercase px-2 py-1 border ${severityColor}`}>
                    Severity: {severity}
                  </span>
                </div>

                {/* Impact row */}
                <div className="grid grid-cols-3 gap-8">
                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Governance Impact</div>
                    <div className="text-2xl font-light text-zinc-300">
                      {reviewQueue.length} / {totalWorkflows || "—"}
                    </div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">
                      Workflows frozen{totalWorkflows > 0 ? ` · ${frozenPct}%` : ""}
                    </div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Freeze Duration</div>
                    <div className="text-2xl font-light text-zinc-300">{freezeTimer}</div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">
                      Since first contradiction
                    </div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Affected Context</div>
                    {affectedSectors.length > 0 && (
                      <div className="text-[10px] font-mono text-zinc-400">
                        Sector: {affectedSectors.join(", ")}
                      </div>
                    )}
                    {affectedCompanies.length > 0 && (
                      <div className="text-[10px] font-mono text-zinc-500 mt-1">
                        {affectedCompanies.join(", ")}
                      </div>
                    )}
                    {affectedSectors.length === 0 && affectedCompanies.length === 0 && (
                      <div className="text-[10px] font-mono text-zinc-600">—</div>
                    )}
                  </div>
                </div>

                {/* Reasons list with full evidence anchors */}
                <div>
                  <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-2">Reasons</div>
                  <div className="space-y-4">
                    {reviewQueue.slice(0, 4).map((item: any, i: number) => (
                      <div key={i} className="text-[9px] font-mono text-zinc-500">
                        <div className="flex items-start gap-3">
                          <span className="text-red-400/50 mt-0.5">*</span>
                          <span className="flex-1">
                            {item.review_reason || "Conflicting signal detected"}
                          </span>
                          {item.risk_level && (
                            <span className={`uppercase tracking-widest text-[8px] px-1 py-0.5 border ${getSeverityColor(item.risk_level.toUpperCase())}`}>
                              {item.risk_level}
                            </span>
                          )}
                        </div>
                        <ConflictDetail item={item} onViewEvidence={onViewEvidence} />
                      </div>
                    ))}
                    {reviewQueue.length > 4 && (
                      <div className="text-[9px] font-mono text-zinc-700 pl-4">
                        +{reviewQueue.length - 4} more
                      </div>
                    )}
                  </div>
                </div>

                {/* Next action */}
                <div className="border-t border-zinc-800/30 pt-4">
                  <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Next Action</div>
                  <div className="text-[10px] font-mono text-zinc-400">{nextAction}</div>
                </div>

              </div>
            ) : (
              /* ── STABLE STATE ── */
              <div className="w-full space-y-6">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono font-bold text-emerald-400 tracking-widest uppercase px-2 py-1 border border-emerald-400/30 bg-emerald-400/5">
                    GOVERNANCE_STABLE
                  </span>
                  <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest">
                    All workflows executing normally
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-8">
                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Last Governance Review</div>
                    <div className="text-lg font-light text-zinc-300">—</div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">No recent freeze</div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Replay Confidence</div>
                    <div className="text-lg font-light text-zinc-300">
                      {metrics?.replay_confidence ?? "—"}%
                    </div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">Deterministic Rate</div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Evidence Coverage</div>
                    <div className="text-lg font-light text-zinc-300">
                      {metrics?.evidence_density ?? "—"} anchors
                    </div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">Per Synthesis</div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Contradiction Pressure</div>
                    <div className="text-lg font-light text-zinc-300">
                      {metrics?.contradiction_pressure ?? "—"}
                    </div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">Instability Index</div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Last Contradiction Resolved</div>
                    <div className="text-lg font-light text-zinc-300">—</div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">No history this session</div>
                  </div>

                  <div>
                    <div className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Active Workflows</div>
                    <div className="text-lg font-light text-zinc-300">{totalWorkflows || "—"}</div>
                    <div className="text-[9px] font-mono text-zinc-600 mt-1 uppercase tracking-widest">All unblocked</div>
                  </div>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
