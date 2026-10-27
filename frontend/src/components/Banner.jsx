const STYLES = {
  error: "border-red-400 bg-red-50 text-red-950 dark:bg-red-950/50 dark:text-red-100",
  warning: "border-amber-400 bg-amber-50 text-amber-950 dark:bg-amber-950/50 dark:text-amber-100",
  info: "border-sky-400 bg-sky-50 text-sky-950 dark:bg-sky-950/50 dark:text-sky-100",
};

export default function Banner({ kind = "error", title, children, action }) {
  return (
    <div role={kind === "error" ? "alert" : "status"} className={`flex flex-wrap items-center justify-between gap-2 rounded-xl border px-4 py-3 ${STYLES[kind]}`}>
      <div>
        {title && <p className="font-semibold">{title}</p>}
        <p className="text-sm">{children}</p>
      </div>
      {action}
    </div>
  );
}
