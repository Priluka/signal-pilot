/** Word-level diff renderer (green for additions, red strikethrough for removals). */
import { diffWords } from 'diff';


export function DiffView({
  original,
  edited,
}: {
  original: string;
  edited: string;
}) {
  const parts = diffWords(original, edited);
  return (
    <div className="text-sm text-ink-body leading-relaxed whitespace-pre-wrap font-sans">
      {parts.map((part, i) => {
        if (part.added) {
          return (
            <span
              key={i}
              className="bg-emerald-100 text-emerald-900 rounded px-0.5"
            >
              {part.value}
            </span>
          );
        }
        if (part.removed) {
          return (
            <span
              key={i}
              className="bg-red-100 text-red-900 line-through rounded px-0.5"
            >
              {part.value}
            </span>
          );
        }
        return <span key={i}>{part.value}</span>;
      })}
    </div>
  );
}
