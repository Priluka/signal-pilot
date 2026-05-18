/** Minimal toast system — top-right stack of self-dismissing notifications.
 *
 * Usage:
 *   const toast = useToast()
 *   toast.success('Suggestion submitted')
 *   toast.error('Save failed')
 */
import { createContext, useCallback, useContext, useState } from 'react';


type ToastTone = 'success' | 'error';

interface Toast {
  id: number;
  message: string;
  tone: ToastTone;
}

interface ToastApi {
  success: (message: string) => void;
  error: (message: string) => void;
}

const ToastContext = createContext<ToastApi>({
  success: () => {},
  error: () => {},
});


export function useToast(): ToastApi {
  return useContext(ToastContext);
}


export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback((message: string, tone: ToastTone) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, tone }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  }, []);

  const api: ToastApi = {
    success: (m) => push(m, 'success'),
    error: (m) => push(m, 'error'),
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto px-3 py-2 text-sm rounded-lg border shadow-sm bg-white max-w-sm ${
              t.tone === 'success'
                ? 'border-emerald-200 text-emerald-800'
                : 'border-red-200 text-red-800'
            }`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
