/** Placeholder page for sidebar links whose backend pieces aren't wired up yet. */
export function ComingSoonPage({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="max-w-3xl mx-auto px-8 py-16 text-center">
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200 rounded">
          Coming soon
        </span>
        <h1 className="mt-4 text-2xl font-semibold tracking-tight text-ink">
          {title}
        </h1>
        {description && (
          <p className="mt-2 text-sm text-ink-muted max-w-lg mx-auto">{description}</p>
        )}
      </div>
    </div>
  );
}
