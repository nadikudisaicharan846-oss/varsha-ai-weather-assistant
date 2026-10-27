export default function LoadingSkeleton({ rows = 3 }) {
  return (
    <div className="space-y-3" aria-busy="true">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="card h-24 animate-pulse opacity-60" />
      ))}
    </div>
  );
}
