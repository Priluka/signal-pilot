/** Force-directed knowledge graph of the playbook corpus.
 *
 * Nodes are playbooks colored by ``ticket_class`` and sized by
 * ``cluster_size``. Edges are deduped ``related_playbooks`` cross-references.
 * Hover surfaces title + confidence; click navigates to the playbook viewer.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import type { ForceGraphMethods } from 'react-force-graph-2d';
import { useNavigate } from 'react-router-dom';

import { getGraph } from '../lib/api';
import { reliabilityTier, ticketClassLabel } from '../lib/labels';
import type { GraphNode } from '../lib/types';


const TICKET_CLASS_COLORS: Record<string, string> = {
  end_user: '#3b82f6',          // blue
  b2b_partner: '#10b981',       // green
  internal_partner: '#f59e0b',  // amber
};
const FALLBACK_COLOR = '#94a3b8'; // slate-400


// react-force-graph expects nodes with x/y/fx/fy fields it can mutate.
type RenderNode = GraphNode & {
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number;
  fy?: number;
};

type RenderLink = {
  source: string | RenderNode;
  target: string | RenderNode;
};


function colorFor(ticket_class: string): string {
  return TICKET_CLASS_COLORS[ticket_class] ?? FALLBACK_COLOR;
}


/** Map cluster_size to a draw radius. Sqrt-scale so very large clusters don't dominate. */
function radiusFor(cluster_size: number | null): number {
  const base = 4;
  const size = cluster_size ?? 1;
  return base + Math.sqrt(Math.max(size, 1)) * 0.8;
}


export function GraphPage() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<ForceGraphMethods<RenderNode, RenderLink> | undefined>(undefined);

  const [graph, setGraph] = useState<{ nodes: RenderNode[]; links: RenderLink[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hovered, setHovered] = useState<RenderNode | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [classFilter, setClassFilter] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getGraph()
      .then((data) => {
        if (cancelled) return;
        setGraph({
          nodes: data.nodes.map((n) => ({ ...n })),
          links: data.edges.map((e) => ({ source: e.source, target: e.target })),
        });
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Observe container size so the canvas fills the available area.
  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    const update = () => setSize({ width: el.clientWidth, height: el.clientHeight });
    update();
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Recenter the simulation when the data first lands.
  useEffect(() => {
    if (graph && fgRef.current) {
      // Defer one frame so the simulation has positions to fit.
      setTimeout(() => fgRef.current?.zoomToFit(400, 60), 100);
    }
  }, [graph]);

  const filteredGraph = useMemo(() => {
    if (!graph) return null;
    if (!classFilter) return graph;
    const keep = new Set(
      graph.nodes.filter((n) => n.ticket_class === classFilter).map((n) => n.id),
    );
    return {
      nodes: graph.nodes.filter((n) => keep.has(n.id)),
      links: graph.links.filter((l) => {
        const s = typeof l.source === 'string' ? l.source : l.source.id;
        const t = typeof l.target === 'string' ? l.target : l.target.id;
        return keep.has(s) && keep.has(t);
      }),
    };
  }, [graph, classFilter]);

  const handleNodeClick = useCallback(
    (n: RenderNode) => navigate(`/knowledge/${n.id}`),
    [navigate],
  );

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-ink">
            Knowledge Graph
          </h1>
          <p className="text-[11px] text-ink-muted mt-0.5">
            {graph
              ? `${filteredGraph?.nodes.length ?? graph.nodes.length} playbooks · ${
                  filteredGraph?.links.length ?? graph.links.length
                } related-playbook links`
              : 'Loading the corpus…'}
          </p>
        </div>
        <Legend onFilter={setClassFilter} active={classFilter} />
      </header>
      <div ref={containerRef} className="relative flex-1 overflow-hidden bg-hover">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center text-sm text-ink-muted">
            Loading graph…
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center text-sm text-red-600">
            {error}
          </div>
        )}
        {filteredGraph && size.width > 0 && (
          <ForceGraph2D
            ref={fgRef}
            graphData={filteredGraph}
            width={size.width}
            height={size.height}
            backgroundColor="#f7f8fa"
            nodeRelSize={1}
            nodeVal={(n) => {
              const node = n as RenderNode;
              return Math.pow(radiusFor(node.cluster_size), 2);
            }}
            nodeColor={(n) => colorFor((n as RenderNode).ticket_class)}
            nodeLabel={() => ''}
            onNodeHover={(n) => setHovered((n as RenderNode) ?? null)}
            onNodeClick={(n) => handleNodeClick(n as RenderNode)}
            linkColor={() => 'rgba(148, 163, 184, 0.35)'}
            linkWidth={0.7}
            d3AlphaDecay={0.025}
            d3VelocityDecay={0.35}
            cooldownTime={4000}
            warmupTicks={60}
            enableNodeDrag={true}
          />
        )}
        {hovered && <NodeTooltip node={hovered} />}
      </div>
    </div>
  );
}


function Legend({
  onFilter,
  active,
}: {
  onFilter: (value: string | null) => void;
  active: string | null;
}) {
  return (
    <div className="flex items-center gap-2">
      {Object.entries(TICKET_CLASS_COLORS).map(([cls, color]) => (
        <button
          key={cls}
          type="button"
          onClick={() => onFilter(active === cls ? null : cls)}
          className={`inline-flex items-center gap-1.5 px-2 py-1 text-[11px] border rounded transition-colors ${
            active === cls
              ? 'bg-hover border-line text-ink'
              : active === null
              ? 'bg-card border-line text-ink-body hover:bg-hover'
              : 'bg-card border-line text-ink-muted hover:bg-hover'
          }`}
        >
          <span
            className="inline-block w-2.5 h-2.5 rounded-full"
            style={{ background: color }}
          />
          {cls}
        </button>
      ))}
      {active && (
        <button
          type="button"
          onClick={() => onFilter(null)}
          className="text-[11px] text-accent hover:text-accent"
        >
          Clear
        </button>
      )}
    </div>
  );
}


function NodeTooltip({ node }: { node: RenderNode }) {
  return (
    <div className="absolute pointer-events-none top-4 left-4 max-w-sm bg-card border border-panel-border rounded-md shadow-sm p-3">
      <div className="text-sm font-medium text-ink leading-snug">
        {node.title}
      </div>
      <div className="mt-1 text-[11px] font-mono text-ink-muted">{node.id}</div>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px]">
        <span
          className="inline-flex items-center gap-1 px-1.5 py-0.5 border rounded bg-hover text-ink-body"
          style={{ borderColor: colorFor(node.ticket_class) }}
        >
          <span
            className="inline-block w-1.5 h-1.5 rounded-full"
            style={{ background: colorFor(node.ticket_class) }}
          />
          {ticketClassLabel(node.ticket_class)}
        </span>
        <span className="text-ink-muted">{node.issue_category}</span>
      </div>
      {(() => {
        const rel = reliabilityTier(node.extraction_confidence);
        return (
          <div className="mt-2 grid grid-cols-3 gap-3 text-[11px]">
            <div>
              <div className="uppercase tracking-wider text-ink-muted font-semibold text-[10px]">
                Tickets
              </div>
              <div className="text-ink-body font-mono">{node.cluster_size ?? '—'}</div>
            </div>
            <div>
              <div className="uppercase tracking-wider text-ink-muted font-semibold text-[10px]">
                Reliability
              </div>
              <div className="text-ink-body">
                {rel != null ? `${rel.tier} (${rel.percent}%)` : '—'}
              </div>
            </div>
            <div>
              <div className="uppercase tracking-wider text-ink-muted font-semibold text-[10px]">
                Links
              </div>
              <div className="text-ink-body font-mono">{node.degree}</div>
            </div>
          </div>
        );
      })()}
      <div className="mt-2 text-[10px] text-ink-muted">Click to open playbook</div>
    </div>
  );
}
