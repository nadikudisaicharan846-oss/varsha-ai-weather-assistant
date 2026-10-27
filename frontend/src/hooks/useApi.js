import { useCallback, useEffect, useRef, useState } from "react";

/** Runs `fn` on mount and whenever `deps` change; ignores out-of-order responses. */
export function useApi(fn, deps, { enabled = true } = {}) {
  const [state, setState] = useState({ data: null, loading: enabled, error: null });
  const latest = useRef(0);
  const run = useCallback(async () => {
    const id = ++latest.current;
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await fn();
      if (id === latest.current) setState({ data, loading: false, error: null });
    } catch (e) {
      if (id === latest.current) setState((s) => ({ ...s, loading: false, error: e.message }));
    }
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (enabled) run(); }, [run, enabled]);
  return { ...state, reload: run };
}
